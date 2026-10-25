#!/usr/bin/env bash
# InstaBox deploy agent for tj-core-01 — Tianji stable channel (prerelease)
# plus development-branch preview channels (TJ-027.1 evolution).
#
# EVOLUTION NOTE: this file is the additive evolution of the original
# stable-only agent, not a replacement. The stable path (deploy_tianji,
# offline_accept, sealed build, health + bazi gates, rollback, retention,
# flock, disk guard, fail-closed preflights) is unchanged except for two
# mechanical additions: the JSON log gains a "port" field, and the stable
# channel gains a main-only guard (see deploy_tianji). Everything
# preview-related is new code (deploy_preview and helpers) that never
# touches the stable env file, state files, or compose project.
#
# Pull-model: watches the public channel branch head. Release gate is the
# TRUSTED-MACHINE OFFLINE ACCEPTANCE (public repo scripts/accept_offline.py
# --suite all) run locally against the exact public SHA, the controlled
# knowledge snapshot under $BASE/secure, and the independently recorded
# trusted manifest SHA256 ($CICD/env/trusted-acceptance). No GitHub
# accepted-* tags and no private-repo Actions are used or required.
# After acceptance passes, the sealed API image is built locally (never
# pushed) with its recorded PIN, the web image is pulled from GHCR (local
# build fallback), the stack switches via the private repo's own compose,
# gates on health + a real bazi business probe run, and any gate failure
# auto-rolls back. Every attempt is logged as JSON to the evidence
# deploys.log. FAIL-CLOSED: missing private clone, public clone, snapshot
# or trusted-manifest record => log BLOCKED/ACCEPTANCE_FAILED, touch
# nothing.
#
# Preview channels (new): one operator-managed file per branch,
# $CICD/channels/tianji-preview-<slug>.branch, whose content is the branch
# name. Each preview is a web-only container on its own loopback port in
# its own compose project (tianji-preview-<slug>), attached to the stable
# network so /api/ proxies to the ALREADY-ACCEPTED stable sealed backend.
# Previews NEVER build a sealed API image, so the sealed-acceptance gate
# cannot be bypassed through a preview. A preview's health gate is: GHCR
# image pull + web /health (rag_ready:true via the stable backend) +
# frontend 200 + docker inspect image match. Failure rolls back to that
# preview's previous healthy web image only; stable is never touched.
# Capacity: at most MAX_PREVIEWS previews (default 5); beyond that, new
# previews are refused, never evicting an existing preview.
# Recovery: the systemd timer re-runs this agent; every channel
# reconciles only when its head SHA differs from recorded state, so a
# post-resume run is idempotent and deploys exactly the changed channels.
#
# All paths below are operator environment overrides; defaults match the
# tj-core-01 machine layout and are operator configuration, not secrets.
# This script contains no secrets and no private knowledge.
set -uo pipefail

BASE=${BASE:-/data/workspace/platform-deploy}
PRIV=${PRIV:-$BASE/projects/tianji-private-knowledge}
PUB=${PUB:-$BASE/projects/tianji-knowledge-base}
SNAP=${SNAP:-$BASE/secure/tianji-knowledge}
CICD=${CICD:-$BASE/cicd}
STATE=${STATE:-$CICD/state}
EVID=${EVID:-$BASE/deployment-evidence/tj-core-01}
LOG=${LOG:-$EVID/deploys.log}
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PREVIEW_COMPOSE=${PREVIEW_COMPOSE:-$SCRIPT_DIR/deploy-preview-compose.yml}
API_DB_OVERRIDE=${API_DB_OVERRIDE:-$CICD/deploy-api-db-override.yml}
PREVIEW_PORT_START=${PREVIEW_PORT_START:-8101}
MAX_PREVIEWS=${MAX_PREVIEWS:-5}
TIANJI_PREVIEW_NETWORK=${TIANJI_PREVIEW_NETWORK:-tianji_tianji-private-net}
mkdir -p "$STATE" "$CICD/env" "$CICD/build" "$CICD/channels" "$EVID"
exec 9>"$CICD/agent-tj.lock"
flock -n 9 || exit 0
touch "$CICD/DEPLOYING-TJ"; trap 'rm -f "$CICD/DEPLOYING-TJ"' EXIT

jlog() {
  python3 - "$@" <<'PYEOF'
import json,sys,datetime
keys=["project","channel","branch","sha","image","port","result","detail"]
d=dict(zip(keys,sys.argv[1:9])); d["ts"]=datetime.datetime.now().astimezone().isoformat()
print(json.dumps(d,ensure_ascii=False))
PYEOF
}
log() { local line; line=$(jlog "$@"); echo "$line" >> "$LOG"; echo "$line"; }

# Disk guard: docker data lives on the root fs on this machine; build
# dirs live on /data. Both need headroom before a build starts.
ensure_disk_tj() {
  local free_root free_data
  free_root=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
  if [ "${free_root:-0}" -lt 5 ]; then docker builder prune -af --keep-storage 256MB >/dev/null 2>&1; docker image prune -f >/dev/null 2>&1; fi
  free_root=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
  free_data=$(df -BG --output=avail /data | tail -1 | tr -dc 0-9)
  [ "${free_root:-0}" -ge 4 ] && [ "${free_data:-0}" -ge 2 ]
}
prune_after_build() { docker builder prune -f --keep-storage 512MB >/dev/null 2>&1 || true; }
# Audit-DB override (TJ-027.1 wiring for TJ-026.5): the sealed api runs
# read-only as user 10001 with no volumes in the private compose, and its
# audit DB default path is relative (resolves to read-only /opt/tianji), so
# a fresh sealed image crashes at startup (fail-fast, by design). The
# override pins the DB to a host bind mount the operator prepares once
# (mkdir + chown 10001:10001; see PREVIEW_DEPLOY_AGENT.md). It is generated
# here, not shipped as a separate template, so it exists before EVERY stable
# up call, deploy or rollback; a write failure aborts loudly instead of
# running up without the mount.
ensure_api_db_override() {
  cat > "$API_DB_OVERRIDE" <<'EOF'
services:
  tianji-api:
    environment:
      - TIANJI_ADMIN_DB_PATH=/var/lib/tianji/tianji_admin.db
    volumes:
      - /data/workspace/platform-deploy/data/tianji-admin:/var/lib/tianji:rw
EOF
  [ -s "$API_DB_OVERRIDE" ]
}
gh_head() { git ls-remote "https://github.com/HelloMrDuan/$1.git" "refs/heads/$2" 2>/dev/null | cut -f1; }

ACCEPT_RAN=0
offline_accept() { # $1 = exact public sha. Runs the full offline suite at
  # most once per SHA (success cached as evidence JSON; failure throttled
  # to one run per 30 min). Returns 0 only on a verified SUCCESS evidence
  # whose public_sha and knowledge_manifest_sha256 match this SHA and the
  # independently recorded trusted manifest SHA256.
  local sha=$1 tsha ev out fmark
  tsha=$(grep -oE '[0-9a-f]{64}' "$CICD/env/trusted-acceptance" 2>/dev/null | head -1)
  [ -n "$tsha" ] || return 1
  ev="$EVID/acceptance-$sha.json"
  if [ -f "$ev" ] && python3 - "$ev" "$sha" "$tsha" <<'PYEOF'
import json,sys
try:
  d=json.load(open(sys.argv[1]))
except Exception:
  sys.exit(1)
ok = (d.get("result")=="SUCCESS" and d.get("mode")=="offline-controlled"
      and d.get("public_sha")==sys.argv[2]
      and d.get("knowledge_manifest_sha256")==sys.argv[3]
      and d.get("suite")=="all")
sys.exit(0 if ok else 1)
PYEOF
  then return 0; fi
  fmark="$STATE/accept-failed-$sha"
  if [ -f "$fmark" ] && [ $(( $(date +%s) - $(stat -c %Y "$fmark") )) -lt 1800 ]; then return 1; fi
  git -C "$PUB" fetch -q origin || return 1
  git -C "$PUB" checkout -q --detach "$sha" || return 1
  [ "$(git -C "$PUB" rev-parse HEAD)" = "$sha" ] || return 1
  out="$CICD/build/acceptance-$sha.out"
  ACCEPT_RAN=1
  local py=python3
  [ -x "$CICD/env/accept-venv/bin/python" ] && py="$CICD/env/accept-venv/bin/python"
  ( cd "$PUB" && "$py" scripts/accept_offline.py --public-code "$PUB" \
      --expected-sha "$sha" --knowledge-snapshot "$SNAP" \
      --trusted-manifest-sha256 "$tsha" --suite all ) > "$out" 2>&1
  local rc=$?
  python3 - "$out" "$ev" <<'PYEOF'
import json,sys
txt=open(sys.argv[1],errors="replace").read()
dec=json.JSONDecoder(); best=None
for i,ch in enumerate(txt):
  if ch=="{":
    try:
      obj,_=dec.raw_decode(txt[i:])
    except Exception:
      continue
    if isinstance(obj,dict) and obj.get("result")=="SUCCESS": best=obj
if best is None: sys.exit(1)
json.dump(best,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
PYEOF
  if [ "$rc" -eq 0 ] && [ -f "$ev" ] && python3 - "$ev" "$sha" "$tsha" <<'PYEOF'
import json,sys
try:
  d=json.load(open(sys.argv[1]))
except Exception:
  sys.exit(1)
ok = (d.get("result")=="SUCCESS"
      and d.get("mode")=="offline-controlled"
      and d.get("public_sha")==sys.argv[2]
      and d.get("knowledge_manifest_sha256")==sys.argv[3]
      and d.get("suite")=="all")
sys.exit(0 if ok else 1)
PYEOF
  then
    rm -f "$fmark"
    return 0
  fi
  rm -f "$ev"
  touch "$fmark"
  return 1
}

deploy_tianji() { # channel branch port envfile projargs
  local channel=$1 br=$2 port=$3 envf=$4 proj=$5
  local sha cur api_img web_img used_web prev_api prev_web ok i pin
  # Stable-channel protection (hard rule, TJ-027.1 preview evolution):
  # the prerelease channel IS the stable service on port 8080. It accepts
  # main only. Any attempt to point it at another branch is refused and
  # logged (once per day, like the other operator markers); the running
  # service is untouched. Preview branches must use deploy_preview below,
  # never this path.
  if [ "$channel" = "prerelease" ] && [ "$br" != "main" ]; then
    local rmarker="$STATE/tianji-prerelease-refused-$(date +%F)"
    [ -f "$rmarker" ] || { touch "$rmarker"; log tianji "$channel" "$br" "" "" "$port" REFUSED "stable channel accepts main only; branch $br refused; running service untouched"; }
    return 0
  fi
  if [ -f "$CICD/channels/tianji-$channel.paused" ]; then
    local marker="$STATE/tianji-$channel-paused-$(date +%F)"
    [ -f "$marker" ] || { touch "$marker"; log tianji "$channel" "$br" "" "" "$port" PAUSED "channel paused by operator; running service untouched"; }
    return 0
  fi
  # Preflight: without the private clone (read-only deploy key), neither
  # the sealed build nor its knowledge source can run. Fail closed.
  if [ ! -d "$PRIV/.git" ]; then
    local bmarker="$STATE/tianji-blocked-clone-$(date +%F)"
    [ -f "$bmarker" ] || { touch "$bmarker"; log tianji "$channel" "$br" "" "" "$port" BLOCKED "private repo clone missing on tj-core-01 (no .git at $PRIV); add the read-only deploy key and clone to activate auto-deploy; running service untouched"; }
    return 0
  fi
  # Preflight: offline acceptance prerequisites (public clone, controlled
  # knowledge snapshot, independently recorded trusted manifest SHA256).
  if [ ! -d "$PUB/.git" ] || [ ! -d "$SNAP" ] || [ ! -s "$CICD/env/trusted-acceptance" ]; then
    local amarker="$STATE/tianji-blocked-accept-$(date +%F)"
    [ -f "$amarker" ] || { touch "$amarker"; log tianji "$channel" "$br" "" "" "$port" BLOCKED "offline acceptance prerequisites missing (public clone / knowledge snapshot / trusted manifest record); running service untouched"; }
    return 0
  fi
  sha=$(gh_head tianji-knowledge-base "$br"); [ -n "$sha" ] || { log tianji "$channel" "$br" "" "" "$port" FAILED "ls-remote failed"; return; }
  cur=$(cat "$STATE/tianji-$channel.sha" 2>/dev/null || true)
  [ "$sha" = "$cur" ] && return 0
  ACCEPT_RAN=0
  if ! offline_accept "$sha"; then
    [ "$ACCEPT_RAN" = 1 ] && log tianji "$channel" "$br" "$sha" "" "$port" ACCEPTANCE_FAILED "offline acceptance (accept_offline.py --suite all vs trusted manifest) did not pass; see cicd/build/acceptance-$sha.out; running service untouched"
    return
  fi
  log tianji "$channel" "$br" "$sha" "" "$port" ACCEPTED "offline acceptance SUCCESS (evidence: deployment-evidence/tj-core-01/acceptance-$sha.json)"
  ensure_disk_tj || { log tianji "$channel" "$br" "$sha" "" "$port" FAILED "disk guard: insufficient free space on / or /data after prune"; return; }
  api_img="tianji-api:cicd-$channel-${sha:0:8}"
  web_img="ghcr.io/hellomrduan/tianji-web:$sha"; used_web="$web_img"
  "$BASE/tianji/build-sealed-for.sh" "$sha" "$api_img" >>"$CICD/build/tianji-build.log" 2>&1 \
    || { log tianji "$channel" "$br" "$sha" "" "$port" FAILED "sealed build/verify/smoke failed"; return; }
  pin=$(grep "sealed ok sha=$sha" "$CICD/build/tianji-build.log" | tail -1 | grep -oE 'pin=[0-9a-f]{64}' | cut -d= -f2)
  [ -n "$pin" ] || { log tianji "$channel" "$br" "$sha" "" "$port" FAILED "sealed build did not report a PIN"; return; }
  if ! docker pull "$web_img" >/dev/null 2>&1; then
    log tianji "$channel" "$br" "$sha" "$web_img" "$port" WAITING_IMAGE "GHCR image unavailable; running service untouched"
    return 0
  fi
  prune_after_build
  prev_api=$(cat "$STATE/tianji-$channel.api-image" 2>/dev/null || echo tianji-api:sealed-82b119e)
  prev_web=$(cat "$STATE/tianji-$channel.web-image" 2>/dev/null || echo tianji-web:static-82b119e)
  printf "TIANJI_PRIVATE_API_IMAGE=%s\nTIANJI_PUBLIC_WEB_IMAGE=%s\nTIANJI_HOST_PORT=%s\n" "$api_img" "$web_img" "$port" > "$envf"; chmod 600 "$envf"
  ensure_api_db_override || { log tianji "$channel" "$br" "$sha" "$api_img" "$port" FAILED "cannot write api db override $API_DB_OVERRIDE; running service untouched"; return; }
  ( cd "$PRIV" && docker compose -f deploy/compose.yml -f "$API_DB_OVERRIDE" --env-file "$envf" $proj up -d >/dev/null 2>&1 )
  ok=0; for i in $(seq 1 40); do sleep 2
    curl -sf -m 3 "http://127.0.0.1:$port/health" 2>/dev/null | grep -q '"rag_ready":true' && { ok=1; break; }
  done
  local actual_web actual_api
  actual_web=$(docker inspect tianji-tianji-web-1 --format '{{.Config.Image}}' 2>/dev/null || true)
  actual_api=$(docker inspect tianji-tianji-api-1 --format '{{.Config.Image}}' 2>/dev/null || true)
  if [ "$ok" = 1 ] && [ "$actual_web" = "$web_img" ] && [ "$actual_api" = "$api_img" ] && curl -sf -m 10 -X POST "http://127.0.0.1:$port/api/v1/public/execute" -H 'Content-Type: application/json' \
      -d '{"domain":"bazi","input":{"year_ganzhi":"庚午","month_ganzhi":"壬午","day_ganzhi":"甲子","hour_ganzhi":"甲子"}}' 2>/dev/null | grep -q '"pillars"'; then
    echo "$sha" > "$STATE/tianji-$channel.sha"; echo "$api_img" > "$STATE/tianji-$channel.api-image"; echo "$web_img" > "$STATE/tianji-$channel.web-image"
    log tianji "$channel" "$br" "$sha" "$api_img" "$port" DEPLOYED "health+bazi ok; port $port; web=$used_web; pin=$pin"
    # Retention: keep ONLY the just-deployed pair and the previous
    # healthy pair among agent-created tags. Release tags (sealed-*/
    # static-*) and the protected rollback pair are never matched here.
    local img_ref
    for img_ref in $(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E '^tianji-api:cicd-' || true); do
      if [ "$img_ref" != "$api_img" ] && [ "$img_ref" != "$prev_api" ]; then docker rmi "$img_ref" >/dev/null 2>&1 || true; fi
    done
    for img_ref in $(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E '^ghcr\.io/hellomrduan/tianji-web:' || true); do
      if [ "$img_ref" != "$web_img" ] && [ "$img_ref" != "$prev_web" ]; then docker rmi "$img_ref" >/dev/null 2>&1 || true; fi
    done
    return
  fi
  printf "TIANJI_PRIVATE_API_IMAGE=%s\nTIANJI_PUBLIC_WEB_IMAGE=%s\nTIANJI_HOST_PORT=%s\n" "$prev_api" "$prev_web" "$port" > "$envf"; chmod 600 "$envf"
  ensure_api_db_override || { log tianji "$channel" "$br" "$sha" "$api_img" "$port" FAILED "health gate failed and rollback aborted: cannot write api db override $API_DB_OVERRIDE; running service still on failed $api_img, operator must restore $prev_api manually"; return; }
  ( cd "$PRIV" && docker compose -f deploy/compose.yml -f "$API_DB_OVERRIDE" --env-file "$envf" $proj up -d >/dev/null 2>&1 )
  log tianji "$channel" "$br" "$sha" "$api_img" "$port" FAILED_ROLLED_BACK "health/business gate failed; restored $prev_api"
}

# ---- Preview channels (TJ-027.1 evolution; additive only) ----

slugify_branch() { # $1 = branch or filename fragment -> safe slug
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -e 's/[^a-z0-9_.-]/-/g' -e 's/^[^a-z0-9_]*//' -e 's/[-._]*$//'
}

assign_preview_port() { # $1 = slug; prints the port. On first assignment
  # it records $STATE/tianji-preview-$slug.port. Returns 1 when the
  # capacity guard refuses a new preview (no port, no eviction).
  local slug=$1 existing p used f count
  existing=$(cat "$STATE/tianji-preview-$slug.port" 2>/dev/null || true)
  if [ -n "$existing" ]; then echo "$existing"; return 0; fi
  count=0
  for f in "$STATE"/tianji-preview-*.port; do [ -f "$f" ] && count=$((count+1)); done
  if [ "$count" -ge "${MAX_PREVIEWS:-5}" ]; then return 1; fi
  local start=${PREVIEW_PORT_START:-8101}
  p=$start
  while [ $((p - start)) -lt "${MAX_PREVIEWS:-5}" ]; do
    used=0
    for f in "$STATE"/tianji-preview-*.port; do
      [ -f "$f" ] || continue
      [ "$(cat "$f" 2>/dev/null)" = "$p" ] && { used=1; break; }
    done
    if [ "$used" = 0 ]; then echo "$p" > "$STATE/tianji-preview-$slug.port"; echo "$p"; return 0; fi
    p=$((p+1))
  done
  return 1
}

deploy_preview() { # $1 = slug, $2 = branch. Web-only preview: never builds
  # a sealed API image, never touches stable env/state/project.
  local slug=$1 br=$2
  local port envf proj sha cur web_img prev_web ok i actual
  # Guards: main belongs to the stable channel, and the stable channel
  # name prerelease can never be a preview. An empty/unsafe slug is
  # refused rather than guessed.
  if [ "$br" = "main" ] || [ "$slug" = "prerelease" ] || [ -z "$slug" ]; then
    log tianji "preview-$slug" "$br" "" "" "" REFUSED "preview refused: main and the stable channel name prerelease are never previews; running service untouched"
    return 0
  fi
  if [ -f "$CICD/channels/tianji-preview-$slug.paused" ]; then
    local marker="$STATE/tianji-preview-$slug-paused-$(date +%F)"
    [ -f "$marker" ] || { touch "$marker"; log tianji "preview-$slug" "$br" "" "" "" PAUSED "preview channel paused by operator; running preview untouched"; }
    return 0
  fi
  if ! port=$(assign_preview_port "$slug"); then
    local cmarker="$STATE/tianji-preview-$slug-capacity-$(date +%F)"
    [ -f "$cmarker" ] || { touch "$cmarker"; log tianji "preview-$slug" "$br" "" "" "" CAPACITY_REFUSED "preview capacity reached (MAX_PREVIEWS=${MAX_PREVIEWS:-5}); no new preview created and no existing preview evicted"; }
    return 0
  fi
  envf="$CICD/env/tianji-preview-$slug.env"
  proj="tianji-preview-$slug"
  sha=$(gh_head tianji-knowledge-base "$br"); [ -n "$sha" ] || { log tianji "preview-$slug" "$br" "" "" "$port" FAILED "ls-remote failed"; return; }
  cur=$(cat "$STATE/tianji-preview-$slug.sha" 2>/dev/null || true)
  [ "$sha" = "$cur" ] && return 0
  # Preview gate: GHCR web image only. The preview web container joins
  # the stable network, so /api/ proxies to the already-accepted stable
  # sealed backend; the backend is by construction the accepted version
  # and the sealed-acceptance gate cannot be bypassed through a preview.
  ensure_disk_tj || { log tianji "preview-$slug" "$br" "$sha" "" "$port" FAILED "disk guard: insufficient free space after prune"; return; }
  web_img="ghcr.io/hellomrduan/tianji-web:$sha"
  if ! docker pull "$web_img" >/dev/null 2>&1; then
    log tianji "preview-$slug" "$br" "$sha" "$web_img" "$port" WAITING_IMAGE "GHCR image unavailable; running preview untouched"
    return 0
  fi
  prev_web=$(cat "$STATE/tianji-preview-$slug.web-image" 2>/dev/null || true)
  printf "TIANJI_PUBLIC_WEB_IMAGE=%s\nTIANJI_HOST_PORT=%s\n" "$web_img" "$port" > "$envf"; chmod 600 "$envf"
  docker compose -p "$proj" -f "$PREVIEW_COMPOSE" --env-file "$envf" up -d >/dev/null 2>&1
  ok=0; for i in $(seq 1 40); do sleep 2
    curl -sf -m 3 "http://127.0.0.1:$port/health" 2>/dev/null | grep -q '"rag_ready":true' && { ok=1; break; }
  done
  actual=$(docker inspect "tianji-preview-$slug-tianji-web-1" --format '{{.Config.Image}}' 2>/dev/null || true)
  if [ "$ok" = 1 ] && [ "$actual" = "$web_img" ] && curl -sf -m 3 "http://127.0.0.1:$port/" >/dev/null 2>&1; then
    echo "$sha" > "$STATE/tianji-preview-$slug.sha"; echo "$web_img" > "$STATE/tianji-preview-$slug.web-image"
    log tianji "preview-$slug" "$br" "$sha" "$web_img" "$port" DEPLOYED "preview health ok (via stable sealed backend); port $port"
    # First successful deploy of this preview: publish its loopback port
    # so it gets a public URL. Best effort only: a publish failure is
    # logged and never breaks the deploy; the marker stays absent so the
    # next successful deploy retries.
    if [ ! -f "$STATE/tianji-preview-$slug.published" ]; then
      if command -v instabox-port >/dev/null 2>&1; then
        if instabox-port publish "$port" >/dev/null 2>&1; then
          touch "$STATE/tianji-preview-$slug.published"
          log tianji "preview-$slug" "$br" "$sha" "$web_img" "$port" PUBLISHED "instabox-port publish $port ok"
        else
          log tianji "preview-$slug" "$br" "$sha" "$web_img" "$port" PUBLISH_NOTE "instabox-port publish $port failed; preview still deployed on loopback; publish manually"
        fi
      else
        log tianji "preview-$slug" "$br" "$sha" "$web_img" "$port" PUBLISH_NOTE "instabox-port not found on this machine; preview deployed on loopback only"
      fi
    fi
    # Retention: keep ONLY the just-deployed and the previous healthy web
    # image for this preview. Never -f: images in use by running
    # containers (including stable) cannot be removed this way.
    local img_ref
    for img_ref in $(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E '^ghcr\.io/hellomrduan/tianji-web:' || true); do
      if [ "$img_ref" != "$web_img" ] && [ "$img_ref" != "$prev_web" ]; then docker rmi "$img_ref" >/dev/null 2>&1 || true; fi
    done
    return
  fi
  if [ -n "$prev_web" ]; then
    printf "TIANJI_PUBLIC_WEB_IMAGE=%s\nTIANJI_HOST_PORT=%s\n" "$prev_web" "$port" > "$envf"; chmod 600 "$envf"
    docker compose -p "$proj" -f "$PREVIEW_COMPOSE" --env-file "$envf" up -d >/dev/null 2>&1
    log tianji "preview-$slug" "$br" "$sha" "$web_img" "$port" FAILED_ROLLED_BACK "preview health gate failed; restored $prev_web; stable untouched"
  else
    docker compose -p "$proj" -f "$PREVIEW_COMPOSE" --env-file "$envf" down >/dev/null 2>&1
    log tianji "preview-$slug" "$br" "$sha" "$web_img" "$port" FAILED "preview health gate failed and no previous healthy preview exists; preview removed; stable untouched"
  fi
}

main() {
  local br
  br=$(cat "$CICD/channels/tianji-prerelease.branch" 2>/dev/null || echo main)
  deploy_tianji prerelease "$br" 8080 "$CICD/env/tianji-prerelease.env" ""
  # Preview channels: one operator-managed file per branch,
  # $CICD/channels/tianji-preview-<slug>.branch, whose content is the
  # branch name. Adding a file enables a preview; removing it stops
  # reconciliation (the container keeps running until removed manually).
  # Recovery after a machine resume needs nothing special: the systemd
  # timer re-runs this agent, and each channel reconciles only when its
  # head SHA differs from recorded state (idempotent).
  local bf slug pbr
  for bf in "$CICD"/channels/tianji-preview-*.branch; do
    [ -f "$bf" ] || continue
    slug=$(basename "$bf" .branch); slug=${slug#tianji-preview-}
    slug=$(slugify_branch "$slug")
    [ -n "$slug" ] || continue
    pbr=$(cat "$bf" 2>/dev/null || true)
    [ -n "$pbr" ] || continue
    deploy_preview "$slug" "$pbr"
  done
}

# Run main only when executed, not when sourced (the simulation harness
# sources this file to test deploy_preview and the guards directly).
if [ "${BASH_SOURCE[0]:-$0}" = "$0" ]; then
  main "$@"
fi
