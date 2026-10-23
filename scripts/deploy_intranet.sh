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

start_api() {
  echo "[deploy] starting API on :$API_PORT (backend: $BACKEND_DIR)"
  [ -d "$BACKEND_DIR/src" ] || { echo "[deploy] ERROR: backend not found at $BACKEND_DIR"; exit 1; }
  cd "$BACKEND_DIR"
  PYTHONPATH="$BACKEND_DIR/src:${PYTHONPATH:-}" nohup python3 -m uvicorn tianji_kb.api:app \
    --host 127.0.0.1 --port "$API_PORT" > "$PIDDIR/api.log" 2>&1 &
  echo $! > "$PIDDIR/api.pid"
}
start_web() {
  echo "[deploy] building frontend"
  cd "$ROOT/web/visual-prototype"
  npm run build > "$PIDDIR/build.log" 2>&1 || { echo "[deploy] ERROR: frontend build failed"; tail -20 "$PIDDIR/build.log"; exit 1; }
  echo "[deploy] starting static+gateway on :$WEB_PORT"
  cat > "$PIDDIR/gateway.py" << PYEOF
import http.server, urllib.request, urllib.error
DIST = "$ROOT/web/visual-prototype/dist"
API = "http://127.0.0.1:$API_PORT"
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=DIST, **k)
    def do_GET(self):
        if self.path.startswith("/api/"): self._proxy()
        else: super().do_GET()
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
  echo "[deploy] stopping (rollback)"
  for f in "$PIDDIR/api.pid" "$PIDDIR/web.pid"; do
    [ -f "$f" ] && kill "$(cat "$f")" 2>/dev/null || true
    rm -f "$f"
  done
  echo "[deploy] stopped"
}
case "$cmd" in
  start) start_api; sleep 6; start_web; sleep 3; do_health ;;
  stop) do_stop ;;
  health) do_health ;;
  status)
    for n in api web; do
      if [ -f "$PIDDIR/$n.pid" ] && kill -0 "$(cat "$PIDDIR/$n.pid")" 2>/dev/null; then echo "$n: running (pid $(cat "$PIDDIR/$n.pid"))"; else echo "$n: stopped"; fi
    done ;;
  *) echo "usage: $0 [start|stop|status|health]"; exit 1 ;;
esac
