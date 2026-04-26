# Pitch deck — recording recipe

The deck (`docs/pitch/index.html`) plus your live dashboard recording add up to a 2-minute submission video.  This file is the exact recipe to record it.

## What's here

- **`index.html`** — 9-slide deck. 16:9. Self-contained (no internet needed at record time). Keyboard-navigable. Optional auto-advance with timed slide durations matching the script.
- **`notes.md`** — speaker notes per slide, timed.
- **`README.md`** — this file.

## The 60-minute recording recipe (Mac)

### 1.  Get the deck on screen (2 min)

```bash
# Open the deck in Chrome, full-screen.
open -a "Google Chrome" docs/pitch/index.html
```

In Chrome, press **F** (or fn+F11) → fullscreen.  The deck takes the whole monitor.

### 2.  Get the live dashboard ready in another window (3 min)

In a second Chrome tab/window (move it to a second display if you have one):

```bash
# terminal 1
uvicorn bridge.server:app --port 8765 --reload

# terminal 2 — open dashboard/index.html (or your Lovable URL)
open dashboard/index.html

# terminal 3 — fire the auto-demo when the recording rolls
python scripts/run_demo_auto.py --scenario max_rear_end_a4 --pace slow
```

If your Gemini quota is dead, swap to Ollama beforehand:

```bash
echo "BRAIN_PROVIDER=ollama" >> .env
ollama serve &
ollama pull llama3.2
```

### 3.  Record with QuickTime (5 min setup)

QuickTime Player → **File → New Screen Recording** → pick "record entire screen" → choose internal mic → **Record**.

Recording flow (matches the script in `notes.md`):

1.  **Slide deck visible** — start the recording.  Hit **`A`** to start auto-advance.
2.  **Slides 1–5** play with your voiceover (~38 s total).
3.  **At the end of slide 5**, switch the active window to the dashboard recording.  *Pro tip*: use macOS `Mission Control → Move window` or just `Cmd+Tab`.
4.  Run the dashboard auto-demo for ~25–30 s.  Let pillars tick.  Let Tavily fire.  Let the FINAL CLAIM EXPORT panel show the JSON at the end.
5.  Switch back to the deck (`Cmd+Tab`).  Press **Right arrow** to jump to slide 6.  Resume voiceover.
6.  Slides 6–9 play (~50 s total).
7.  **Stop recording** when slide 9 has been on screen for ~5 s.

Total target: **2:00 ± 5 s**.

### 4.  Edit (10–20 min)

Open the recording in **iMovie** (free, on every Mac):

- Trim head and tail.
- If your voiceover doesn't perfectly match the auto-advance timing, you can drop the slides and the dashboard recording onto the timeline separately and re-time the slides manually.
- Add a quick fade-in at 0:00 and fade-out at end.
- *Optional*: drop background music *very low* (-30 dB) for atmosphere — Apple has free Inca-mood loops in iMovie's library.

Export → **1080p, H.264** → upload to Loom (or YouTube unlisted, or Google Drive).

### 5.  Get the share URL → paste into the submission form

Loom:  *Share → Copy link*.  Paste into the form's "Demo Video Link" field.

## Backup plans

| If… | Then… |
|---|---|
| Auto-advance gets ahead of your voiceover | Press `Esc` to cancel auto-advance, drive the deck manually with `→` |
| Dashboard recording is too long | In iMovie, just trim it down — slides 6–9 still cover the same content |
| QuickTime audio drops out | Re-record audio over the deck silently using *iMovie → File → Record voiceover* |
| Gemini is dead during recording | `BRAIN_PROVIDER=ollama` in `.env`, voice still works on llama3.2 |
| You overshoot 2:00 | Cut slide 3 (the threshold metrics) — the most expendable; keeps the narrative arc intact |

## What the deck shows (for last-minute content checks)

| # | Title | Duration | Key idea |
|---|---|---|---|
| 1 | Title card | 10 s | Caution Claims · Inca Human Test · 32BitSavvy |
| 2 | The challenge | 9 s | Inca's brief verbatim |
| 3 | Three thresholds | 8 s | >50% human · 100% docs · ∞ dialects |
| 4 | The insight | 11 s | Real agents don't ask stupid questions |
| 5 | Sample dialog | 9 s | One actual Sofia turn |
| ↓ | **CUT TO LIVE DASHBOARD** | ~25 s | Run the auto-demo |
| 6 | Multi-domain | 11 s | Car · health · theft · same engine |
| 7 | Architecture | 14 s | Twilio → Gradium → Gemini → Tavily → dashboard |
| 8 | Side bounties | 12 s | Aikido · Entire · Gradium · Pioneer |
| 9 | Closing | 10 s | Repo URL + team |

Total deck time: ~94 s · Dashboard cut: ~25 s · **Sum: ~119 s = 1:59**.

## Editing-free path (if you're tight on time)

If you literally have no time to edit:

1.  In one Chrome window: split-screen with the deck on the left and the dashboard on the right.
2.  Press **`A`** to start auto-advance on the deck.
3.  At the same moment, run `python scripts/run_demo_auto.py --pace slow` in a terminal.
4.  Record everything in one take with QuickTime.
5.  Stop when slide 9 lands.

You'll lose the dramatic cut but keep the timing.  Better a slightly-less-cinematic 2-minute video that ships than a perfect one that misses the deadline.
