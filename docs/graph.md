# Graph model and retrieval

ContextMesh uses the official `falkordb` Python client. Every workspace maps to its own graph key (`contextmesh_<workspace_id>`). Workspace names are validated before selecting a graph; all node IDs, text and other values are query parameters. Node labels and relationship types come from fixed allowlists. No endpoint accepts Cypher. Database failures become `GraphUnavailable` with a safe public message and the original exception retained for server-side diagnostics.

## Nodes

All nodes have stable `id`, `kind`, `label`, `created_at`, and `updated_at` scalar properties. Structured run outputs are JSON strings; the graph itself remains the durable store.

| Kind | Purpose |
| --- | --- |
| Workspace | Workspace identity and synthetic-fixture disclosure |
| Session | Separate conversations with retained history |
| Memory | User notes, provenance, and continuity across sessions |
| Evidence | Source facts and documented resolutions |
| Entity | Services, releases, incidents, people |
| Task | Scoped agent actions and dependencies |
| Decision | Evidence-backed synthesis and qualifications |
| Agent | Runtime agent identity |
| AgentRun | Persisted specialist inputs, outputs and status |
| Run | Complete execution record and replayable result |

## Relationships

`HAS_SESSION`, `HAS_MEMORY`, and `HAS_RUN` organize durable history. `MENTIONS` links notes and workspace context to entities. `RELATES_TO` expresses association without asserting causation. `SUPPORTS` connects supporting facts. `DEPENDS_ON` captures task prerequisites. `GENERATED` records provenance and outputs. `HANDOFF_TO` links persisted specialist executions. `OWNED_BY` captures service ownership. `AFFECTS` connects releases, configuration and incidents to their systems. `RESOLVED_BY` preserves the resolution of earlier incidents. `NEXT` can order session/run records.

The fixture is explicitly synthetic. Its path Redis change → Checkout API → Maya Chen explains ownership; previous incident → documented resolution preserves lessons. A configuration change associated with an incident is a hypothesis, not proof of its cause. Seeding uses stable IDs and `MERGE` edges, leaving existing node contents intact.

## Important query patterns

```cypher
MATCH (n {id: $id}) RETURN n LIMIT 1
MATCH (s {id: $s}), (t {id: $t})
MERGE (s)-[r:SUPPORTS]->(t) RETURN s.id, t.id, type(r)
MATCH p=(s {id: $s})-[*1..4]-(t {id: $t})
RETURN [n IN nodes(p) | n.id], [r IN relationships(p) | type(r)] LIMIT 12
```

Retrieval tokenizes the request into at most 16 useful terms and selects at most 12 matching Memory/Evidence/Entity/Decision anchors. It traverses real semantic relationships up to three hops, with at most 80 returned paths, 40 context nodes and 24 exposed paths. Session/run hubs are excluded from semantic expansion. Every returned path is obtained from `nodes(p)` and `relationships(p)` in FalkorDB. Paths are undirected traversals; the graph's returned edges retain their actual source/target direction. Paths whose nodes were truncated out of the returned context are removed.

Neighborhoods are bounded to three hops and 150 nodes; general paths to four hops and 12 results. Query execution has a 5-second server timeout and socket timeouts. These are small-workspace demo limits, not a claim of production-scale indexing or identity authorization. Workspace separation is storage isolation, not authentication: deploy behind authentication before exposing publicly.

Persistence depends on the Compose named volume and Redis append-only file. Restart testing must compare actual nodes and paths before and after restarting the database; an application process restart alone only verifies client reconnection.
