# Architecture

React + Vite + TypeScript renders data returned by FastAPI. Three.js provides orbit, zoom, picking, and node labels; a keyboard-accessible list presents the same data without WebGL. Nginx serves the built UI and proxies /api to FastAPI. FalkorDB is the sole durable memory store with AOF enabled on a named volume.

## Execution

1. Researcher stores an explicitly unverified user note and provenance, retrieves a bounded semantic neighborhood, and records matching sources and real paths. Only explicitly mentioned entity labels become MENTIONS edges.
2. Planner reads the persisted Researcher AgentRun, inspects AFFECTS / OWNED_BY / RESOLVED_BY edges, and creates dependent investigation tasks with relationship basis. Missing facts produce blocked checks.
3. Executor reads the saved plan, retrieves referenced facts again, persists a hypothesis Decision and SUPPORTS links, and completes safe internal checks. It does not operate production systems.
4. Verifier reads the saved execution output, checks sources and actual queried paths, flags recognized owner/config conflicts and evidence gaps, and persists the final answer. Prior Decisions never become source evidence.

The orchestrator schedules stages synchronously. Each AgentRun has input references, structured JSON output, output references and HANDOFF_TO relationships. Sessions and Run.result survive process restarts. Partial failures mark the Run failed when the database is reachable; a total outage can leave a running record and requires operator inspection. There is no automatic retry of mutations or resume engine.

## Bounds and isolation

Each workspace maps to a validated FalkorDB graph name. All dynamic values are query parameters; node kinds, relation names, identifiers, and depth are validated/allowlisted. Graph reads cap nodes/edges, semantic retrieval caps sources and paths, each run has four stages, and optional synthesis makes at most one 20-second call with a 10,000-character payload and 400 output tokens. Token budgeting before inference uses a conservative character cap rather than claiming exact tokenization. No provider tool calls or automatic retries. Structured state remains separate from prose.

User notes and model text are untrusted. Notes are labeled unverified, hypotheses retain uncertainty, model synthesis is supplementary, and evidence paths come from database results. Contradiction checks recognize selected AcmeShop owner/TTL assertions; they are not a general semantic proof system. Lexical retrieval is deterministic and bounded, not vector search. Large workspaces need ranking/pagination and index tuning; the current graph viewport is capped at 300 recent nodes.

The API is intended for localhost use. Graph isolation is storage isolation, not access control. There is no login, distributed job queue, arbitrary Cypher endpoint, shell execution, autonomous remediation, or external messaging.

## Provider references

Implementation follows [Groq chat completion API](https://console.groq.com/docs/api-reference) and the [official FalkorDB Python client](https://github.com/FalkorDB/falkordb-py). Provider selection, model and credentials are environment configuration. Runtime provider charges are separate from Codex engineering usage.
