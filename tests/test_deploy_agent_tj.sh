#!/usr/bin/env bash
# Simulation tests for scripts/deploy-agent-tj.sh (TJ-027.1 preview evolution).
#
# SIMULATION ONLY: docker, git, curl, sleep, df and instabox-port are PATH
# stubs; no real containers, no real GHCR, no real machine. Passing here
# never counts as real-machine acceptance. Each case runs in a fresh
# subshell with a fresh fake CICD tree and sources the agent (main() does
# not run on source, by the BASH_SOURCE guard at the bottom of the agent).
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
AGENT=$ROOT/scripts/deploy-agent-tj.sh
COMPOSE=$ROOT/scripts/deploy-preview-compose.yml
PASS=0
FAIL=0
FAILED_DIRS=""

# --- syntax gate (fails the harness outright) ---
bash -n "$AGENT" || { echo "FAIL: bash -n scripts/deploy-agent-tj.sh"; exit 1; }
echo "PASS: bash -n scripts/deploy-agent-tj.sh"
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck -S warning "$AGENT" && echo "PASS: shellcheck scripts/deploy-agent-tj.sh"
else
  echo "SKIP: shellcheck not installed"
fi
if python3 -c "import yaml" >/dev/null 2>&1; then
  python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "$COMPOSE" \
    && echo "PASS: deploy-preview-compose.yml parses as YAML"
else
  echo "SKIP: python yaml not available, compose YAML not parsed"
fi

write_stubs() { # $1 = stubbin dir; $2 = case dir
  local bin=$1 case_dir=$2
  cat > "$bin/docker" <<'STUBEOF'
#!/usr/bin/env bash
echo "docker $*" >> "$CASE_DIR/docker.log"
cmd=${1:-}
case "$cmd" in
  pull)
    if [ "${DOCKER_PULL_FAIL:-0}" = "1" ]; then exit 1; fi
    echo "$2" >> "$CASE_DIR/images.txt"
    ;;
  inspect)
    name=$2
    grep "^$name " "$CASE_DIR/containers.txt" 2>/dev/null | cut -d' ' -f2 | head -1 || true
    ;;
  compose)
    args="$*"
    proj=$(printf '%s' "$args" | sed -n 's/.*-p \([^ ]*\).*/\1/p')
    # Stable path has no -p: its compose file (deploy/compose.yml) uses
    # project "tianji", matching the agent's inspect names
    # tianji-tianji-web-1 / tianji-tianji-api-1. The preview compose file
    # (deploy-preview-compose.yml) always carries -p, so no overlap.
    if [ -z "$proj" ]; then case "$args" in *deploy/compose.yml*) proj=tianji;; esac; fi
    envf=$(printf '%s' "$args" | sed -n 's/.*--env-file \([^ ]*\).*/\1/p')
    # Action is not the last word: the agent calls "up -d" / "down".
    action=""
    case "$args" in *" up "*) action=up;; *" down"*) action=down;; esac
    if [ "$action" = "up" ]; then
      img=$(grep '^TIANJI_PUBLIC_WEB_IMAGE=' "$envf" | cut -d= -f2)
      cname="${proj}-tianji-web-1"
      grep -v "^${cname} " "$CASE_DIR/containers.txt" 2>/dev/null > "$CASE_DIR/containers.tmp" || true
      mv "$CASE_DIR/containers.tmp" "$CASE_DIR/containers.txt"
      echo "$cname $img" >> "$CASE_DIR/containers.txt"
      grep -qx "$img" "$CASE_DIR/images.txt" 2>/dev/null || echo "$img" >> "$CASE_DIR/images.txt"
      # Stable env files also carry the sealed API image; record the API
      # container the same way so the agent's inspect gate is exercised.
      # Preview env files have no TIANJI_PRIVATE_API_IMAGE, so this is
      # skipped for previews.
      api_img=$(grep '^TIANJI_PRIVATE_API_IMAGE=' "$envf" 2>/dev/null | cut -d= -f2 || true)
      if [ -n "$api_img" ]; then
        aname="${proj}-tianji-api-1"
        grep -v "^${aname} " "$CASE_DIR/containers.txt" 2>/dev/null > "$CASE_DIR/containers.tmp" || true
        mv "$CASE_DIR/containers.tmp" "$CASE_DIR/containers.txt"
        echo "$aname $api_img" >> "$CASE_DIR/containers.txt"
        grep -qx "$api_img" "$CASE_DIR/images.txt" 2>/dev/null || echo "$api_img" >> "$CASE_DIR/images.txt"
      fi
    elif [ "$action" = "down" ]; then
      grep -v "^${proj}-" "$CASE_DIR/containers.txt" 2>/dev/null > "$CASE_DIR/containers.tmp" || true
      mv "$CASE_DIR/containers.tmp" "$CASE_DIR/containers.txt"
    fi
    ;;
  images)
    cat "$CASE_DIR/images.txt" 2>/dev/null || true
    ;;
  rmi)
    grep -v "^$2$" "$CASE_DIR/images.txt" 2>/dev/null > "$CASE_DIR/images.tmp" || true
    mv "$CASE_DIR/images.tmp" "$CASE_DIR/images.txt"
    ;;
  *)
    : ;;
esac
exit 0
STUBEOF
  cat > "$bin/git" <<'STUBEOF'
#!/usr/bin/env bash
echo "git $*" >> "$CASE_DIR/git.log"
if [ "${1:-}" = "ls-remote" ]; then
  if [ -n "${GIT_LSREMOTE_SHA:-}" ]; then printf '%s\t%s\n' "$GIT_LSREMOTE_SHA" "${3:-}"; fi
  exit 0
fi
exit 0
STUBEOF
  cat > "$bin/curl" <<'STUBEOF'
#!/usr/bin/env bash
url=""
for a in "$@"; do case "$a" in http*) url=$a;; esac; done
echo "curl $url" >> "$CASE_DIR/curl.log"
case "$url" in
  */health)
    if [ "${CURL_HEALTH:-ok}" = "ok" ]; then echo '{"status":"ok","rag_ready":true}'; exit 0; else exit 1; fi
    ;;
  */)
    if [ "${CURL_FRONTEND:-ok}" = "ok" ]; then exit 0; else exit 1; fi
    ;;
  *)
    exit 0 ;;
esac
STUBEOF
  cat > "$bin/sleep" <<'STUBEOF'
#!/usr/bin/env bash
exit 0
STUBEOF
  cat > "$bin/df" <<'STUBEOF'
#!/usr/bin/env bash
printf 'Avail\n100G\n'
STUBEOF
  cat > "$bin/instabox-port" <<'STUBEOF'
#!/usr/bin/env bash
echo "instabox-port $*" >> "$CASE_DIR/instabox.log"
[ "${INSTABOX_PUBLISH_FAIL:-0}" = "1" ] && exit 1
exit 0
STUBEOF
  chmod +x "$bin"/*
}

# run_case NAME FUNCTION [VAR=VAL ...]: fresh fake tree, stub PATH first,
# source the agent, run the case function under set -e (a failed assertion
# aborts the subshell, which fails the case).
run_case() {
  local name=$1 fn=$2; shift 2
  local case_dir
  case_dir=$(mktemp -d)
  mkdir -p "$case_dir/stubbin" "$case_dir/cicd/channels" "$case_dir/cicd/state" \
    "$case_dir/cicd/env" "$case_dir/evid"
  : > "$case_dir/docker.log"; : > "$case_dir/git.log"; : > "$case_dir/curl.log"
  : > "$case_dir/instabox.log"; : > "$case_dir/containers.txt"; : > "$case_dir/images.txt"
  write_stubs "$case_dir/stubbin" "$case_dir"
  if (
    export CASE_DIR="$case_dir"
    export PATH="$case_dir/stubbin:$PATH"
    export BASE="$case_dir/base" CICD="$case_dir/cicd" STATE="$case_dir/cicd/state"
    export EVID="$case_dir/evid" LOG="$case_dir/evid/deploys.log"
    export PREVIEW_COMPOSE="$COMPOSE" PREVIEW_PORT_START=8101 MAX_PREVIEWS=5
    export GIT_LSREMOTE_SHA="" CURL_HEALTH=ok CURL_FRONTEND=ok
    export DOCKER_PULL_FAIL=0 INSTABOX_PUBLISH_FAIL=0
    for kv in "$@"; do export "$kv"; done
    source "$AGENT"
    set -e
    "$fn"
  ); then
    PASS=$((PASS+1)); echo "PASS: $name"; rm -rf "$case_dir"
  else
    FAIL=$((FAIL+1)); echo "FAIL: $name (case dir kept: $case_dir)"
    FAILED_DIRS="$FAILED_DIRS $case_dir"
  fi
}

SHA40() { # $1 = char -> 40 copies (a realistic 40-hex SHA stand-in)
  printf "$1%.0s" $(seq 1 40)
}

case_stable_markers() {
  for m in offline_accept build-sealed-for.sh rag_ready FAILED_ROLLED_BACK \
    tianji-prerelease.branch accept_offline.py trusted-acceptance \
    "sealed ok sha=" "tianji-api:cicd-"; do
    grep -q "$m" "$AGENT"
  done
}

case_port_assignment() {
  p1=$(assign_preview_port alpha); [ "$p1" = "8101" ]
  p2=$(assign_preview_port beta); [ "$p2" = "8102" ]
  p3=$(assign_preview_port alpha); [ "$p3" = "8101" ]
  [ "$(cat "$STATE/tianji-preview-alpha.port")" = "8101" ]
  [ "$(cat "$STATE/tianji-preview-beta.port")" = "8102" ]
}

case_stable_refusal() {
  deploy_tianji prerelease feature-x 8080 "$CICD/env/tianji-prerelease.env" ""
  grep -q 'REFUSED' "$LOG"
  grep -q 'stable channel accepts main only' "$LOG"
  [ "$(grep -c 'REFUSED' "$LOG")" = "1" ]
  deploy_tianji prerelease feature-x 8080 "$CICD/env/tianji-prerelease.env" ""
  [ "$(grep -c 'REFUSED' "$LOG")" = "1" ]
  [ ! -f "$STATE/tianji-prerelease.sha" ]
  [ ! -s "$CASE_DIR/docker.log" ]
}

case_stable_main_passthrough() {
  deploy_tianji prerelease main 8080 "$CICD/env/tianji-prerelease.env" ""
  grep -q 'BLOCKED' "$LOG"
  ! grep -q 'REFUSED' "$LOG"
  [ ! -s "$CASE_DIR/docker.log" ]
}

case_preview_success() {
  local sha; sha=$(SHA40 a)
  deploy_preview demo demo-branch
  grep -q 'DEPLOYED' "$LOG"
  grep -q '"port": "8101"' "$LOG"
  [ "$(cat "$STATE/tianji-preview-demo.sha")" = "$sha" ]
  [ "$(cat "$STATE/tianji-preview-demo.web-image")" = "ghcr.io/hellomrduan/tianji-web:$sha" ]
  grep -q "TIANJI_PUBLIC_WEB_IMAGE=ghcr.io/hellomrduan/tianji-web:$sha" "$CICD/env/tianji-preview-demo.env"
  grep -q 'TIANJI_HOST_PORT=8101' "$CICD/env/tianji-preview-demo.env"
  grep -q 'compose -p tianji-preview-demo' "$CASE_DIR/docker.log"
  grep -q 'publish 8101' "$CASE_DIR/instabox.log"
  [ -f "$STATE/tianji-preview-demo.published" ]
}

case_preview_rollback() {
  local old new; old=$(SHA40 a); new=$(SHA40 b)
  echo "$old" > "$STATE/tianji-preview-demo.sha"
  echo "ghcr.io/hellomrduan/tianji-web:$old" > "$STATE/tianji-preview-demo.web-image"
  echo "8101" > "$STATE/tianji-preview-demo.port"
  deploy_preview demo demo-branch
  grep -q 'FAILED_ROLLED_BACK' "$LOG"
  [ "$(cat "$STATE/tianji-preview-demo.sha")" = "$old" ]
  grep -q "TIANJI_PUBLIC_WEB_IMAGE=ghcr.io/hellomrduan/tianji-web:$old" "$CICD/env/tianji-preview-demo.env"
  [ "$(grep -c 'compose -p tianji-preview-demo' "$CASE_DIR/docker.log")" = "2" ]
  [ ! -f "$STATE/tianji-prerelease.sha" ]
  ! grep -q 'tianji-prerelease' "$CASE_DIR/docker.log"
}

# TJ-005.3: stable-channel rollback. Pre-seeds the previous healthy pair,
# a cache-hit offline-acceptance evidence for the new SHA, the trusted
# manifest record, the preflight dirs, and a stub sealed build; then the
# health gate fails (CURL_HEALTH=fail) and the agent must restore the
# previous pair. This proves the rollback logic is wired; it does NOT
# prove a real-machine stable rollback (the harness header says simulation
# never counts as real-machine acceptance).
case_stable_rollback() {
  local old new tsha pin
  old=$(SHA40 a); new=$(SHA40 b)
  tsha=$(printf 'e%.0s' $(seq 1 64))
  pin=$(printf 'd%.0s' $(seq 1 64))
  # Previous healthy pair (state the agent reads for prev_api/prev_web).
  echo "$old" > "$STATE/tianji-prerelease.sha"
  echo "tianji-api:cicd-prerelease-aaaaaaaa" > "$STATE/tianji-prerelease.api-image"
  echo "ghcr.io/hellomrduan/tianji-web:$old" > "$STATE/tianji-prerelease.web-image"
  # Preflight prerequisites: private + public clones, snapshot, trusted
  # manifest record.
  mkdir -p "$BASE/projects/tianji-private-knowledge/.git" \
    "$BASE/projects/tianji-knowledge-base/.git" \
    "$BASE/secure/tianji-knowledge" "$BASE/tianji"
  printf '%s' "$tsha" > "$CICD/env/trusted-acceptance"
  # Cache-hit offline acceptance for the new SHA (no real accept run).
  cat > "$EVID/acceptance-$new.json" <<JSONEOF
{"result": "SUCCESS", "mode": "offline-controlled", "public_sha": "$new", "knowledge_manifest_sha256": "$tsha", "suite": "all"}
JSONEOF
  # Stub sealed build: reports the PIN the agent greps for.
  printf '#!/usr/bin/env bash\necho "sealed ok sha=$1 pin=%s"\n' "$pin" \
    > "$BASE/tianji/build-sealed-for.sh"
  chmod +x "$BASE/tianji/build-sealed-for.sh"
  deploy_tianji prerelease main 8080 "$CICD/env/tianji-prerelease.env" ""
  grep -q 'ACCEPTED' "$LOG"
  grep -q "sealed ok sha=$new" "$CICD/build/tianji-build.log"
  grep -q 'FAILED_ROLLED_BACK' "$LOG"
  grep -q '"channel": "prerelease"' "$LOG"
  # State still records the previous pair, never the failed new SHA.
  [ "$(cat "$STATE/tianji-prerelease.sha")" = "$old" ]
  [ "$(cat "$STATE/tianji-prerelease.api-image")" = "tianji-api:cicd-prerelease-aaaaaaaa" ]
  [ "$(cat "$STATE/tianji-prerelease.web-image")" = "ghcr.io/hellomrduan/tianji-web:$old" ]
  # Env file rewritten to the previous pair.
  grep -q "TIANJI_PRIVATE_API_IMAGE=tianji-api:cicd-prerelease-aaaaaaaa" "$CICD/env/tianji-prerelease.env"
  grep -q "TIANJI_PUBLIC_WEB_IMAGE=ghcr.io/hellomrduan/tianji-web:$old" "$CICD/env/tianji-prerelease.env"
  # Compose up ran twice (deploy attempt + rollback), both containers
  # restored to the previous pair, and no preview was touched.
  [ "$(grep -c 'compose -f deploy/compose.yml' "$CASE_DIR/docker.log")" = "2" ]
  [ "$(docker inspect tianji-tianji-web-1 --format '{{.Config.Image}}')" = "ghcr.io/hellomrduan/tianji-web:$old" ]
  [ "$(docker inspect tianji-tianji-api-1 --format '{{.Config.Image}}')" = "tianji-api:cicd-prerelease-aaaaaaaa" ]
  ! grep -q 'tianji-preview' "$CASE_DIR/docker.log"
}

case_preview_no_prev_fail() {
  deploy_preview demo demo-branch
  grep -q '"result": "FAILED"' "$LOG"
  ! grep -q 'ROLLED_BACK' "$LOG"
  grep -q 'tianji-preview-demo.*down' "$CASE_DIR/docker.log"
  [ ! -f "$STATE/tianji-preview-demo.sha" ]
}

case_capacity() {
  echo "8101" > "$STATE/tianji-preview-one.port"
  echo "8102" > "$STATE/tianji-preview-two.port"
  deploy_preview third third-branch
  grep -q 'CAPACITY_REFUSED' "$LOG"
  [ ! -f "$STATE/tianji-preview-third.port" ]
  [ ! -s "$CASE_DIR/docker.log" ]
}

case_reconcile_idempotent() {
  local sha; sha=$(SHA40 a)
  echo "$sha" > "$STATE/tianji-preview-demo.sha"
  echo "ghcr.io/hellomrduan/tianji-web:$sha" > "$STATE/tianji-preview-demo.web-image"
  echo "8101" > "$STATE/tianji-preview-demo.port"
  deploy_preview demo demo-branch
  [ ! -s "$CASE_DIR/docker.log" ]
}

case_paused() {
  touch "$CICD/channels/tianji-preview-demo.paused"
  deploy_preview demo demo-branch
  grep -q 'PAUSED' "$LOG"
  [ ! -s "$CASE_DIR/docker.log" ]
}

case_preview_main_refused() {
  deploy_preview demo main
  deploy_preview prerelease some-branch
  [ "$(grep -c 'REFUSED' "$LOG")" = "2" ]
  [ ! -s "$CASE_DIR/docker.log" ]
}

case_main_reconcile() {
  echo "demo-branch" > "$CICD/channels/tianji-preview-demo.branch"
  main
  grep -q 'DEPLOYED' "$LOG"
  grep -q 'BLOCKED' "$LOG"
  [ "$(grep -c 'compose -p tianji-preview-demo' "$CASE_DIR/docker.log")" = "1" ]
  main
  [ "$(grep -c 'compose -p tianji-preview-demo' "$CASE_DIR/docker.log")" = "1" ]
}

SHA_A=$(SHA40 a)
run_case "stable markers present" case_stable_markers
run_case "preview port assignment" case_port_assignment
run_case "stable refuses non-main branch" case_stable_refusal
run_case "stable main passes guard to preflight" case_stable_main_passthrough
run_case "preview first deploy success + publish" case_preview_success "GIT_LSREMOTE_SHA=$SHA_A"
run_case "preview health fail rolls back to previous preview" case_preview_rollback "GIT_LSREMOTE_SHA=$(SHA40 b)" "CURL_HEALTH=fail"
run_case "stable health fail rolls back to previous pair" case_stable_rollback "GIT_LSREMOTE_SHA=$(SHA40 b)" "CURL_HEALTH=fail"
run_case "preview health fail without previous removes preview" case_preview_no_prev_fail "GIT_LSREMOTE_SHA=$SHA_A" "CURL_HEALTH=fail"
run_case "preview capacity refusal" case_capacity "MAX_PREVIEWS=2" "GIT_LSREMOTE_SHA=$SHA_A"
run_case "preview reconcile idempotent" case_reconcile_idempotent "GIT_LSREMOTE_SHA=$SHA_A"
run_case "paused preview untouched" case_paused "GIT_LSREMOTE_SHA=$SHA_A"
run_case "preview refuses main and stable name" case_preview_main_refused "GIT_LSREMOTE_SHA=$SHA_A"
run_case "main() reconciles stable + preview idempotently" case_main_reconcile "GIT_LSREMOTE_SHA=$SHA_A"

echo "----"
echo "simulation cases: PASS=$PASS FAIL=$FAIL"
[ "$FAILED_DIRS" = "" ] || echo "failed case dirs kept:$FAILED_DIRS"
[ "$FAIL" = "0" ]
