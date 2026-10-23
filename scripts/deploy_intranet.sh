#!/bin/bash
# TJ-027.1: controlled intranet deployment loop for the Tianji platform.
# Deploys: production frontend build (static) + API backend + /api gateway,
# then runs scripts/health_check.py. Rollback = stop all services.
# Usage: ./scripts/deploy_intranet.sh [start|stop|status|health]
# Environment:
#   TIANJI_BACKEND_DIR  assembled backend dir (default: ./backend)
#   TIANJI_API_PORT     default 8000
#   TIANJI_WEB_PORT     default 4176
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_PORT="${TIANJI_API_PORT:-8000}"
WEB_PORT="${TIANJI_WEB_PORT:-4176}"
BACKEND_DIR="${TIANJI_BACKEND_DIR:-$ROOT/backend}"
PIDDIR="/tmp/tianji-intranet"

cmd="${1:-start}"
mkdir -p "$PIDDIR"

# NOTE (honesty boundary): 127.0.0.1 loopback runs are LOCAL controlled
# acceptance only. Real intranet access requires a separately provided
# reachable address plus access-control evidence; this script never claims it.

# Port owner: which PID is listening on 127.0.0.1:$1 (empty if free)
port_owner() {
  ss -tlnp 2>/dev/null | grep -E "127.0.0.1:$1\b" | grep -oP 'pid=\K[0-9]+' | head -1
}

# Abort if the port is occupied by a process we do not own.
require_port_free() { # $1=port $2=name
  local owner
  owner="$(port_owner "$1")"
  if [ -n "$owner" ]; then
    echo "[deploy] ERROR: port $1 ($2) already occupied by pid $owner (not owned by this deployment); refusing to start"
    return 1
  fi
  return 0
}

# Verify the recorded PID is actually listening on the expected port.
verify_listening() { # $1=pidfile $2=port $3=name
  local pid owner tries
  pid="$(cat "$1" 2>/dev/null || echo "")"
  [ -n "$pid" ] || { echo "[deploy] ERROR: $3 pid file missing"; return 1; }
  for tries in 1 2 3 4 5; do
    owner="$(port_owner "$2")"
    if [ "$owner" = "$pid" ]; then
      echo "[deploy] $3 pid $pid confirmed listening on :$2"
      return 0
    fi
    sleep 2
  done
  echo "[deploy] ERROR: $3 pid $pid is NOT listening on :$2 (owner: ${owner:-none}); refusing to claim success"
  return 1
}

# Kill only PIDs we own: verify the process cmdline matches our service tag.
pid_owned() { # $1=pidfile $2=tag
  local pid tag cmdline
  pid="$(cat "$1" 2>/dev/null || echo "")"
  tag="$2"
  [ -n "$pid" ] || return 1
  cmdline="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || echo "")"
  case "$cmdline" in *"$tag"*) return 0;; *) return 1;; esac
}

start_api() {
  echo "[deploy] starting API on :$API_PORT (backend: $BACKEND_DIR)"
  [ -d "$BACKEND_DIR/src" ] || { echo "[deploy] ERROR: backend not found at $BACKEND_DIR"; exit 1; }
  require_port_free "$API_PORT" "api" || exit 1
  cd "$BACKEND_DIR"
  PYTHONPATH="$BACKEND_DIR/src:${PYTHONPATH:-}" nohup python3 -m uvicorn tianji_kb.api:app \
    --host 127.0.0.1 --port "$API_PORT" > "$PIDDIR/api.log" 2>&1 &
  apid=$!
  echo "$apid" > "$PIDDIR/api.pid"
  echo "uvicorn tianji_kb.api:app" > "$PIDDIR/api.tag"
  verify_listening "$PIDDIR/api.pid" "$API_PORT" "api" || { do_stop; exit 1; }
}
start_web() {
  echo "[deploy] building frontend"
  cd "$ROOT/web/visual-prototype"
  # Snapshot protection: never overwrite the last available version.
  # Keep timestamped snapshots; `rollback` always uses the newest one.
  if [ -d dist ]; then
    snap="$PIDDIR/dist.prev.$(date +%Y%m%d%H%M%S)"
    mv dist "$snap"
    echo "[deploy] previous build snapshotted to $snap"
    # Record SHA256 of the snapshot for rollback verification.
    ( cd "$snap" && find . -type f | sort | xargs sha256sum > "$snap.SHA256" )
    echo "[deploy] snapshot SHA256 recorded"
  fi
  require_port_free "$WEB_PORT" "gateway" || { do_stop; exit 1; }
  npm run build > "$PIDDIR/build.log" 2>&1 || { echo "[deploy] ERROR: frontend build failed"; tail -20 "$PIDDIR/build.log"; do_stop; exit 1; }
  echo "[deploy] starting static+gateway on :$WEB_PORT"
  cat > "$PIDDIR/gateway.py" << PYEOF
import http.server, os, urllib.request, urllib.error
DIST = "$ROOT/web/visual-prototype/dist"
API = "http://127.0.0.1:$API_PORT"
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=DIST, **k)
    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy()
        elif os.path.isfile(os.path.join(DIST, self.path.lstrip("/").split("?")[0])):
            super().do_GET()
        else:
            # SPA fallback: deep links (e.g. /bazi-profile) serve index.html,
            # never masquerade as an API response.
            self.path = "/index.html"
            super().do_GET()
    def do_POST(self):
        if self.path.startswith("/api/"): self._proxy()
        else: self.send_error(404)
    def _proxy(self):
        url = API + self.path
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n) if n else None
        req = urllib.request.Request(url, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length"): req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read(); self.send_response(r.status)
                self.send_header("Content-Type", r.headers.get("Content-Type", ""))
                self.send_header("Content-Length", str(len(data))); self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            self.send_response(e.code); self.end_headers()
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(("127.0.0.1", $WEB_PORT), H).serve_forever()
PYEOF
  nohup python3 "$PIDDIR/gateway.py" > "$PIDDIR/web.log" 2>&1 &
  sleep 2
  wpid="$(resolve_pid "tianji-intranet/gateway.py")"
  [ -n "$wpid" ] || { echo "[deploy] ERROR: gateway did not start"; do_stop; exit 1; }
  echo "$wpid" > "$PIDDIR/web.pid"
  echo "tianji-intranet/gateway.py" > "$PIDDIR/web.tag"
  verify_listening "$PIDDIR/web.pid" "$WEB_PORT" "gateway" || { do_stop; exit 1; }
}
do_health() {
  echo "[deploy] health check"
  HC="${TIANJI_HEALTH_CHECK:-$ROOT/scripts/health_check.py}"
  [ -f "$HC" ] || { echo "[deploy] ERROR: health_check.py not found at $HC"; exit 1; }
  python3 "$HC" \
    --api "http://127.0.0.1:$API_PORT" \
    --frontend "http://127.0.0.1:$WEB_PORT"
}
do_stop() {
  echo "[deploy] stopping services started by this script"
  for n in api web; do
    tag="$(cat "$PIDDIR/$n.tag" 2>/dev/null || echo "tianji-intranet")"
    if pid_owned "$PIDDIR/$n.pid" "$tag"; then
      kill "$(cat "$PIDDIR/$n.pid")" 2>/dev/null || true
      echo "[deploy] stopped $n (pid $(cat "$PIDDIR/$n.pid"))"
    else
      echo "[deploy] skip $n: pid not owned by this deployment (not killing)"
    fi
    rm -f "$PIDDIR/$n.pid" "$PIDDIR/$n.tag"
  done
  echo "[deploy] stopped"
}
do_rollback() {
  # FRONTEND-ONLY rollback: restores the newest snapshot, restarts the gateway,
  # then verifies (a) restored files match the snapshot SHA256 and (b) the
  # actually-served page matches. The backend API is untouched and NOT rolled back.
  snap=""
  for c in $(ls -dt "$PIDDIR"/dist.prev.* 2>/dev/null); do
    case "$c" in *.SHA256) continue;; *) [ -d "$c" ] && { snap="$c"; break; };; esac
  done
  [ -n "$snap" ] || { echo "[deploy] ERROR: no previous build snapshot to roll back to"; exit 1; }
  echo "[deploy] rolling back FRONTEND ONLY to snapshot $snap (API untouched)"
  [ -f "$snap.SHA256" ] && expected_sha="$(sha256sum "$snap.SHA256" | cut -d' ' -f1)" || expected_sha=""
  # Stop only the gateway, keep the API running.
  tag="$(cat "$PIDDIR/web.tag" 2>/dev/null || echo "tianji-intranet/gateway.py")"
  if pid_owned "$PIDDIR/web.pid" "$tag"; then kill "$(cat "$PIDDIR/web.pid")" 2>/dev/null || true; fi
  rm -f "$PIDDIR/web.pid" "$PIDDIR/web.tag"
  rm -rf "$ROOT/web/visual-prototype/dist"
  mkdir -p "$ROOT/web/visual-prototype/dist"
  cp -r "$snap/." "$ROOT/web/visual-prototype/dist/"
  start_web_nobuild
  sleep 3
  # (a) verify restored files match the snapshot
  if [ -n "$expected_sha" ]; then
    actual_sha="$(cd "$ROOT/web/visual-prototype/dist" && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1)"
    # recompute snapshot sha the same way for comparison
    snap_sha="$(cd "$snap" && find . -type f ! -name SHA256 | sort | xargs sha256sum | sha256sum | cut -d' ' -f1)"
    [ "$actual_sha" = "$snap_sha" ] || { echo "[deploy] ERROR: restored files do NOT match snapshot ($actual_sha != $snap_sha)"; exit 1; }
    echo "[deploy] restored files match snapshot SHA256"
  fi
  # (b) verify the actually-served page matches the restored build
  served="$(curl -s -m 10 "http://127.0.0.1:$WEB_PORT/")"
  restored_index="$(cat "$ROOT/web/visual-prototype/dist/index.html")"
  [ "$served" = "$restored_index" ] || { echo "[deploy] ERROR: served page does not match restored build"; exit 1; }
  echo "[deploy] served page matches restored build"
  do_health && echo "[deploy] FRONTEND rollback verified: previous version serving (backend not rolled back)"
}
resolve_pid() { # $1=pattern -> prints PID or empty
  for p in /proc/[0-9]*; do
    pid="${p#/proc/}"
    if tr '\0' ' ' < "$p/cmdline" 2>/dev/null | grep -q "$1"; then echo "$pid"; return 0; fi
  done
  return 1
}
start_web_nobuild() {
  echo "[deploy] starting static+gateway on :$WEB_PORT (no rebuild)"
  nohup python3 "$PIDDIR/gateway.py" > "$PIDDIR/web.log" 2>&1 &
  sleep 2
  wpid="$(resolve_pid "tianji-intranet/gateway.py")"
  [ -n "$wpid" ] || { echo "[deploy] ERROR: gateway did not start"; exit 1; }
  echo "$wpid" > "$PIDDIR/web.pid"
  echo "tianji-intranet/gateway.py" > "$PIDDIR/web.tag"
  echo "[deploy] gateway running as pid $wpid"
}
case "$cmd" in
  start)
    start_api; sleep 6; start_web; sleep 3
    if ! do_health; then
      echo "[deploy] health check FAILED - cleaning up services started in this run"
      do_stop
      exit 1
    fi ;;
  stop) do_stop ;;
  rollback) do_rollback ;;
  health) do_health ;;
  status)
    for n in api web; do
      stag="$(cat "$PIDDIR/$n.tag" 2>/dev/null || echo "")"
      if [ -n "$stag" ] && pid_owned "$PIDDIR/$n.pid" "$stag"; then echo "$n: running (pid $(cat "$PIDDIR/$n.pid"))"; else echo "$n: stopped"; fi
    done ;;
  *) echo "usage: $0 [start|stop|status|health|rollback]"; exit 1 ;;
esac
