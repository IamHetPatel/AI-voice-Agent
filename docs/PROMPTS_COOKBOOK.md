# Prompts cookbook — examples for Cursor / Claude Code

Copy/paste prompts that produced the working code in this repo. Use them as the seed for further iteration; Entire will pick up the reasoning.

## 1. Stack-aware integration prompt

> Write a Python class `JamiePipeline` using `livekit-agents[gradium]` that wires `gradium.TTS()` as TTS, falls back to LiveKit's default STT if `gradium.STT` is unavailable, and uses `agent.gemini_client.GeminiBrain` (Gemini 3 Flash) as the LLM. The pipeline must (a) accept inbound audio from a LiveKit room, (b) regenerate the system prompt every turn via `agent.prompts.build_jamie_system_prompt(crm, state)`, (c) fork the latest user transcript to `extraction.gliner2_service.ExtractionService` and push entity events to `bridge.client.publish`, and (d) inject pre-generated filler audio from `fillers/audio/*.pcm` whenever the LLM stalls more than 400ms. Use the documented `gradium.TTS()` constructor — do NOT invent a `GradiumTTSService` class, that doesn't exist.

## 2. Known-context system-prompt prompt

> Write `agent.prompts.build_jamie_system_prompt(crm, state)` that produces a system prompt for Gemini 3 Flash playing a German motor-insurance claims-intake specialist. It must (a) inline the entire CRM JSON under a header that says "DO NOT ASK FOR ANY OF THESE FIELDS", (b) inline the live ClaimState (filled vs. unfilled pillars, emotional mode), (c) forbid acknowledging being an AI, (d) instruct the agent to confirm physical safety before any data collection, (e) describe the available Tavily tool calls and how to phrase them out loud as "let me just pull up the map…", (f) keep replies to one or two sentences in spoken style — no markdown, no bullet lists. Emit the prompt as a single string.

## 3. GLiNER2 extraction microservice

> Write `extraction.gliner2_service.ExtractionService` that loads `fastino/gliner2-base-v1` first, falls back to `knowledgator/gliner-bi-large-v2.0`, and falls back to a regex stub if `gliner` isn't installed at all. Expose `extract(text) -> {pillars, fraud, elapsed_ms, mode, model}`. The 15 claim labels and 5 fraud labels live as module-level lists. Expose `run_async_extractor(stream, on_update)` for streaming use. When called from the bridge, push events as `{type: "entity", label, value, confidence}` and `{type: "fraud_signal", signal, severity, evidence}`.

## 4. Adversarial juror harness

> Write `tests/juror_bot.py` that simulates 6 adversarial calls (rotating 3 personas) between an Anthropic claude-sonnet-4-6 caller and our Jamie pipeline (text-only, calling `agent.gemini_client.GeminiBrain` and `agent.prompts.build_jamie_system_prompt`). After each call, ask the juror LLM for a strict-JSON verdict `{verdict, confidence, reasoning}`. Save results to `tests/juror_results.json` and `.csv`. Print the human-pass rate at the end. Make the harness run gracefully without ANTHROPIC_API_KEY (deterministic stubs), so it can be invoked in CI.

## 5. PII redactor for DSGVO logging

> Write `agent/pii_redact.py` exposing `redact(text)` and `redacted_dict(d)`. Patterns: German policy numbers (regex `[A-Z]{2}-[A-Z]{2,4}-\d{4}-\d{4,8}`), VINs (17 chars), German plates (`B-MM 4421` style), German phones (loose), German IBANs, DOB (`yyyy-mm-dd`), emails. Replace each with a token in square brackets. Include a `__main__` self-test. This file is the load-bearing piece of the Aikido bounty pitch — it is the answer to "you handle GDPR Article 9 data, how do you log it?"
