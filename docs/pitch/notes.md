# Speaker notes — Caution Claims · 2-minute pitch

Read these *while the deck advances*. Each block is timed to a slide's `data-dur` attribute so the slides + voiceover stay synced.

Total deck-only time: ~94 s. Leave ~25 s of that for **dashboard recording cuts** between slides 5 ↔ 6 and slides 6 ↔ 7. If you nail this, you land at **~2:00 ± 5 s**.

---

## Slide 1 · Title (0:00 – 0:10)

> *"This is **Caution Claims**. Our entry for Inca's Human Test at Big Berlin Hack."*

Beat. Let the gradient title breathe.

---

## Slide 2 · The challenge (0:10 – 0:19)

> *"Inca's brief was specific: build a phone agent that fools blind jurors into voting 'human'. They call you. You don't see them. They vote with their gut."*

---

## Slide 3 · The threshold (0:19 – 0:27)

> *"Three things have to land at once. More than half of jurors voting human. Complete claim documentation captured live. And consistency across dialects, highway noise, panicked callers — the whole call-centre nightmare."*

---

## Slide 4 · The insight (0:27 – 0:38)

> *"Our insight is that real claims agents don't ask stupid questions. The caller's name, policy, vehicle, coverage — that's already on the screen before the phone rings. So is ours. Our agent — Jamie — speaks from knowledge, not from a questionnaire. Three layers make that work: known data injected every turn, asked-pillars tracked so she never repeats, and Tavily lookups firing invisibly so she casually quotes real conditions."*

---

## Slide 5 · A real turn (0:38 – 0:47)

> *"Here's what one actual call sounds like. Sofia calls about her physio claim. Jamie already knows her, knows her ytd-usage, asks the one question that closes the gap."*

— at this beat, **CUT TO YOUR DASHBOARD RECORDING** for ~25–30 seconds. The dashboard you screenshotted, with Max's call running live. Pillars ticking. Tavily firing. Live transcript scrolling. End the cut on the "FINAL CLAIM EXPORT" panel showing the JSON.

---

## Slide 6 · Multi-domain (0:47 – 0:58)

> *"Same engine. Different domain config. Three insurance lines shipping today: car FNOL, private health, and Hausrat theft. Each one is a JSON file under data/domains. Banking, telco, life — drop a config, the engine re-targets itself. Inca asked for broad. We went broad."*

---

## Slide 7 · Architecture (0:58 – 1:12)

> *"Under the hood: Twilio SIP into a LiveKit room. Gradium does STT and TTS — Emma voice. Gemini is the brain, with auto-rotation across the model family because Google's free tier melted down mid-hackathon. The system prompt rebuilds every turn with fresh context. Tavily handles the magic 'I see on my system' moments. Pioneer's GLiNER2 plus a Gemini-Lite extractor pull the claim file in parallel. Lovable rendered the dashboard. The brain is provider-pluggable — when Gemini died at 6 PM yesterday we proved it by flipping to local Ollama in one env var."*

---

## Slide 8 · Side bounties (1:12 – 1:24)

> *"Side challenges, woven into the architecture. Aikido's been scanning since commit zero — twelve PII patterns redacted before anything touches a log, because insurance is GDPR Article 9 health data. Entire wrote our build journal — every architectural decision is in docs/entire-dispatches. Gradium runs in three integration tiers, all real. Pioneer is the speed lane: GLiNER2 at 47 milliseconds versus Gemini-Lite at 300 — the benchmark table is in the repo."*

---

## Slide 9 · Closing (1:24 – 1:34)

> *"Caution Claims. Same engine, any insurance line. Built to cross fifty percent. 32BitSavvy — Het Patel and Viraj Dalsania."*

Hold the closing slide for 5 seconds with the repo URL on screen.

---

## Auto-advance mode

The deck supports timed auto-advance via `data-dur` on each slide. The current durations sum to **~94 seconds**, which leaves ~26 seconds for the dashboard cut between slides 5 and 6. If you want the deck to advance itself while you record voiceover, press **`A`** to toggle.

If you'd rather drive it manually with a remote (or with the spacebar), don't press A — just record yourself clicking through.

## Keyboard shortcuts

| Key | Action |
|---|---|
| `→` / `Space` / `PgDn` | Next slide |
| `←` / `PgUp` | Previous slide |
| `A` | Toggle auto-advance |
| `F` | Toggle fullscreen |
| `Home` / `End` | Jump to first / last slide |
| `?` | Hide / show the help hint |
| `Esc` | Cancel auto-advance |

## Click navigation

- Click left third of the slide → previous
- Click right two-thirds → next
