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
| Blog | ✅ Published | https://aayushkumbharkar.github.io/Contentmesh/ (HTTP 200 verified; Pages build succeeded) |
| Live demo URL | ⏳ Ready, needs Render sign-in | `render.yaml` + `deploy/single-container/` verified locally. Apply the Blueprint (see `docs/deployment.md`) |
| Submission form | ⏳ | `SUBMISSION_FORM.md`. Paste the YouTube URL; leave the live URL empty unless a deployment is verified |

## Remaining manual actions

1. Upload `submission/contextmesh-demo-voiced.mp4` (voiced version of `submission/video/contextmesh-technical-demo.mp4`) to YouTube (Unlisted or Public) using the copy in `submission/video/SHARE_COPY.md`. Add the URL to the form.
2. Live deployment: open https://dashboard.render.com/blueprint/new?repo=https://github.com/aayushkumbharkar/Contentmesh, sign in, authorize GitHub, and apply the free Blueprint. Verify `/api/health` returns `{"status":"ok","database":"FalkorDB"}` before submitting the URL.
