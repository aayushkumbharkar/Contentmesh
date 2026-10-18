# 90-second demo storyboard

0–12s: Open localhost:5173. Show AcmeShop synthetic label. Load synthetic demo; orbit the actual graph and select Checkout API. Show OWNED_BY Maya Chen and Redis change evidence.

12–32s: Choose Record an incident, add a distinctive note such as “Checkout API session-expired errors after release 2.4; observation CART-729.” Run investigation. Show persisted Researcher, Planner, Executor, Verifier handoffs.

32–48s: Open Memory and inspect the note and provenance. Show that the answer calls the TTL change a candidate, not a proven cause.

48–70s: Create New session. Choose Recall earlier context. Run; point out the previous CART-729 note, owner Maya Chen, TTL change 3600→60, and previous lesson to restore TTL and add regression checks.

70–82s: Expand supporting evidence and graph paths. Inspect a real Redis change / Checkout API / Maya Chen path. Switch to List to demonstrate accessible navigation.

82–90s: Refresh the page and reopen the session/run. State that FalkorDB AOF persistence was separately verified after container restart. Do not claim a live restart happened in the video unless shown.

Use deterministic demo mode for repeatability. No paid API key needed. Do not describe synthetic incident evidence as a real AcmeShop outage.
