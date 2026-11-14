"""Gujarati TTS: ElevenLabs (primary when quota/voice allow) or Edge neural (fallback).

Audio is cached by engine+voice+text hash, so re-runs never re-bill the API.
"""
import os, hashlib, subprocess, asyncio
import requests

EL_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"


def ffprobe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path])
    return float(out.strip())


def _key(cfg, text):
    raw = f"{cfg['engine']}|{cfg.get('voice')}|{cfg.get('model')}|{cfg.get('rate')}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _elevenlabs(text, cfg, out):
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        raise RuntimeError("ELEVENLABS_API_KEY not set")
    body = {"text": text, "model_id": cfg.get("model", "eleven_v3"), "language_code": "gu",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    r = requests.post(EL_URL.format(voice=cfg["voice"]), json=body, timeout=180,
                      headers={"xi-api-key": k, "Content-Type": "application/json"})
    if not r.ok:
        raise RuntimeError(f"ElevenLabs error {r.status_code}: {r.text[:300]}")
    with open(out, "wb") as f:
        f.write(r.content)


def _edge(text, cfg, out):
    import edge_tts

    async def go():
        c = edge_tts.Communicate(text, cfg.get("voice", "gu-IN-NiranjanNeural"),
                                 rate=cfg.get("rate", "+0%"))
        await c.save(out)

    for attempt in range(4):
        try:
            asyncio.run(go())
            if os.path.getsize(out) > 0:
                return
        except Exception as e:  # transient websocket failures happen
            last = e
    raise RuntimeError(f"edge-tts failed: {last}")


def synthesize(text, cfg, cache_dir):
    """Return (mp3_path, seconds). cfg = {'engine': 'edge'|'elevenlabs', 'voice': ..., ...}"""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, _key(cfg, text) + ".mp3")
    if not os.path.exists(path):
        tmp = path + ".part.mp3"
        (_elevenlabs if cfg["engine"] == "elevenlabs" else _edge)(text, cfg, tmp)
        os.replace(tmp, path)
    return path, ffprobe_duration(path)
