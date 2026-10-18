"""Record the real running application; requires playwright, Chrome and ffmpeg.

Run: .venv/Scripts/python scripts/record_demo.py
The isolated browser uses no personal profile. No graph data is deleted.
"""
import json
import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission"


def main():
    OUTPUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True,
                                    args=["--enable-unsafe-swiftshader"])
        context = browser.new_context(viewport={"width": 1600, "height": 1000},
                                      record_video_dir=str(OUTPUT / "recordings"),
                                      record_video_size={"width": 1600, "height": 1000})
        page = context.new_page()
        page.goto("http://localhost:5173", wait_until="networkidle")
        page.get_by_role("button", name="Load synthetic demo").click()
        expect(page.get_by_role("button", name="Load synthetic demo")).to_be_enabled(timeout=30000)
        page.get_by_role("button", name="+ New session", exact=True).click()
        expect(page.get_by_role("button", name="+ New session", exact=True)).to_be_enabled()
        start = time.monotonic()

        def caption(message):
            page.evaluate("""message => {
              let el = document.getElementById('recording-caption');
              if (!el) { el = document.createElement('div'); el.id='recording-caption'; document.body.appendChild(el); }
              el.textContent=message;
              el.style.cssText='position:fixed;bottom:15px;left:50%;transform:translateX(-50%);z-index:99999;background:#0c182bef;color:#d7fff7;padding:14px 26px;border:1px solid #42cbb9;border-radius:12px;font:600 19px system-ui;max-width:1450px;text-align:center;pointer-events:none';
            }""", message)

        def until(seconds):
            page.wait_for_timeout(max(0, seconds - (time.monotonic() - start)) * 1000)

        caption("ContextMesh | Real FalkorDB memory · Synthetic AcmeShop incident")
        until(6)
        page.get_by_role("textbox", name="Incident note or question").fill(
            "Checkout API errors increased after release 2.4. Redis keys expire mid-purchase. Unique observation: cart-video-729. Investigate the recorded owner and earlier resolution.")
        page.get_by_role("textbox", name="Incident note or question").scroll_into_view_if_needed()
        caption("Session 1: record an incident with a unique observation — cart-video-729")
        until(14)
        page.get_by_role("button", name="Run investigation").click()
        expect(page.locator(".timeline li")).to_have_count(4, timeout=30000)
        page.locator(".timeline").scroll_into_view_if_needed()
        caption("Researcher → Planner → Executor → Verifier | Handoffs saved in FalkorDB")
        until(25)
        page.get_by_role("button", name="+ New session", exact=True).click()
        expect(page.get_by_role("button", name="+ New session", exact=True)).to_be_enabled()
        page.get_by_role("textbox", name="Incident note or question").fill(
            "Which previous change could explain the Checkout API incident, who owns it, and what was learned earlier? Recover cart-video-729.")
        page.get_by_role("textbox", name="Incident note or question").scroll_into_view_if_needed()
        caption("Session 2: ask for earlier context in a separate session")
        until(33)
        page.get_by_role("button", name="Run investigation").click()
        expect(page.locator(".answer")).to_contain_text("cart-video-729", timeout=30000)
        expect(page.locator(".answer")).to_contain_text("Maya Chen")
        page.locator(".answer").scroll_into_view_if_needed()
        caption("Retrieved earlier note + Redis TTL change + Maya Chen + INC-104 lesson")
        until(44)
        page.locator(".answer summary").click()
        page.locator(".path").first.scroll_into_view_if_needed()
        expect(page.locator(".path").first).to_be_visible()
        caption("Supporting evidence and paths are queried records — causality remains unproven")
        until(55)
        page.get_by_role("button", name="List", exact=True).click()
        page.get_by_role("textbox", name="Search graph nodes").fill("Redis")
        page.locator(".node-list button").filter(has_text="Redis TTL configuration change").click()
        page.locator(".graph-panel").scroll_into_view_if_needed()
        caption("Accessible list view: inspect actual node properties and relationships")
        until(65)
        page.reload(wait_until="networkidle")
        expect(page.locator(".answer")).to_contain_text("cart-video-729", timeout=30000)
        page.locator(".answer").scroll_into_view_if_needed()
        caption("Refresh complete: the saved session and evidence are still available")
        until(75)
        page.screenshot(path=str(OUTPUT / "recordings" / "final-frame.png"))
        video = page.video
        context.close()
        raw = Path(video.path())
        browser.close()
    target = OUTPUT / "contextmesh-demo.mp4"
    subprocess.run([shutil.which("ffmpeg") or "ffmpeg", "-y", "-i", str(raw),
                    "-vf", "scale=1600:1000", "-c:v", "libx264", "-preset", "fast",
                    "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(target)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    probe = subprocess.check_output([shutil.which("ffprobe") or "ffprobe", "-v", "error",
                                    "-show_entries", "format=duration,size", "-of", "json", str(target)], text=True)
    metadata = json.loads(probe)
    assert 60 <= float(metadata["format"]["duration"]) <= 90, metadata
    print(json.dumps({"video": str(target), **metadata}, indent=2))


if __name__ == "__main__":
    main()
