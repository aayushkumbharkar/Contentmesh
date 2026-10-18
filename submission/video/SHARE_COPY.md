# Video files and share copy

| File | Duration | Format | Contents |
| --- | --- | --- | --- |
| `../contextmesh-demo-voiced.mp4` (**upload this one**) | 89.3 s | 1920×1080 H.264 + AAC, −16 LUFS | Technical demo with a neural voice-over (edge-tts `en-US-AndrewMultilingualNeural`). Footage is a stream copy of the technical demo. Subtitles: `contextmesh-demo.srt`. Built by `scripts/add_voiceover.py` |
| `contextmesh-technical-demo.mp4` | 89.3 s | 1920×1080 H.264 + AAC | Problem card → genuine browser capture (seed, session 1, four-stage run, session 2 recall, evidence paths, list view, refresh) → closing card |
| `contextmesh-trailer.mp4` | 20.5 s | 1920×1080 H.264 + AAC | Title → real graph view → real agent-handoff panel → real evidence paths → closing card |
| `thumbnail.png` | — | 1280×720 | Frame from the trailer at 6 s (real graph view) |

Source footage: `submission/contextmesh-demo.mp4`, a genuine headless-Chrome capture produced by `scripts/record_demo.py` against the Docker stack with real FalkorDB. The edit is built by `scripts/build_videos.py`. The audio is a soft synthesized ambient bed; there is no narration. All UI footage is unmodified application output plus captions. AcmeShop data is synthetic.

**Brag:** the requested Brag / Hyperframes workflow was not used. Installing it (`npx skills add https://github.com/latent-spaces/brag --skill brag`) was blocked by this session's permission policy, and plugin commands are not available to the agent. The trailer was made with FFmpeg from real footage instead. To regenerate it with Brag, run `/plugin marketplace add latent-spaces/brag`, `/plugin install brag@brag`, then `/brag --full` in an interactive Claude Code session.

## YouTube

**Title:** ContextMesh — persistent, connected, explainable memory for AI agents (FalkorDB · Graph Hacks)

**Description:**

ContextMesh gives a team of AI agents one shared, persistent memory graph in FalkorDB. In this real capture, a Researcher → Planner → Executor → Verifier workflow investigates a synthetic AcmeShop checkout incident. A second session then recalls the earlier observation, the service owner, a Redis TTL change, and a previous incident's lesson, each backed by actual graph paths returned from FalkorDB.

- Cross-session recall, and persistence across a refresh and a container restart (tested)
- Agent handoffs stored as graph records that the next stage must read
- Every answer exposes its evidence and real multi-hop paths; causality is never asserted
- One graph per workspace for isolation

Source: https://github.com/aayushkumbharkar/Contentmesh
All data is synthetic. Built for Graph Hacks: Context for AI Agents by FalkorDB.

**Short share copy:** Agents forget. ContextMesh doesn't. Four agents share a persistent FalkorDB memory graph, and every answer shows the real graph paths behind it. https://github.com/aayushkumbharkar/Contentmesh #GraphHacks #FalkorDB
