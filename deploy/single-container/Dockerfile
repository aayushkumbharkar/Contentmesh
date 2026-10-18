# Single-container public demo (Render free web service; build context = repository root).
# FalkorDB listens on 127.0.0.1 only; only the FastAPI app is exposed, on $PORT.
FROM node:22-alpine AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/index.html frontend/tsconfig.json frontend/vite.config.ts ./
COPY frontend/src ./src
RUN npm run build

FROM falkordb/falkordb:v4.14.11 AS falkordb

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY --from=falkordb /usr/local/bin/redis-server /usr/local/bin/redis-cli /usr/local/bin/
COPY --from=falkordb /var/lib/falkordb/bin/falkordb.so /opt/falkordb/falkordb.so
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend /build/dist ./static
COPY deploy/single-container/start.sh ./start.sh
RUN useradd --uid 1000 --create-home user
USER user
ENV FRONTEND_DIST=/app/static LLM_PROVIDER=demo FALKORDB_HOST=127.0.0.1 FALKORDB_PORT=6379 DATA_DIR=/home/user/graph-data
EXPOSE 7860
CMD ["sh", "/app/start.sh"]
