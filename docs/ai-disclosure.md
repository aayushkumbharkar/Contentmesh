# AI coding assistance disclosure

ContextMesh was implemented with OpenAI Codex assistance. The lead Codex agent defined shared contracts, integrated FastAPI and the optional provider adapter, configured deployment, reviewed specialist work, and ran verification. Three native Codex sub-agents implemented isolated frontend, FalkorDB, and memory/orchestration modules; the graph and orchestration specialists also added focused tests. These coding assistants are distinct from the four runtime agents shipped in ContextMesh.

AI-generated code was integrated and exercised against a real local FalkorDB instance. Test and audit results are recorded in verification.md. The AcmeShop data is synthetic. Deterministic runtime execution uses no LLM calls; optional Groq synthesis requires separately configured credentials. No paid-provider execution or public deployment is claimed unless explicitly recorded in verification.md.

Installed skill catalog and the preferred caveman skill were inspected for concise communication. No external skill repositories, lifecycle hooks, or proxy code were installed. Existing project instructions guided the modular workflow.
