# Deployment

The root `Dockerfile` builds the React/Three.js frontend with Node 22 and serves its compiled files through FastAPI in a Python 3.12 image. `FRONTEND_DIST=/app/static` enables static hosting. The API binds to Railway's `PORT` (8000 locally). The container runs as an unprivileged user.

## Railway configuration

Use a dedicated project with two services:

1. **falkordb**: image `falkordb/falkordb:v4.14.11`; persistent volume mounted at `/data`; start command `redis-server --loadmodule /FalkorDB/bin/falkordb.so --appendonly yes --dir /data --bind 0.0.0.0 :: --protected-mode no`. Keep this service on the private network; do not create a public TCP proxy or HTTP domain.
2. **contextmesh**: deploy the root repository using `Dockerfile` and `railway.json`. Set `FALKORDB_HOST` to the database service's Railway private hostname, `FALKORDB_PORT=6379`, and `LLM_PROVIDER=demo`. Generate an HTTPS service domain for this service only. `/api/health` verifies database availability.

This public hackathon demo is a shared synthetic workspace, not an authenticated multi-user deployment. Do not enter secrets or personal data. Workspace partitioning is not authentication. Keep the paid LLM provider disabled for the public demo. A production deployment requires authentication, authorization, quotas and operational monitoring.

## Deployment attempt on 18 October 2026

Railway authentication succeeded and the existing projects were inspected. Creating the dedicated `contextmesh` project failed with the provider response: **“Your trial has expired. Please select a plan to continue using Railway.”** No project, service, volume, or public application URL was created. The unrelated existing project was left unchanged. Deployment requires the account owner to select a Railway plan; no subscription or payment was initiated.

## Local deployment-image verification

```powershell
docker build -t contextmesh-public-demo:local .
```

The existing `compose.yaml` remains the recommended local startup route, with its persistent FalkorDB volume and separate frontend/API services. The root image is the combined frontend/API packaging for hosted deployment.
