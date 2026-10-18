# ContextMesh: giving four agents a shared memory they can explain

A useful incident investigation rarely fits inside one conversation. Someone records an observation, another engineer remembers a configuration change, and a previous incident contains the lesson that could connect them. When a new session starts, those relationships should still exist.

ContextMesh is my Graph Hacks project: a React, TypeScript, and Three.js workspace backed by FastAPI and FalkorDB. Four runtime stages—Researcher, Planner, Executor, and Verifier—coordinate through persisted graph records. The interface lets a user inspect the evidence, memories, and relationship paths behind an investigation.

The central design decision is simple: the graph is the application's working memory. It supplies context to the workflow and stores its outputs. The visualization displays that same persisted data.

## A deliberately small incident scenario

The demo uses **AcmeShop**, an explicitly synthetic software company. Its Checkout API uses Redis sessions. Release 2.4 reduced the recorded session TTL from 3,600 seconds to 60 seconds; checkout errors appeared afterward. Maya Chen is the recorded system owner. An earlier incident, INC-104, documents a similar configuration problem and a resolution involving restoring the TTL, checking sessions, monitoring checkout completion, and adding a regression check.

These are fixture facts, not observations about a real production system. Even within the scenario, a configuration change occurring before an incident does not prove causality. ContextMesh presents it as an investigation candidate and asks for operational verification.

In the first session, a user adds an incident note. In a separate session, they ask which earlier change might explain the problem, who owns the system, and what was learned previously. The second run retrieves saved records from FalkorDB, including notes from the first session. It does not need the first conversation copied into a prompt.

## Modeling memory and coordination together

The graph contains `Workspace`, `Session`, `Memory`, `Evidence`, `Entity`, `Task`, `Decision`, `Agent`, `AgentRun`, and `Run` nodes.

Different relationships answer different questions. `OWNED_BY` connects a system to an owner. `AFFECTS` connects a change or incident to a system. `RESOLVED_BY` connects a previous incident to its documented lesson. `HAS_MEMORY` preserves session provenance. `GENERATED` connects runs and agents to their outputs. `DEPENDS_ON` records task ordering, while `HANDOFF_TO` connects consecutive agent executions.

Each workspace uses its own graph name, derived from a validated identifier. This keeps repository queries scoped to a workspace. It is useful isolation, but it is **not authentication**: the current application is a trusted local demonstration, not a secure public multi-user service.

User notes carry `source: user_note` and `trusted: false`. Updating a memory first creates an Evidence node containing the previous text and revision number. That preserves the earlier statement rather than silently replacing its provenance.

## Retrieval starts with terms, then follows relationships

The current retriever is intentionally understandable. It extracts bounded search terms from the question, matches labels and text, and expands along selected semantic relationships. It does not use embeddings or claim a sophisticated semantic ranking system.

The initial query uses parameters for user-derived values:

```cypher
MATCH (n)
WHERE n.kind IN $kinds
  AND any(term IN $terms WHERE
    toLower(coalesce(n.label, "") + " " + coalesce(n.text, ""))
    CONTAINS term)
RETURN n
ORDER BY n.updated_at DESC
LIMIT 12
```

The next query follows relevant connections rather than indiscriminately traversing session and execution hubs:

```cypher
MATCH p=(s)-[:MENTIONS|RELATES_TO|SUPPORTS|DEPENDS_ON|OWNED_BY|AFFECTS|RESOLVED_BY*1..3]-(n)
WHERE s.id IN $ids
RETURN [x IN nodes(p) | x.id],
       [r IN relationships(p) | type(r)]
LIMIT 80
```

The workflow requests at most 20 context nodes. Returned paths are filtered so their nodes remain inside that selected context. Separate neighborhood and path methods also impose hop and result limits.

For example, the seeded graph can connect `redis-change` to `checkout-api` and then `maya-chen`. ContextMesh queries those connections; it never asks a language model to invent a plausible-looking path. Traversals can follow relationships in either direction, so a displayed path describes connectivity, not a causal proof or necessarily a forward-directed chain.

## Four stages with durable handoffs

The Researcher retrieves facts and memories, then persists their identifiers, relationships, and paths in an AgentRun record. Explicitly mentioned entity labels create `MENTIONS` relationships from the new note.

The Planner reads the Researcher's saved output back from FalkorDB. It creates three dependent investigation tasks. Their wording and supporting relationships change according to whether affected-system, ownership, and prior-resolution evidence were retrieved. Missing relationships become explicit gaps.

The Executor reads the saved plan, reloads its evidence nodes, and writes an investigation Decision with `SUPPORTS` relationships. It records whether evidence includes memories from other sessions. Tasks lacking required relationships remain blocked. Execution here means safe internal record creation; it never changes Redis configuration or operates production infrastructure.

The Verifier reloads evidence and queries paths again. It flags specific competing owner and current-TTL assertions, reports evidence gaps, and qualifies causality. Its contradiction checks are narrow rules, not a general fact-checking model. Previously generated Decisions are excluded from the final evidence candidates, preventing the system from repeatedly treating its own conclusions as independent sources.

These are four bounded, deterministic runtime roles. They are not four autonomous LLM conversations. Persisted handoffs still matter: downstream stages read their predecessor's saved record, and a missing handoff stops the workflow.

## Optional language generation, bounded by design

Demo mode needs no model key, but always needs real FalkorDB. There is no in-memory database fallback.

An optional Groq adapter can add a clearly labeled model hypothesis after evidence verification. It receives at most 12 facts, each shortened to 500 characters, and a question capped at 2,000 characters. The adapter also caps serialized input, requests JSON output, allows 400 completion tokens, uses a timeout, and makes one call without automatic retries.

Provider failure leaves the deterministic evidence answer intact. Returned token counts are recorded when available. Dollar cost is an estimate calculated only when rates are configured; missing rates mean unknown cost. Character limits are practical input bounds, not exact token accounting.

## Making the graph inspectable

The Three.js view renders nodes and edges returned by the API. Orbit controls support camera movement, node selection opens properties and connected relationships, and search helps locate entities. The layout is a visual arrangement, not an embedding or relevance score.

A list alternative supports users who prefer keyboard-accessible records or cannot use WebGL. Other panels expose saved memories, session history, completed agent steps, usage information, supporting facts, and queried paths. Execution traces are persisted results; the application does not pretend they are a live streaming scheduler.

## Testing the claims that matter

The repository's tests require a real FalkorDB instance. They cover graph round trips, path-to-edge consistency, two-session recall using a unique note marker, persisted handoffs, memory revisions, workspace isolation, injection-shaped literal input, empty retrieval, contradiction warnings, and provider failure.

One particularly useful test removes access to a persisted handoff and checks that downstream tasks are not created. Another asks an unrelated question and expects empty evidence and paths rather than a convenient demo answer. Failure-injection tests check that errors do not expose private connection details.

Docker Compose configures FalkorDB append-only persistence and a named data volume. Ordinary container restarts preserve that volume; deliberately removing it erases the data. A fresh client round-trip test is distinct from a complete container-restart check, and neither is a performance benchmark.

The current verification run passed all 17 tests against real FalkorDB. The frontend production build passed, and npm audit and pip-audit reported no known dependency vulnerabilities. These checks establish functional behavior for the tested scenarios, not performance or production-readiness.

## What building it taught me

The most valuable constraint was requiring evidence to survive each boundary: session to memory, Researcher to Planner, and final answer to UI. It exposed shortcuts that a polished chat interface could otherwise conceal.

Bounded retrieval also makes tradeoffs visible. Term matching can miss relevant context, and result caps can omit useful evidence. The workflow is synchronous, writes are not one atomic transaction, and interrupted runs do not automatically resume. Public deployment needs authentication, authorization, rate limiting, and operational hardening.

OpenAI Codex assisted implementation, integration, and testing, including native coding sub-agents with separate module ownership. Those engineering assistants are distinct from ContextMesh's four runtime roles. The goal of this project is a small, inspectable foundation: shared context that persists, coordination that leaves records, and answers whose supporting relationships can be examined.


## Explore the project

[Source code and local setup](https://github.com/aayushkumbharkar/Contentmesh) · [Graph schema and queries](https://github.com/aayushkumbharkar/Contentmesh/blob/main/docs/graph.md) · [Verification report](https://github.com/aayushkumbharkar/Contentmesh/blob/main/docs/verification.md)
