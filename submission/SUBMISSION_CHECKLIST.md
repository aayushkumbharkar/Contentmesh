# Submission checklist — actual status (18 Oct 2026, 22:40 IST)

| Item | Status | Evidence / next action |
| --- | --- | --- |
| Public repository | ✅ Done | https://github.com/aayushkumbharkar/Contentmesh, `main` |
| Backend tests vs real FalkorDB | ✅ 17 passed | `FALKORDB_PORT=6380 .venv/Scripts/python -m pytest tests -q` |
| End-to-end + container restart | ✅ Passed | `scripts/verify_demo.py --restart`, after fixing nginx stale-DNS 502s on backend restart |
| Frontend production build | ✅ Passed | `npm run build` (bundle-size warning only) |
| Dependency audit | ✅ Clean | `npm audit --omit=dev`: 0 vulnerabilities; `pip-audit -r backend/requirements.txt`: none known |
| Secret scan of tracked files | ✅ Clean | Pattern scan for Groq, OpenAI, GitHub and AWS keys and private keys; `.env` is not present or tracked |
| Technical demo video | ✅ Built, ⏳ upload | `submission/video/contextmesh-technical-demo.mp4` (89.3 s). Upload to YouTube manually |
| Launch trailer | ✅ Built (FFmpeg, not Brag) | `submission/video/contextmesh-trailer.mp4` (20.5 s). Brag install was blocked |
| Thumbnail | ✅ | `submission/video/thumbnail.png` |
| Storyboard / script | ✅ | `DEMO_VIDEO_STORYBOARD.md`, `DEMO_SCRIPT.md` |
| Blog | ⚠️ Check rebuild | https://aayushkumbharkar.github.io/ContextMesh/ failed to build (non-UTF-8 byte); fixed and pushed. Confirm the page loads before submitting |
| Live demo URL | ❌ Blocked | Railway trial expired, GCP billing disabled, no Render credential. See `docs/deployment.md` |
| Submission form | ⏳ | `SUBMISSION_FORM.md`. Paste the YouTube URL; leave the live URL empty unless a deployment is verified |

## Remaining manual actions

1. Upload `submission/video/contextmesh-technical-demo.mp4` to YouTube (Unlisted or Public) using the copy in `submission/video/SHARE_COPY.md`. Add the URL to the form.
2. Open https://aayushkumbharkar.github.io/ContextMesh/ and confirm the article renders.
3. Optional live deployment: select a Railway plan, or create Render and FalkorDB Cloud accounts, then follow `docs/deployment.md`. Verify `/api/health` returns `{"status":"ok","database":"FalkorDB"}` before submitting the URL.
