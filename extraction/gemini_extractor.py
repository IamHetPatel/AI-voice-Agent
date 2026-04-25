"""Pillar extraction via Gemini structured output, domain-aware.

The extractor builds its prompt + allowed-keys list from the domain
config it's constructed with.  This is the fix for the bug where the
banking + telco runs filled pillars like 'accident_location' (FNOL
labels) — the prompt was hardcoded to the FNOL label set.

We use Gemini-Lite specifically: independent quota bucket from Flash,
basically free, ~300ms latency.  Falls back to GLiNER on failure so
the dashboard never sits empty.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from .gliner2_service import (
    CLAIM_LABELS, FRAUD_LABELS, ExtractionService as _GLiNERService,
)


_EXTRACT_PROMPT_TEMPLATE = """\
You are a strict information extractor.  Read the SHORT transcript chunk \
below — it is one or two sentences from a phone call about an insurance claim.

Extract ONLY information that is explicitly stated.  Do NOT infer, do NOT \
fill in details that aren't there.  If a key has nothing to extract from \
the transcript, OMIT it from the output (do NOT write "null" or "unknown").

Return a single JSON object with these allowed keys (and only these):
{label_block}

For each key you include, the value is the literal text snippet from the \
transcript that supports it (verbatim, no paraphrasing).

Transcript:
"""


class GeminiExtractor:
    """Domain-aware extractor.  Same surface as ExtractionService.extract()."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash-lite",
        fallback: _GLiNERService | None = None,
        targets: list[tuple[str, str]] | None = None,
        fraud_labels: list[str] | None = None,
    ) -> None:
        self.model = model
        self._fallback = fallback or _GLiNERService()
        # Domain-driven labels — fall back to the FNOL-flavored CLAIM_LABELS
        # if no domain was passed (preserves old single-domain quickstart).
        self._targets = list(targets) if targets is not None else [
            (l, l.replace("_", " ")) for l in CLAIM_LABELS
        ]
        self._fraud_labels = list(fraud_labels) if fraud_labels is not None else list(FRAUD_LABELS)
        self._target_ids = {t[0] for t in self._targets}
        self._fraud_ids = set(self._fraud_labels)

        self._enabled = bool(os.environ.get("GOOGLE_API_KEY"))
        self._client: Any = None
        if self._enabled:
            try:
                from google import genai  # type: ignore
                self._client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
            except Exception:
                self._enabled = False

    @property
    def mode(self) -> str:
        if self._enabled:
            return f"gemini-extract ({self.model})"
        return self._fallback.mode

    @property
    def model_name(self) -> str:
        return self.model if self._enabled else (self._fallback.model_name or "")

    # ---- prompt builder, domain-aware --------------------------------
    def _build_prompt(self, text: str) -> str:
        lines = [f"  {tid}  —  {desc}" for (tid, desc) in self._targets]
        if self._fraud_labels:
            lines.append("")
            lines.append("Plus the following FRAUD-SIGNAL keys (only if explicit in the transcript):")
            for fid in self._fraud_labels:
                lines.append(f"  {fid}")
        return _EXTRACT_PROMPT_TEMPLATE.format(label_block="\n".join(lines)) + text

    # -----------------------------------------------------------------
    def extract(self, text: str) -> dict[str, Any]:
        """Domain-aware extraction.  Returns {pillars, fraud, mode, model}."""
        t0 = time.perf_counter()
        if not self._enabled:
            return self._fallback.extract(text)

        try:
            from google.genai import types  # type: ignore
            resp = self._client.models.generate_content(
                model=self.model,
                contents=self._build_prompt(text),
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    max_output_tokens=600,
                ),
            )
            raw = (getattr(resp, "text", "") or "").strip()
            data = json.loads(raw) if raw else {}
        except Exception:
            return self._fallback.extract(text)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        pillars: dict[str, dict[str, Any]] = {}
        fraud: dict[str, dict[str, Any]] = {}
        for k, v in data.items():
            if not isinstance(v, str) or not v.strip():
                continue
            if k in self._target_ids:
                pillars[k] = {"label": k, "text": v.strip(), "score": 0.95}
            elif k in self._fraud_ids:
                fraud[k] = {"label": k, "text": v.strip(), "score": 0.9}
            # else: silently drop hallucinated keys outside the domain's set
        return {
            "pillars": pillars,
            "fraud": fraud,
            "elapsed_ms": round(elapsed_ms, 2),
            "mode": "gemini-extract",
            "model": self.model,
        }


    # ---- factory: build from a DomainConfig --------------------------
    @classmethod
    def for_domain(cls, domain, **kwargs) -> "GeminiExtractor":
        """Build a GeminiExtractor pre-configured for a DomainConfig."""
        return cls(
            targets=list(domain.targets),
            fraud_labels=list(domain.fraud_signals),
            **kwargs,
        )


# --- self-test -------------------------------------------------------------
if __name__ == "__main__":
    from dotenv import load_dotenv  # type: ignore
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    e = GeminiExtractor()
    print("mode:", e.mode)
    out = e.extract(
        "Hi, no one's hurt but my car got hit on the A4 near Köln-Ost about 30 minutes ago."
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
