"""Provider-pluggable conversational brain.

Why: Google's free tier had a multi-hour 429 storm during the hackathon
(other teams confirmed on Discord).  Pinning to a single provider is a
demo-day failure waiting to happen.  This module lets the brain be:

    BRAIN_PROVIDER=gemini    (default — agent.gemini_client.GeminiBrain)
    BRAIN_PROVIDER=ollama    (local llama3 / qwen, no quota)
    BRAIN_PROVIDER=openai    (if you have an OpenAI key)

All brains expose the same async interface:

    async for chunk in brain.stream_reply(system_prompt, history, user_msg):
        ...

`make_brain()` reads BRAIN_PROVIDER and returns the right one.  If the
configured provider isn't available (key missing / package not installed)
we log loudly and fall back to the next available option, so the demo
never silently degrades.
"""

from __future__ import annotations

import os
import sys
from collections.abc import AsyncIterator
from typing import Any, Protocol


class Brain(Protocol):
    """The minimal interface every brain implementation must satisfy."""

    model_name: str
    _real: bool   # True if the brain is wired to a live LLM, False = stub

    def stream_reply(
        self,
        system_prompt: str,
        history: list[dict[str, str]],
        user_message: str,
    ) -> AsyncIterator[str]: ...


def _try_gemini() -> Brain | None:
    try:
        from .gemini_client import GeminiBrain
        b = GeminiBrain()
        # The stub falls back to deterministic replies when no key.  We
        # still return it for offline development; callers can check ._real.
        return b
    except Exception as e:
        print(f"  [brain] gemini unavailable: {e}", file=sys.stderr)
        return None


def _try_ollama() -> Brain | None:
    try:
        from .ollama_brain import OllamaBrain
        b = OllamaBrain()
        if not b.probe_sync():
            print(
                f"  [brain] ollama not reachable at {b.base_url} "
                f"or model '{b.model_name}' not pulled — falling through",
                file=sys.stderr,
            )
            return None
        return b
    except Exception as e:
        print(f"  [brain] ollama unavailable: {e}", file=sys.stderr)
        return None


def _try_openai() -> Brain | None:
    try:
        from .openai_brain import OpenAIBrain
        b = OpenAIBrain()
        if not b._real:
            return None
        return b
    except Exception as e:
        print(f"  [brain] openai unavailable: {e}", file=sys.stderr)
        return None


_FACTORIES = {
    "gemini": _try_gemini,
    "ollama": _try_ollama,
    "openai": _try_openai,
}


def make_brain(prefer: str | None = None) -> Brain:
    """Return a usable brain.  Tries the preferred provider first, then
    falls back through the others until one yields a real (non-stub)
    brain.  Worst case returns the Gemini stub so code paths still run."""
    order = [prefer or os.environ.get("BRAIN_PROVIDER", "gemini")]
    for k in ("gemini", "ollama", "openai"):
        if k not in order:
            order.append(k)

    for prov in order:
        if prov not in _FACTORIES:
            continue
        b = _FACTORIES[prov]()
        if b is not None and getattr(b, "_real", False):
            print(f"  [brain] using {prov}: {b.model_name}", file=sys.stderr)
            return b

    # Worst case — return the gemini stub so the demo runs without keys.
    fallback = _try_gemini()
    if fallback is not None:
        print(f"  [brain] no live provider — falling back to stub", file=sys.stderr)
        return fallback
    raise RuntimeError("no brain available — install google-genai at minimum")
