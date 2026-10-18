# Shared implementation contracts

All paths relative to this directory. Lead owns backend/app/main.py, models.py, provider.py, requirements, deployment, tests/, README. Graph specialist owns backend/app/graph/ and docs/graph.md. Coordination specialist owns backend/app/orchestration/ and backend/app/memory/. Frontend specialist owns frontend/.

## Graph interface
`from app.graph import GraphStore` constructed without args using FALKORDB_HOST (localhost), FALKORDB_PORT (6379), FALKORDB_PASSWORD (optional).
Methods: health()->bool; seed(workspace_id)->dict; put_node(workspace_id, kind, properties)->dict; link(workspace_id, source_id, target_id, relationship)->dict; get_node(workspace_id,id)->dict|None; nodes(workspace_id,kind=None,limit=200)->list; graph(workspace_id,limit=300)->dict; retrieve(workspace_id,query,limit=20)->dict; paths(workspace_id,source_id,target_id,max_hops=4)->list; neighborhood(workspace_id,node_id,hops=2)->dict.
Node shape: {id,kind,label, ...properties}; edge: {id,source,target,type}; graph: {nodes:[],edges:[]}; retrieve: {nodes:[],edges:[],paths:[]} with paths {nodes:[node IDs],edges:[relationship names]}. Properties flat scalar values; structured data stored JSON strings. put_node generates UUID if absent, upserts by id. Valid workspace IDs: lowercase alphanumeric and hyphen, 1-64 chars. One graph per workspace. Fixed allowlists for kinds and relationships; no arbitrary Cypher API. Kinds: Workspace Session Memory Evidence Entity Task Decision Agent AgentRun Run. Relations: HAS_SESSION MENTIONS RELATES_TO SUPPORTS DEPENDS_ON GENERATED HANDOFF_TO HAS_MEMORY HAS_RUN OWNED_BY AFFECTS RESOLVED_BY NEXT.
Seed AcmeShop synthetic connected scenario idempotently (workspace acmeshop), including release 2.4, Redis TTL configuration change, Checkout API, owner Maya Chen, previous incident and resolution. Every returned path must come from actual graph queries.

## Orchestration
`from app.orchestration import run_workflow`
`run_workflow(store, workspace_id, session_id, text, provider=None)->dict`
provider callable optional `provider(context:dict)->dict` for optional bounded synthesis; deterministic behavior default. Validate session exists and belongs to selected graph. Persist Memory for submitted note, Run, four AgentRun nodes, Tasks, Decision and handoffs. Downstream stages read stored predecessor output. Final dict: {id,session_id,status,answer,evidence:[nodes],paths:[path],steps:[{id,agent,status,summary,input_ids:[],output_ids:[]}],usage:dict}. Store complete result JSON on Run.result. Distinguish evidence from hypotheses; no unsupported causal certainty.

## HTTP contract
All routes prefixed /api. GET /health {status,database}; POST /workspaces/{w}/seed graph; GET /workspaces/{w}/graph graph; GET /workspaces/{w}/sessions {sessions:[nodes]}; POST same body {title:string} returns Session node; GET /workspaces/{w}/memories {memories:[nodes]}; PATCH /workspaces/{w}/memories/{id} body {text:string} node; POST /workspaces/{w}/sessions/{s}/runs body {text:string} returns workflow result synchronously; GET /workspaces/{w}/runs {runs:[decoded results]}; GET /workspaces/{w}/nodes/{id}/neighborhood?hops=2 graph; GET /workspaces/{w}/paths?source=&target=&max_hops=4 {paths:[]}.
Errors JSON {detail:string}; missing 404, validation 422, database unavailable 503. frontend uses relative /api through Vite proxy/nginx. Default workspace acmeshop. Seed button explicit. No mocked visual data.

## Acceptance and task board
- [ ] Real FalkorDB seed/read/path/isolation
- [ ] Persisted four-stage workflow and separate-session memory
- [ ] Typed frontend with real Three.js graph and accessible list
- [ ] Bounded optional Groq adapter with usage accounting
- [ ] Docker Compose and repeatable tests, restart proof
- [ ] Docs, demo storyboard, disclosure
