# Tianji API sealed-runtime image.
#
# This image contains ONLY Python + third-party dependencies. NO tianji code,
# NO knowledge, NO secrets are baked in. At runtime the audited sealed bundle
# (built by scripts/export_sealed_runtime.py) is mounted read-only at /sealed
# and Python loads tianji_kb from there. The entrypoint fails fast unless the
# pinned sealed bundle is actually in use.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install third-party deps from pyproject (single source of truth);
# the tianji_kb package itself is NOT installed -- it comes from /sealed.
COPY pyproject.toml ./
RUN python - <<'PYEOF'
import tomllib, subprocess, sys
with open('pyproject.toml', 'rb') as f:
    optional = tomllib.load(f)['project']['optional-dependencies']
pkgs = optional['api'] + optional['calendar'] + optional['validation']
subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', *pkgs], check=True)
PYEOF
RUN rm pyproject.toml

COPY deploy/docker-entrypoint.py ./docker-entrypoint.py

RUN useradd -m -u 10001 tianji && chown -R tianji:tianji /app
USER tianji

EXPOSE 8000

# Sealed runtime mount is required; the entrypoint verifies it.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status==200 else 1)"

ENTRYPOINT ["python", "/app/docker-entrypoint.py"]
