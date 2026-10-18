"""Add a neural-TTS voice-over to the ContextMesh technical demo video.

Reproducible pipeline (footage is never re-encoded; video stream is copied):
  1. Synthesize each narration segment with edge-tts (one voice throughout).
  2. Measure each clip with ffprobe and fail if it overruns its scene window.
  3. Place each clip at its start time -> voiceover-only WAV (48 kHz).
  4. Duck the existing ambient pad, mix with the voice, two-pass loudnorm to -16 LUFS.
  5. Mux with the original video (stream copy), AAC 192k, +faststart.
  6. Write the narration text and an SRT using the measured start/end times.

Usage:  .venv/Scripts/python scripts/add_voiceover.py
Requires: edge-tts (pip), ffmpeg/ffprobe on PATH, network access for edge-tts.
"""
from __future__ import annotations

import asyncio
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "submission/video/contextmesh-technical-demo.mp4"
OUT_VIDEO = ROOT / "submission/contextmesh-demo-voiced.mp4"
OUT_TXT = ROOT / "submission/video/contextmesh-narration.txt"
OUT_WAV = ROOT / "submission/video/contextmesh-voiceover.wav"
OUT_SRT = ROOT / "submission/video/contextmesh-demo.srt"

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "+5%"
PAD_GAIN_DB = -9.0
TARGET_LUFS = -16.0
MIN_GAP = 0.3

# (start seconds, latest allowed end seconds, text) aligned to on-screen scenes.
SEGMENTS: list[tuple[float, float, str]] = [
    (0.15, 3.5,
     "Agents lose context between sessions."),
    (3.8, 14.8,
     "ContextMesh gives agents graph-native memory in FalkorDB. "
     "This seeded graph models a synthetic AcmeShop incident, "
     "with its services, owners and changes."),
    (15.5, 27.8,
     "In session one, a user records an incident note with a unique observation, "
     "cart-video-729, and runs an investigation. The note is stored as evidence."),
    (28.2, 40.6,
     "Agents hand off through the graph: the Researcher gathers facts, the Planner plans, "
     "the Executor records an evidence-backed decision, and the Verifier re-checks "
     "paths for gaps or contradictions."),
    (40.5, 47.6,
     "Now a separate, new session asks what earlier change could explain the incident, "
     "who owns it, and what was learned before."),
    (48.0, 56.9,
     "It recalls the cart-video-729 note, a Redis TTL change, "
     "owner Maya Chen and the INC-104 lesson."),
    (57.3, 65.6,
     "Evidence and the actual graph paths come straight from FalkorDB. "
     "They are investigation leads, not proof of cause."),
    (66.0, 77.6,
     "The accessible list view shows the same data without 3D. "
     "Here we inspect the Redis TTL configuration change, with its properties and relationships."),
    (77.8, 82.9,
     "After a page refresh, the saved session and its evidence are still there."),
    (83.2, 88.5,
     "ContextMesh: persistent memory, coordinated agents, explainable evidence."),
]


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)]).stdout
    return float(out.strip())


async def synth(text: str, dest: Path) -> None:
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(dest))


def srt_ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    total = duration(SRC)
    tmp = Path(tempfile.mkdtemp(prefix="cm_vo_"))
    clips: list[tuple[float, float, str, Path]] = []
    errors: list[str] = []
    for i, (start, limit, text) in enumerate(SEGMENTS):
        mp3 = tmp / f"seg{i:02d}.mp3"
        wav = tmp / f"seg{i:02d}.wav"
        asyncio.run(synth(text, mp3))
        # Trim edge-tts leading/trailing silence so placement is exact.
        run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-af",
             "silenceremove=start_periods=1:start_threshold=-50dB,"
             "areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
             "-ar", "48000", "-ac", "1", str(wav)])
        d = duration(wav)
        end = start + d
        clips.append((start, end, text, wav))
        print(f"seg{i:02d} {start:6.2f} -> {end:6.2f} ({d:5.2f}s, limit {limit:5.2f})")
        if end > limit:
            errors.append(f"seg{i:02d} overruns by {end - limit:.2f}s")
    for (s0, e0, *_), (s1, *_rest) in zip(clips, clips[1:]):
        if s1 - e0 < MIN_GAP - 1e-6:
            errors.append(f"gap before {s1:.2f} is {s1 - e0:.2f}s")
    if clips[-1][1] > min(88.5, total):
        errors.append("last segment ends too late")
    if errors:
        print("TIMING ERRORS:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 1

    # Voice-over only track, full video length, 48 kHz.
    inputs: list[str] = []
    chains: list[str] = []
    for i, (start, _e, _t, wav) in enumerate(clips):
        inputs += ["-i", str(wav)]
        ms = int(round(start * 1000))
        chains.append(f"[{i}:a]adelay={ms}:all=1[d{i}]")
    mix_in = "".join(f"[d{i}]" for i in range(len(clips)))
    fc = ";".join(chains) + f";{mix_in}amix=inputs={len(clips)}:normalize=0:dropout_transition=0," \
        f"apad,atrim=0:{total:.3f},aformat=sample_rates=48000:channel_layouts=mono[v]"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]",
         "-c:a", "pcm_s16le", str(OUT_WAV)])

    # Mix: ducked pad + voice (voice boosted toward speech level before loudnorm).
    pre = (f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={PAD_GAIN_DB}dB[pad];"
           f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo[vo];"
           f"[pad][vo]amix=inputs=2:normalize=0:duration=first")
    measure = run(["ffmpeg", "-hide_banner", "-y", "-i", str(SRC), "-i", str(OUT_WAV),
                   "-filter_complex", pre + f",loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:print_format=json",
                   "-f", "null", "-"]).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", measure, re.S).group(0))
    ln = (f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:measured_I={m['input_i']}:"
          f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-i", str(OUT_WAV),
         "-filter_complex", pre + f",{ln},aresample=48000[a]",
         "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{total:.3f}", "-movflags", "+faststart", str(OUT_VIDEO)])

    OUT_TXT.write_text(
        f"ContextMesh technical demo narration\nVoice: {VOICE} (edge-tts, rate {RATE})\n\n"
        + "\n".join(f"[{s:05.2f}-{e:05.2f}] {t}" for s, e, t, _ in clips) + "\n",
        encoding="utf-8")
    OUT_SRT.write_text(
        "\n".join(f"{i + 1}\n{srt_ts(s)} --> {srt_ts(e)}\n{t}\n" for i, (s, e, t, _) in enumerate(clips)),
        encoding="utf-8")
    print(f"wrote {OUT_VIDEO}\n      {OUT_WAV}\n      {OUT_SRT}\n      {OUT_TXT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
