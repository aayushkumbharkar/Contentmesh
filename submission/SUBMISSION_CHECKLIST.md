# Submission checklist — actual status (18 Oct 2026, 23:15 IST)

| Item | Status | Evidence / next action |
| --- | --- | --- |
| Public repository | ✅ Done | https://github.com/aayushkumbharkar/Contentmesh, `main` |
| Backend tests vs real FalkorDB | ✅ 17 passed | `FALKORDB_PORT=6380 .venv/Scripts/python -m pytest tests -q` |
| End-to-end + container restart | ✅ Passed | `scripts/verify_demo.py --restart`, after fixing nginx stale-DNS 502s on backend restart |
| Frontend production build | ✅ Passed | `npm run build` (bundle-size warning only) |
| Dependency audit | ✅ Clean | `npm audit --omit=dev`: 0 vulnerabilities; `pip-audit -r backend/requirements.txt`: none known |
| Secret scan of tracked files | ✅ Clean | Pattern scan for Groq, OpenAI, GitHub and AWS keys and private keys; `.env` is not present or tracked |
| Technical demo video | ✅ Uploaded (Unlisted) | https://youtu.be/B06nzWsC9nk (voiced cut) |
| Launch trailer | ✅ Built (FFmpeg, not Brag) | `submission/video/contextmesh-trailer.mp4` (20.5 s). Brag install was blocked |
| Thumbnail | ✅ | `submission/video/thumbnail.png` |
| Storyboard / script | ✅ | `DEMO_VIDEO_STORYBOARD.md`, `DEMO_SCRIPT.md` |
| Blog | ✅ Published | https://aayushkumbharkar.github.io/Contentmesh/ (HTTP 200 verified; Pages build succeeded) |
| Live demo URL | ✅ Live | https://contextmesh-e25o.onrender.com: health OK, verify_demo passed live (22 paths) |
| Submission form | ✅ Ready | `SUBMISSION_FORM.md`: all URLs filled and verified |

## Remaining manual actions

Paste the answers from `SUBMISSION_FORM.md` into the Graph Hacks form and submit before 23:59 IST.
