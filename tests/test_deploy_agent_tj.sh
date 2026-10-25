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
