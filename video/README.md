# GSET Dec 2024 Paper-1: Gujarati explainer video

Makes one 1920×1080 MP4. For each of the 50 questions it:

1. shows the question and narrates it in Gujarati,
2. reveals the options A–D one at a time, each narrated,
3. gives a **3-second countdown** to think,
4. highlights the correct answer (from the official final key) and says it,
5. narrates a step-by-step explanation; maths questions get every calculation step.

Section cards divide the 10 topic blocks, and the reading passage (Q41–45) is narrated as a Gujarati summary before its questions.

## Files
- `content/*.json`: the full Gujarati script (question, options, answer, and each explanation step's on-screen `show` text and spoken `say` text)
- `scenes.py`: Manim scenes (font Nirmala UI)
- `tts.py`: TTS engines, with cached audio
- `build.py`: builds the audio and clips, renders in parallel, then concatenates (resumable)

## Usage
```
python build.py                      # full 1080p (Edge neural Gujarati voice)
python build.py --only 16-20 -q l    # quick low-res preview
python build.py --engine elevenlabs --voice 3L29IUUN61xcyvsKscMy   # ElevenLabs (needs a paid plan, see below)
```
Output goes to `out/GSET_Dec2024_Paper1_Gujarati_<engine>_<quality>.mp4`. To re-render a clip, delete it from `out/clips/…`.

## Voice / ElevenLabs note
The script is about 38k characters. On the ElevenLabs **free** tier:
- the limit is 10k characters a month;
- professional and library voices (including the native Gujarati ones) are blocked over the API;
- premade English voices produce unintelligible Gujarati.

So the default engine is Microsoft Edge neural `gu-IN-NiranjanNeural`. On a Creator or higher plan, use `--engine elevenlabs` with a Gujarati library voice. "Chinmay – Wise Gujarati Friend" (`3L29IUUN61xcyvsKscMy`) is already added to the account. Put the key in `.env` as `ELEVENLABS_API_KEY=…`.
