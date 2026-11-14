"""GSET Dec 2024 Paper-1 Gujarati explainer video: content JSON -> TTS -> Manim clips -> MP4.

    python build.py                     # full 1080p render (resumable)
    python build.py --only 1-3 -q m     # quick 720p preview of Q1-3
    python build.py --engine elevenlabs --voice <voice_id>
"""
import os, sys, json, glob, shutil, argparse, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tts  # noqa: E402

SCENES = os.path.join(HERE, "scenes.py")
CLASS = {"intro": "IntroScene", "section": "SectionScene", "passage": "PassageScene",
         "question": "QuestionScene", "outro": "OutroScene"}
QFLAG = {"l": "-ql", "m": "-qm", "h": "-qh"}
QRES = {"l": "854,480", "m": "1280,720", "h": "1920,1080"}
SAY_LABEL = {"A": "એ", "B": "બી", "C": "સી", "D": "ડી"}


def load_content():
    qs, meta = [], {}
    for p in sorted(glob.glob(os.path.join(HERE, "content", "*.json"))):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        qs += d.pop("questions", [])
        for k, v in d.items():
            if isinstance(v, list):
                meta.setdefault(k, []).extend(v)
            else:
                meta.setdefault(k, v)
    qs.sort(key=lambda q: q["n"])
    return meta, qs


def section_of(meta, n):
    return next(s for s in meta["sections"] if s["from"] <= n <= s["to"])


def build_specs(meta, qs, only):
    total = 50
    specs = []
    if not only:
        specs.append({"kind": "intro", "name": "c000_intro", "beats": [{"say": meta["intro_say"]}]})
    for q in qs:
        n = q["n"]
        if only and not (only[0] <= n <= only[1]):
            continue
        sec = section_of(meta, n)
        if sec["from"] == n:
            specs.append({"kind": "section", "name": f"c{n:03d}_0sec", "num": sec["num"],
                          "title": sec["title"], "range": sec["range"],
                          "beats": [{"say": sec["say"]}]})
        for p in meta.get("passages", []):
            if p["before"] == n:
                specs.append({"kind": "passage", "name": f"c{n:03d}_1passage", "title": p["title"],
                              "section": sec["title"],
                              "beats": [{"show": x["show"], "say": x["say"]} for x in p["parts"]]})
        beats = [{"role": "question", "say": f"પ્રશ્ન નંબર {n}. " + q.get("q_say", q["q"])}]
        osay = q.get("opts_say", q["opts"])
        for i, L in enumerate("ABCD"):
            beats.append({"role": "option", "say": f"વિકલ્પ {SAY_LABEL[L]}. {osay[i]}"})
        ai = "ABCD".index(q["ans"])
        beats.append({"role": "reveal", "say": q.get("reveal_say",
                      f"સાચો જવાબ છે વિકલ્પ {SAY_LABEL[q['ans']]}. {osay[ai]}.")})
        for s in q["steps"]:
            beats.append({"role": "step", "show": s["show"], "say": s["say"], "kind": s.get("kind", "text")})
        specs.append({"kind": "question", "name": f"c{n:03d}_2q", "n": n, "total": total,
                      "section": sec["title"], "q": q["q"], "opts": q["opts"], "ans": q["ans"],
                      "qwrap": q.get("qwrap", 62), "qmaxh": q.get("qmaxh", 3.0), "beats": beats})
    if not only:
        specs.append({"kind": "outro", "name": "c999_outro", "beats": [{"say": meta["outro_say"]}]})
    return specs


def synth(spec, voice, audio_dir):
    for b in spec["beats"]:
        b["audio"], b["dur"] = tts.synthesize(b["say"], voice, audio_dir)


def render(spec, clips_dir, quality):
    out = os.path.join(clips_dir, spec["name"] + ".mp4")
    if os.path.exists(out):
        return out
    work = os.path.join(clips_dir, "_work", spec["name"])
    os.makedirs(work, exist_ok=True)
    cj = os.path.join(work, "clip.json")
    with open(cj, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False)
    cmd = [sys.executable, "-m", "manim", "render", QFLAG[quality], "--fps", "30",
           "-r", QRES[quality], "--disable_caching", "--media_dir", work,
           "-o", spec["name"], SCENES, CLASS[spec["kind"]]]
    r = subprocess.run(cmd, env=dict(os.environ, QUIZ_CLIP_JSON=cj, PYTHONIOENCODING="utf-8"),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError(f"{spec['name']} failed:\n{r.stderr[-3000:]}")
    found = glob.glob(os.path.join(work, "videos", "**", spec["name"] + ".mp4"), recursive=True)
    if not found:
        raise RuntimeError(f"no output for {spec['name']}")
    shutil.move(found[0], out)
    shutil.rmtree(work, ignore_errors=True)
    return out


def concat(paths, out):
    lst = out + ".txt"
    with open(lst, "w", encoding="utf-8") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-r", "30", "-pix_fmt", "yuv420p",
                    "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-ac", "2", "-movflags", "+faststart", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("-q", "--quality", default="h", choices=list(QFLAG))
    ap.add_argument("--only", help="question range, e.g. 1-3")
    ap.add_argument("--engine", default="edge", choices=["edge", "elevenlabs"])
    ap.add_argument("--voice", default=None)
    ap.add_argument("--model", default="eleven_v3")
    ap.add_argument("--rate", default="-5%", help="edge speaking rate")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    a = ap.parse_args()
    load_dotenv(os.path.join(HERE, ".env"))

    voice = {"engine": a.engine, "voice": a.voice or ("gu-IN-NiranjanNeural" if a.engine == "edge" else None),
             "model": a.model if a.engine == "elevenlabs" else None, "rate": a.rate if a.engine == "edge" else None}
    only = tuple(int(x) for x in a.only.split("-")) if a.only else None
    if only and len(only) == 1:
        only = (only[0], only[0])
    meta, qs = load_content()
    specs = build_specs(meta, qs, only)

    tag = f"{a.engine}_{a.quality}"
    audio_dir = os.path.join(a.out, "audio", a.engine)
    clips_dir = os.path.join(a.out, "clips", tag)
    os.makedirs(clips_dir, exist_ok=True)

    for s in specs:                                  # TTS is sequential (rate limits)
        if not os.path.exists(os.path.join(clips_dir, s["name"] + ".mp4")):
            synth(s, voice, audio_dir)
            print("audio", s["name"], flush=True)

    paths = {}
    with ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(render, s, clips_dir, a.quality): s["name"] for s in specs}
        for f in as_completed(futs):
            paths[futs[f]] = f.result()
            print("clip", futs[f], flush=True)

    name = "GSET_Dec2024_Paper1_Gujarati" + (f"_Q{only[0]}-{only[1]}" if only else "") + f"_{tag}.mp4"
    final = os.path.join(a.out, name)
    concat([paths[s["name"]] for s in specs], final)
    print("FINAL:", final)


if __name__ == "__main__":
    main()
