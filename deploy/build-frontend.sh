#!/bin/bash
# Build the production frontend bundle into deploy/frontend-dist/.
# Run from the repository root. Requires node + npm.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/web/visual-prototype"
npm ci --no-audit --no-fund
npm run build
rm -rf "$ROOT/deploy/frontend-dist"
cp -r dist "$ROOT/deploy/frontend-dist"
echo "frontend bundle -> $ROOT/deploy/frontend-dist"
ls "$ROOT/deploy/frontend-dist"
