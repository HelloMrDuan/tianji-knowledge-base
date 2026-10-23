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
  cd "$BACKEND_DIR"
  PYTHONPATH="$BACKEND_DIR/src:${PYTHONPATH:-}" nohup python3 -m uvicorn tianji_kb.api:app \
    --host 127.0.0.1 --port "$API_PORT" > "$PIDDIR/api.log" 2>&1 &
  echo $! > "$PIDDIR/api.pid"
  echo "uvicorn tianji_kb.api:app" > "$PIDDIR/api.tag"
}
start_web() {
  echo "[deploy] building frontend"
  cd "$ROOT/web/visual-prototype"
  # Keep the previous build so `rollback` can restore a real previous version.
  if [ -d dist ] && [ ! -e "$PIDDIR/dist.prev" ]; then
    mv dist "$PIDDIR/dist.prev"
    echo "[deploy] previous build saved to $PIDDIR/dist.prev"
  elif [ -d dist ]; then
    rm -rf "$PIDDIR/dist.prev"
    mv dist "$PIDDIR/dist.prev"
    echo "[deploy] previous build saved to $PIDDIR/dist.prev"
  fi
  npm run build > "$PIDDIR/build.log" 2>&1 || { echo "[deploy] ERROR: frontend build failed"; tail -20 "$PIDDIR/build.log"; exit 1; }
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
  echo $! > "$PIDDIR/web.pid"
  echo "tianji-intranet/gateway.py" > "$PIDDIR/web.tag"
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
  # Restores the previous frontend build and restarts the gateway, then
  # verifies with a health check. Only after this passes may rollback be claimed.
  [ -d "$PIDDIR/dist.prev" ] || { echo "[deploy] ERROR: no previous build to roll back to"; exit 1; }
  echo "[deploy] rolling back to previous build (frontend only; API untouched)"
  # Stop only the gateway, keep the API running.
  tag="$(cat "$PIDDIR/web.tag" 2>/dev/null || echo "tianji-intranet/gateway.py")"
  if pid_owned "$PIDDIR/web.pid" "$tag"; then kill "$(cat "$PIDDIR/web.pid")" 2>/dev/null || true; fi
  rm -f "$PIDDIR/web.pid" "$PIDDIR/web.tag"
  rm -rf "$ROOT/web/visual-prototype/dist"
  mkdir -p "$ROOT/web/visual-prototype/dist"
  cp -r "$PIDDIR/dist.prev/." "$ROOT/web/visual-prototype/dist/"
  start_web_nobuild
  sleep 3
  do_health && echo "[deploy] rollback verified: previous version serving"
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
