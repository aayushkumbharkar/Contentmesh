# Verification record

Checked on 18 October 2026 (Asia/Calcutta) against the current repository, without replacing FalkorDB with a mock.

## Results

| Check | Actual result |
| --- | --- |
| `.\.venv\Scripts\python.exe -m pytest tests -q` | **17 passed**, 1 deprecation warning, 53.75 seconds; real FalkorDB on loopback port 6380. |
| Memory revision provenance regression | **1 passed**, 2.83 seconds after adding assertions that prior revision evidence and updated memory remain untrusted. |
| `npm run build` in `frontend` | **Passed**: TypeScript and Vite production build. |
| `npm audit --json` in `frontend` | **Passed**: 0 reported vulnerabilities, including development dependencies. |
| `.\.venv\Scripts\python.exe -m pip_audit -r backend/requirements.txt --format json` | **Passed**: no known vulnerabilities found in resolved backend dependencies. |

The backend suite covers graph writes/readback using a fresh client; actual neighborhood and path relationships; two separate sessions recalling a unique saved note; all four agent outputs and persisted handoffs; task dependency edges; memory revision history; cross-workspace isolation; hostile identifiers and literal Cypher-like note content; bounded retrieval; absent evidence; conflicting facts; sanitized database failures; missing handoff refusal; failed-run recording; and deterministic provider fallback. Prior generated decisions are excluded as source evidence.

The added provenance assertions are in `tests/test_graph_safety.py::test_memory_revision_paths_and_neighborhood_are_workspace_local`. They prevent a memory edit from promoting an unverified user note into trusted evidence.

## Reproduce

Start FalkorDB using `docker compose up -d falkordb`. On PowerShell from the repository root:

```powershell
$env:FALKORDB_PORT='6380'
.\.venv\Scripts\python.exe -m pytest tests -q
Set-Location frontend
npm run build
npm audit --json
```

Tests create unique disposable graphs and delete only their own generated namespaces. The first sandboxed attempt could not open the local database socket (`WinError 10013`) and was interrupted; the successful run used permitted local socket access. The initial sandboxed npm audit also could not resolve the registry; the successful audit used permitted network access. Neither blocked attempt is counted as a passing check.

## Warnings and limits

- Starlette emits a TestClient deprecation warning for `httpx`; requests and tests still pass. No dependency was changed merely to suppress this warning.
- Vite reports a 656.45 kB minified JavaScript chunk (176.28 kB gzip), above its 500 kB advisory threshold. This is a size warning, not a build failure.
- Automated API tests use FastAPI TestClient and a real database; they do not prove browser rendering, public hosting, YouTube upload, blog publication, or restart durability. Those need separate observed checks.
- Graph workspace separation is not user authentication. The default deployment is a trusted local demo; public deployment must account for the unauthenticated mutation endpoints.
- No external Groq call, throughput benchmark, latency benchmark, or production scalability claim was verified by this test run.

## Additional checks

Lead-owned browser/restart/publication checks are recorded when their actual results are available. Do not interpret a prepared Docker configuration or a saved article as proof of deployment or publication.
