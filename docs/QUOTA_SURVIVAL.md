# Quota survival — what to do when Gemini is 429-locked

The Gemini Developer free tier has per-model AND per-day buckets. During the hackathon a lot of teams hammered the same models simultaneously and Google rate-limited heavily — both of your accounts hit the wall.

Here's the order to follow when that happens.

## 1. Check what's actually working

```bash
python scripts/diagnose_gemini.py
```

It calls `client.models.list()` to enumerate what your key can see, then probes each candidate with a tiny generateContent. The output tells you which models are reachable and which are 429-locked **per model bucket**. Lite usually survives when Flash and Pro have died.

## 2. If at least one Gemini model still works

Set it as the default in `.env`:

```
GEMINI_MODEL=gemini-2.5-flash-lite
```

Both the chat brain (`agent/gemini_client.py`) and the eval judge (`scripts/eval_jamie.py`) auto-rotate to fallback models if the configured one 429s mid-call, so you don't actually have to change config — the rotation will find Lite. But pinning it saves the wasted retries.

## 3. If EVERYTHING Gemini is 429-locked — switch to Ollama (local, no quota)

```bash
# Install (one-time):
brew install ollama
ollama serve &        # keep this terminal open

# Pull a small fast model (~2 GB) — first time only:
ollama pull llama3.2    # 3B, fast, fine for prompt iteration
# OR
ollama pull qwen2.5:7b  # 7B, better empathy / German, slower

# Wire Jamie to use it:
echo "BRAIN_PROVIDER=ollama" >> .env
echo "OLLAMA_MODEL=llama3.2" >> .env

# Same demo as before — Jamie now runs against the local model:
python scripts/run_demo_auto.py --scenario max_rear_end_a4 --pace normal
```

**Trade-offs vs. Gemini:**
- Latency: ~1–3s per turn on M-series MacBook (vs. <500ms on Gemini Flash)
- Quality: llama3.2-3B is noticeably less polite/empathetic; qwen2.5-7b is closer
- No quota, no rate limits, no API key needed

**Use it for:**
- Iterating on Jamie's prompt without burning real credits
- Recording fallback demo videos in case Google is dead at submission time
- Running the eval scoring loop hundreds of times if needed

**Don't use it for:**
- The final pitch-video recording (Gemini Flash sounds noticeably more human)

## 4. If you have other API keys, add them too

The brain factory in `agent/brain.py` knows about OpenAI as well. Set:

```
BRAIN_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

And `pip install openai`. Same `stream_reply` interface; the runner doesn't care which provider answers.

## 5. Iteration discipline for the rest of the hackathon

- **NEVER run an eval pass against transcripts in a loop without checking quota first.** Each `eval_jamie.py --all` is `N transcripts × 1 judge call` — easy to burn 20+ requests without realizing.
- **Save Gemini for the actual pitch-video recording.** Iterate on prompts using Ollama or Lite; record the demo with Flash/Pro for max quality.
- **Run `verify_keys.py` once an hour** so you know early if you've hit the daily wall.
- **Free-tier resets at midnight Pacific**, which is ~09:00 in Berlin — your final test window before submission.

## 6. The judge-model fallback (already wired)

`scripts/eval_jamie.py` now tries judges in this order:
```
gemini-2.5-flash-lite  →  gemini-flash-latest  →  gemini-2.5-flash  →  gemini-2.5-pro
```
First one that answers wins. You'll see this in the output. If all four are dead, the script reports the last exception clearly.
