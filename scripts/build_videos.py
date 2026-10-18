"""Build the launch trailer and technical demo from the genuine browser capture.

Input: submission/contextmesh-demo.mp4 (produced by scripts/record_demo.py against
the running Docker stack with real FalkorDB). Output: submission/video/.
Requires ffmpeg/ffprobe on PATH. Fonts: Windows Segoe UI.
Run: .venv/Scripts/python scripts/build_videos.py
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "submission" / "contextmesh-demo.mp4"
OUT = ROOT / "submission" / "video"
WORK = OUT / "work"
BOLD = "C\\:/Windows/Fonts/segoeuib.ttf"
REG = "C\\:/Windows/Fonts/segoeui.ttf"
BG = "0x0b1220"
ENC = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-preset", "medium", "-crf", "20", "-an"]


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def text(name, value):
    path = WORK / f"{name}.txt"
    path.write_text(value, encoding="utf-8")
    return path.as_posix().replace(":", "\\:")


def draw(name, value, size, y, font=REG, color="white"):
    return (f"drawtext=fontfile='{font}':textfile='{text(name, value)}':fontsize={size}:"
            f"fontcolor={color}:x=(w-text_w)/2:y={y}")


def fades(duration):
    return f"fade=t=in:st=0:d=0.5,fade=t=out:st={duration - 0.5}:d=0.5"


def card(name, duration, lines):
    filters = [draw(f"{name}{i}", *line) for i, line in enumerate(lines)]
    run(["-f", "lavfi", "-i", f"color=c={BG}:s=1920x1080:d={duration}:r=30",
         "-vf", ",".join(filters + [fades(duration)]), *ENC, str(WORK / f"{name}.mp4")])
    return WORK / f"{name}.mp4"


def segment(name, start, duration, title=None, crop=False):
    # crop=True: 16:9 crop of the UI (drops burned-in captions) for the trailer.
    vf = ["crop=1600:900:0:20,scale=1920:1080" if crop
          else f"scale=1728:1080,pad=1920:1080:96:0:color={BG}"]
    if title:
        vf.append(f"drawbox=x=0:y=880:w=iw:h=200:color={BG}@0.86:t=fill")
        vf.append(draw(name, title, 54, 940, BOLD, "0xd7fff7"))
    vf.append(fades(duration))
    run(["-ss", str(start), "-t", str(duration), "-i", str(SRC), "-vf", ",".join(vf),
         *ENC, str(WORK / f"{name}.mp4")])
    return WORK / f"{name}.mp4"


def assemble(name, clips):
    listing = WORK / f"{name}.txt"
    listing.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    silent = WORK / f"{name}-silent.mp4"
    run(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(silent)])
    duration = probe(silent)
    # Soft synthesized ambient pad (no narration); faded at both ends.
    pad = ("aevalsrc='0.05*sin(2*PI*110*t)+0.035*sin(2*PI*164.81*t)"
           "+0.025*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.08*t))':s=48000:c=stereo")
    out = OUT / f"{name}.mp4"
    run(["-i", str(silent), "-f", "lavfi", "-t", str(duration), "-i", pad,
         "-af", f"afade=t=in:d=1.5,afade=t=out:st={duration - 2}:d=2",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
         "-movflags", "+faststart", str(out)])
    return out


def probe(path):
    data = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "json", str(path)], check=True, capture_output=True, text=True)
    return float(json.loads(data.stdout)["format"]["duration"])


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    trailer = assemble("contextmesh-trailer", [
        card("t-open", 4, [("ContextMesh", 120, 400, BOLD),
                           ("Persistent, connected, explainable memory for AI agents", 46, 560, REG, "0x9fb3c8")]),
        segment("t-graph", 22, 4, "One shared memory graph in FalkorDB", crop=True),
        segment("t-handoff", 44, 4, "Researcher → Planner → Executor → Verifier", crop=True),
        segment("t-evidence", 70, 4, "Answers expose the real graph paths behind them", crop=True),
        card("t-close", 4.5, [("ContextMesh", 96, 380, BOLD),
                              ("Context that survives sessions, restarts and handoffs", 44, 520, REG, "0x9fb3c8"),
                              ("Built on FalkorDB  ·  github.com/aayushkumbharkar/Contentmesh", 34, 640, REG, "0x42cbb9")]),
    ])
    demo = assemble("contextmesh-technical-demo", [
        card("d-problem", 3.5, [("Agents lose context between tasks and sessions.", 58, 420, BOLD),
                                ("ContextMesh persists sessions, evidence and handoffs in FalkorDB.", 40, 540, REG, "0x9fb3c8")]),
        segment("d-main", 12, 74.5),        # seed, session 1, agent flow, session 2 recall, evidence, list view
        segment("d-reload", 93.5, 7.3),    # after page refresh: saved session and evidence restored
        card("d-close", 4, [("ContextMesh", 96, 360, BOLD),
                            ("Disconnected agent context → persistent, connected memory", 44, 500, REG, "0x9fb3c8"),
                            ("Real browser capture · synthetic AcmeShop data · FalkorDB v4.14.11", 32, 620, REG, "0x42cbb9")]),
    ])
    run(["-ss", "6", "-i", str(trailer), "-frames:v", "1", "-vf", "scale=1280:720", str(OUT / "thumbnail.png")])
    print(json.dumps({p.name: round(probe(p), 2) for p in (trailer, demo)}))


if __name__ == "__main__":
    main()
