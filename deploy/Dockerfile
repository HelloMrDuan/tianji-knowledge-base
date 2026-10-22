# Tianji API deployment image (public code only; no private knowledge baked in).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime deps first for layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir "./[api,calendar,validation]"

# Public code only. Private knowledge is mounted at runtime, never baked in.
COPY src/ ./src/
COPY config/ ./config/
COPY schemas/ ./schemas/

# Drop privileges.
RUN useradd -m -u 10001 tianji && chown -R tianji:tianji /app
USER tianji

EXPOSE 8000

# Health endpoint is GET /health (no auth).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status==200 else 1)"

CMD ["python", "-m", "uvicorn", "tianji_kb.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
