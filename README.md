# ContextMesh

A graph-native incident workspace: four agents coordinate through persistent FalkorDB records, while a React / Three.js interface shows the evidence behind their work. AcmeShop is entirely synthetic.

## Submission status (18 Oct 2026)

- Video files: `submission/contextmesh-demo-voiced.mp4` (uploaded), `submission/video/contextmesh-trailer.mp4`
- Verified locally: 17 tests pass against real FalkorDB; `scripts/verify_demo.py --restart` passes (cross-session recall survives FalkorDB and backend restarts)
- **Live demo:** https://contextmesh-e25o.onrender.com (Render free plan; sleeps when idle, and the graph resets on restart; see [deployment](docs/deployment.md))
- **Demo video:** https://youtu.be/B06nzWsC9nk
- Submission answers: [submission/SUBMISSION_FORM.md](submission/SUBMISSION_FORM.md)

## Start

Requires Docker Desktop with Linux containers (or Docker Engine + Compose).

```sh
docker compose up --build -d
```

Open http://localhost:5173. Click **Load synthetic demo**, then **Record an incident** and **Run investigation**. Create a **New session**, choose **Recall earlier context**, and run again. Expand supporting evidence to inspect actual graph paths. Reload the page: sessions and results remain. `docker compose restart` preserves the named graph volume. `docker compose down` also preserves it; do not add `-v` unless intentionally erasing saved data.

Ports bind to loopback: UI 5173, API 8000, FalkorDB 6380. Container-to-container database port is 6379. API docs: http://localhost:8000/docs. Health: http://localhost:8000/api/health.

## Local development

Python 3.10+ and Node 20.19+ / 22 supported. On PowerShell:

```powershell
docker compose up -d falkordb
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements.txt
$env:PYTHONPATH='backend'
$env:FALKORDB_PORT='6380'
.\.venv\Scripts\python -m uvicorn app.main:app --reload
# Separate terminal:
cd frontend
npm ci
npm run dev
```

Copy `.env.example` to `.env` for Compose settings. Local Python reads process environment variables, not .env automatically. Demo mode needs no LLM key and always uses real FalkorDB. Set `LLM_PROVIDER=groq`, `GROQ_API_KEY`, and `GROQ_MODEL` to enable one optional synthesis call per run. Provider failures retain the deterministic evidence result. No key is sent to the browser. Optional cost rates are user-configured USD per million tokens; token usage is provider-measured when returned, cost is an estimate, and absent rates mean unknown cost.

## Test

```powershell
$env:FALKORDB_PORT='6380'
.\.venv\Scripts\python -m pytest tests -q
```

Tests require real FalkorDB; database unavailability fails rather than silently mocking persistence. Disposable test graphs use unique namespaces. See [verification](docs/verification.md) for browser, restart, failure and audit checks and [demo storyboard](docs/demo.md) for recording steps.

## Design

- [Architecture and limits](docs/architecture.md)
- [Graph model and Cypher](docs/graph.md)
- [Shared API and ownership contracts](docs/contracts.md)
- [AI assistance disclosure](docs/ai-disclosure.md)

This is a trusted local demonstration, not a public multi-user service. Workspace namespaces prevent accidental cross-workspace queries; they are not authentication or authorization. Add authenticated workspace membership, request rate limits, TLS, backups, and production operations before external deployment. The executor only persists internal investigation records; it never changes Redis configuration or production systems.
