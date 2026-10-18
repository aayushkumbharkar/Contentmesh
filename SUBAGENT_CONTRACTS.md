# ContextMesh sub-agent contracts

These are the coding-time Codex workers. They are not the runtime agents shipped inside ContextMesh.

## A. Frontend / Three.js
**Owns:** `frontend/` only.
**Build:** dashboard shell, session sidebar, agent timeline, memory inspector, graph visualization using Three.js (React Three Fiber if practical), node/edge inspection and evidence panel; accessible 2D/list fallback.
**Must not:** invent graph nodes/edges or fake run status; change backend contracts unilaterally.
**Acceptance:** `npm run build` succeeds; graph view renders provided API data; loading/empty/error states work; selected node shows real properties and relationships.

## B. FalkorDB graph foundation
**Owns:** `backend/app/graph/`, graph schema/query docs and graph-layer tests.
**Build:** connection management, safe graph selection/isolation, schema, seed data, parameterized queries, neighborhood/path retrieval, health check.
**Must not:** build the frontend or own agent orchestration.
**Acceptance:** against a real FalkorDB instance, seed data can be written, queried, and returned as nodes/edges; unsafe arbitrary user Cypher is not exposed.

## C. Persistent memory and agent coordination
**Owns:** `backend/app/memory/` and `backend/app/orchestration/`.
**Build:** retrieval of relevant graph memories, distinct researcher/planner/executor/verifier roles, persisted run records and handoffs, evidence-backed final response, deterministic mode.
**Must not:** implement its own alternate durable database or make up graph paths; use the graph layer's agreed interface.
**Acceptance:** session 2 recovers a fact from session 1 via FalkorDB; agent inputs/outputs and handoffs are queryable; unsupported claims are marked uncertain.

## D. Quality / local runtime
**Owns:** `tests/`, Docker Compose, `.env.example`, and `docs/verification.md`.
**Build:** local startup, readiness/health checks, test fixtures, workspace isolation tests, persistence-after-restart test, smoke-test script.
**Must not:** rewrite implementation modules owned by other agents. File issues with exact reproduction and let the owner fix them.
**Acceptance:** one documented command starts services; one documented command runs tests; test report separates passed, failed and not-run checks.

## Main coordinator
**Owns:** root structure, architecture and API contracts, integration, merge decisions, README finalization and end-to-end test.
**Coordination rules:** define contracts before delegation; collect concise reports; inspect diffs; integrate one boundary at a time; do not accept a sub-agent's claim without evidence; resolve file conflicts centrally.

## Runtime agent roles in the actual product
1. Researcher — retrieves relevant graph context and source facts.
2. Planner — creates steps based on graph dependencies.
3. Executor — performs safe internal work or emits clearly labeled proposed actions.
4. Verifier — checks claims against evidence and records gaps/contradictions.

These runtime roles must communicate through persisted graph records. A coordinator process may schedule them, but downstream agents must retrieve prior context from FalkorDB rather than relying only on copied chat prompts.
