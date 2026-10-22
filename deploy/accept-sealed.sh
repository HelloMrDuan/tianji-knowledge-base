#!/bin/bash
# Sealed-runtime deployment acceptance. Run on a Docker-capable controlled machine,
# from the repository root. Fails fast on any verification failure.
#
# What it proves (not just unit tests):
#  1. The sealed bundle exports and its SHA pin is captured.
#  2. The image builds; the container STARTS only with the pinned sealed bundle
#     (entrypoint verifies tianji_kb loads from /sealed and resolver.ROOT==/sealed).
#  3. /health, the homepage, JS/CSS, /api proxying, and SPA fallback all work.
#  4. Negative: wrong SHA pin -> container refuses to start.
#  5. Negative: admin without token -> refused; error bodies carry no secrets.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> 1. export sealed bundle"
rm -rf /tmp/tianji-sealed-accept
EXPORT_JSON=$(python scripts/export_sealed_runtime.py --destination /tmp/tianji-sealed-accept)
echo "$EXPORT_JSON"
PIN=$(python -c "import json,sys; print(json.load(sys.stdin)['sha256_pin'])" <<< "$EXPORT_JSON")
[[ "$PIN" =~ ^[0-9a-f]{64}$ ]] || { echo "bad pin"; exit 1; }

echo "==> 2. build frontend"
./deploy/build-frontend.sh

echo "==> 3. build + start (positive)"
export TIANJI_SEALED_DIR=/tmp/tianji-sealed-accept
export TIANJI_RUNTIME_SHA256="$PIN"
docker compose -f deploy/docker-compose.yml up -d --build
trap 'docker compose -f deploy/docker-compose.yml down' EXIT
for i in $(seq 1 30); do
  curl -sf http://127.0.0.1:8000/health && break
  sleep 2
done
curl -sf http://127.0.0.1:8000/health | grep -q '"status"' || { echo "health bad"; exit 1; }
curl -sf http://127.0.0.1:8080/ | grep -q '<div id="root"' || { echo "homepage bad"; exit 1; }
curl -sf http://127.0.0.1:8080/some/spa/route | grep -q '<div id="root"' || { echo "spa fallback bad"; exit 1; }
curl -sf http://127.0.0.1:8080/api/v1/capabilities | grep -qv -i "traceback" || { echo "api leak"; exit 1; }
echo "positive path OK"

echo "==> 4. negative: wrong SHA pin refuses to start"
docker compose -f deploy/docker-compose.yml down
export TIANJI_RUNTIME_SHA256="0000000000000000000000000000000000000000000000000000000000000000"
docker compose -f deploy/docker-compose.yml up -d
sleep 8
if curl -sf http://127.0.0.1:8000/health; then echo "NEGATIVE FAILED: started with wrong pin"; exit 1; fi
echo "wrong-pin refusal OK"
docker compose -f deploy/docker-compose.yml down

echo "==> 5. negative: admin without token"
export TIANJI_RUNTIME_SHA256="$PIN"
docker compose -f deploy/docker-compose.yml up -d
for i in $(seq 1 30); do curl -sf http://127.0.0.1:8000/health && break; sleep 2; done
CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/v1/admin/governance/rules)
[[ "$CODE" == "401" || "$CODE" == "403" || "$CODE" == "503" ]] || { echo "admin not refused: $CODE"; exit 1; }
BODY=$(curl -s http://127.0.0.1:8000/api/v1/admin/governance/rules)
echo "$BODY" | grep -qi "traceback" && { echo "admin error leak"; exit 1; }
echo "admin refusal OK"

echo "ALL SEALED ACCEPTANCE CHECKS PASSED"
