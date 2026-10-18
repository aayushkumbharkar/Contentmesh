# Codex kickoff — ContextMesh

Use the repository's `AGENTS.md` as project guidance. Build ContextMesh as a graph-native multi-agent platform for the Graph Hacks / FalkorDB challenge.

## First response
Inspect the current project, available tools and installed skills. Report only:
1. existing repo state and critical constraints;
2. a short implementation sequence;
3. which independent tasks can be delegated safely.
Do not print long architecture essays or dump skill contents.

## Delegate carefully
Use Codex sub-agents if this session supports them. Run a maximum of four independent implementation agents concurrently. Each agent must have one clear deliverable, an explicit set of owned paths, and acceptance tests. If native sub-agents are unavailable, carry out the same work in sequential, clearly separated work packages—do not pretend parallel agents ran.

Recommended work packages:
1. Frontend + graph visualization: own `frontend/` only; React, TypeScript, Three.js/React Three Fiber, interactive node/edge selection, evidence panel, 2D accessible fallback.
2. FalkorDB graph adapter: own `backend/app/graph/` and graph schema docs only; official Python client, safe Cypher, seed graph, health check, query tests.
3. Memory + agent orchestration: own `backend/app/memory/` and `backend/app/orchestration/` only; cross-session retrieval, researcher/planner/executor/verifier roles, persisted handoffs and evidence.
4. Quality + local runtime: own `tests/`, Docker Compose, `.env.example`, and deployment test documentation; verify real database connectivity, persistence and tenant isolation.

The main agent owns the shared API contracts, root project structure, integration, final UI/API compatibility and documentation merge. First agree on interface contracts and paths; do not let agents edit the same file concurrently. Avoid spawning agents for tiny tasks or asking several agents to solve the same problem.

## Implementation sequence
1. Inspect repo; establish a compact plan and API/schema contracts.
2. Start FalkorDB with Docker Compose and prove the backend can write/read a real graph.
3. Implement the minimal graph-backed vertical slice and two-session persistence scenario.
4. Integrate the four specialist roles, with each handoff stored/retrieved from FalkorDB.
5. Add traceable evidence paths generated from real query results.
6. Build the React interface and interactive 3D graph; keep the text/list fallback usable.
7. Run tests, fix failures, validate a restart, and polish the demo only after the core works.

## Required demo
Use an explicitly synthetic `AcmeShop` workspace. Seed a Checkout API, release 2.4, a Redis TTL change, an incident, an assigned engineer, and a previous incident with a documented resolution. Confirm seed relationships support the demo questions.

Session 1: add a note about the incident, run the workflow, and persist extracted facts, evidence and handoffs.
Session 2: ask which earlier change may explain the incident, who owns the affected system, and what was learned previously.
The answer must retrieve memory from FalkorDB and show actual evidence nodes and a real relationship path returned by graph queries. Verify after page refresh and backend restart.

## Required completion report
At the end, report briefly:
- implemented and verified features;
- commands actually run and test outcomes;
- local start steps;
- known defects or limitations;
- exact steps to capture the 90-second demo.
Do not claim tests, integrations, or deployment succeeded without running them.
