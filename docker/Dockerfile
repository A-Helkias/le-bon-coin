# --- Build du frontend ------------------------------------------------------

FROM node:22-alpine AS frontend

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

ENV VITE_API_BASE_URL=""
RUN npm run build

# --- API + frontend statique ------------------------------------------------

FROM python:3.12-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

WORKDIR /app

COPY backend/ ./
RUN uv sync --frozen --no-dev

COPY --from=frontend /build/dist ./static

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health')"

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
