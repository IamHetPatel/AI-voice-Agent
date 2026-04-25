# Entire — agentic-build provenance

Per the verified docs, **only `entire enable` is officially documented**. Treat any `entire dispatch` references in the original game plan as best-effort.

## Setup at hackathon start

```bash
# Once per laptop:
curl -fsSL https://entire.io/install.sh | bash

# Once per repo:
cd /path/to/AI-voice-Agent
entire enable
```

That registers the repo with Entire so every commit-time reasoning trace from Cursor / Claude Code / Codex is captured. The submission story is:

> "Our build process itself is AI-documented. Every architectural decision our agents made while building Jamie is captured by Entire — version-controlled *why* alongside the *what*."

## Architectural decisions worth capturing

If the team uses agents to land changes, write the prompts so the *reasoning* is rich enough for Entire to harvest. Examples:

- *"Use `fastino/gliner2-base-v1` for extraction over `knowledgator/gliner-bi-large-v2.0` because Pioneer is built around Fastino's GLiNER2 family — we win the Pioneer bounty narrative AND get a 5–8% F1 lift on insurance-domain entities. Tradeoff: weights are larger; we ship the base variant, not large."*
- *"Run filler audio injection any time we expect tool-call latency >400ms — Tavily round-trip averages 600–900ms; without filler, perceived latency crosses the uncanny-valley threshold."*
- *"Build the bridge as a separate FastAPI process rather than in-process so the dashboard survives an agent crash. Cost: one extra port; benefit: judges keep seeing live data even if the LLM hangs."*

## If `entire dispatch` does turn out to exist

Run it after each phase and paste the output verbatim into the README's "Build journal" section. Worst case: copy the equivalent reasoning by hand from chat logs; the narrative is the prize, not the tool.
