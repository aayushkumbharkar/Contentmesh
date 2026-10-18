# Genuine application recording storyboard

Target duration: 75 seconds after startup; final MP4 includes a short initial loading/setup period. The script asserts the exported duration is between 60 and 90 seconds. Capture: 1600 × 1000, H.264 MP4, real browser frames with explanatory captions, no synthetic application states or voiceover.

| Approximate time | Real application action | Evidence shown |
| --- | --- | --- |
| 0–6 s | Open seeded AcmeShop graph and a new session | Actual FalkorDB nodes and relationships; synthetic label |
| 6–14 s | Enter incident note containing cart-video-729 | Unique observation sent through the UI |
| 14–25 s | Run investigation; show timeline | Four completed runtime stages with persisted handoffs |
| 25–33 s | Create separate session and enter recall question | New session identity |
| 33–44 s | Run recall | Earlier observation, recorded owner, TTL change and earlier lesson |
| 44–55 s | Expand supporting evidence and paths | Real returned evidence and relationship sequences |
| 55–65 s | Switch to list, search Redis, inspect node | Keyboard-accessible alternative and real properties |
| 65–75 s | Reload page and inspect restored result | Earlier marker remains available after refresh |

The executable source is `scripts/record_demo.py`. It asserts four timeline entries, the unique observation, Maya Chen, visible paths, and retained observation after reload. MP4 conversion preserves recorded browser frames. The script uses its own Chrome instance, not a personal signed-in browser session.

Restart persistence is tested separately by `scripts/verify_demo.py --restart`; a browser refresh alone is not claimed as proof of server-restart persistence.

## Final edited cut — `submission/video/contextmesh-technical-demo.mp4` (89.3 s)

Built by `scripts/build_videos.py` from the raw capture `submission/contextmesh-demo.mp4` (100.8 s). The edit removes about 12 s of browser start-up at the beginning, and about 7 s of the post-refresh loading state (the empty graph shown while saved data is fetched again). No application frames are altered. Times are approximate, ±3 s.

| Edited time | Shown | Burned-in caption |
| --- | --- | --- |
| 0–3.5 s | Problem card | "Agents lose context between tasks and sessions." |
| 3.5–15 s | Seeded AcmeShop graph (FalkorDB nodes/edges) | "ContextMesh \| Real FalkorDB memory · Synthetic AcmeShop incident" |
| 15–28 s | Session 1 incident note with unique observation | "Session 1: record an incident with a unique observation — cart-video-729" |
| 28–41 s | Run; agent-handoff timeline | "Researcher → Planner → Executor → Verifier \| Handoffs saved in FalkorDB" |
| 41–52 s | New session, recall question | "Session 2: ask for earlier context in a separate session" |
| 52–63 s | Recall answer | "Retrieved earlier note + Redis TTL change + Maya Chen + INC-104 lesson" |
| 63–69 s | Supporting evidence and real paths | "Supporting evidence and paths are queried records — causality remains unproven" |
| 69–78 s | List view, Redis TTL node properties | "Accessible list view: inspect actual node properties and relationships" |
| 78–85 s | After page reload | "Refresh complete: the saved session and evidence are still available" |
| 85–89.3 s | Closing card | "Disconnected agent context → persistent, connected memory" |

Launch trailer (20.5 s, `submission/video/contextmesh-trailer.mp4`): title (4 s) → graph view (4 s) → agent-handoff panel (4 s) → evidence paths (4 s) → close (4.5 s). See `submission/video/SHARE_COPY.md`.
