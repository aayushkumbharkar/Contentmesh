# ContextMesh demonstration script

This is a genuine browser capture of the local application backed by FalkorDB. All AcmeShop data is synthetic. Captions explain the actions; they do not replace application results. The capture has no narration audio.

## Recording

Start the application with `docker compose up --build -d`. With Chrome and FFmpeg available:

```powershell
.\.venv\Scripts\python -m pip install playwright
.\.venv\Scripts\python -m playwright install ffmpeg
.\.venv\Scripts\python scripts/record_demo.py
```

The script uses a separate browser profile, writes `submission/contextmesh-demo.mp4`, and checks its duration with ffprobe. It creates two sessions and does not delete existing graph data. Keep the application running without restarting services during capture.

## Optional spoken narration

“ContextMesh gives four agents a shared memory in FalkorDB. This is AcmeShop, a synthetic incident scenario. The graph contains a Checkout API, a release, a Redis configuration change, an owner, and an earlier incident resolution.

“In the first session, I record checkout errors and the unique observation cart-video-729. The Researcher retrieves context, the Planner creates dependent checks, the Executor persists an investigation decision, and the Verifier checks recorded evidence. Their handoffs are saved in the graph.

“Now I create a separate session and ask what happened earlier. The result retrieves the saved observation, Maya Chen's ownership, the Redis TTL change, and the previous lesson. These are investigation candidates, not proof of causality.

“I can inspect the supporting facts and actual queried paths. A list view offers another way to explore nodes and relationships. After refreshing, the saved session and evidence remain available. The demo runs without an LLM key; FalkorDB is always the persistent memory.”

Publication URLs belong in `SUBMISSION_FORM.md`; a local video file is not a YouTube upload.

## Building the final videos

After `scripts/record_demo.py` has produced `submission/contextmesh-demo.mp4`:

```powershell
.\.venv\Scripts\python scripts/build_videos.py
```

This writes `submission/video/contextmesh-technical-demo.mp4` (89.3 s), `contextmesh-trailer.mp4` (20.5 s), and `thumbnail.png`. Container-restart persistence is shown separately by `scripts/verify_demo.py --restart`. It passed on 18 Oct 2026, with 22 paths and the run recovered after the FalkorDB and backend restart. It is not part of the browser capture.
