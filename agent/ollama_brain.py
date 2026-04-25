"""Local-LLM brain via Ollama.

Why: hedge against any single cloud provider's quota meltdown.  Ollama
runs on your laptop (`brew install ollama && ollama serve`) and pulls
llama3.2 or qwen2.5 in a minute.  No quota, no rate limits, no API key.

Trade-off: slower than Gemini Flash on a typical M-series laptop
(~1-2s per turn vs. <500ms), and quality is below Gemini Pro for
nuanced empathy.  Use it as a SAFETY NET, not the default.

Verified API surface against the documented Ollama HTTP /api/chat
endpoint at https://github.com/ollama/ollama/blob/main/docs/api.md
(no SDK introspection — uses the public REST API directly so we
don't add a dependency).
"""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator

import httpx


class OllamaBrain:
    """Streaming chat against a local Ollama server."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model_name = model or os.environ.get("OLLAMA_MODEL", "llama3.2")
        self.base_url = base_url or os.environ.get(
            "OLLAMA_BASE_URL", "http://127.0.0.1:11434"
        )
        # _real means: an Ollama server is reachable AND the configured
        # model is loaded.  Probed lazily on first stream_reply rather
        # than at __init__ so importing this module is free.
        self._real: bool | None = None

    async def _probe(self) -> bool:
        if self._real is not None:
            return self._real
        try:
            async with httpx.AsyncClient(timeout=2.0) as c:
                r = await c.get(f"{self.base_url}/api/tags")
                if r.status_code != 200:
                    self._real = False
                    return False
                tags = r.json().get("models", [])
                names = {m.get("name", "").split(":")[0] for m in tags}
                base = self.model_name.split(":")[0]
                self._real = base in names or any(n.startswith(base) for n in names)
        except Exception:
            self._real = False
        return self._real

    async def stream_reply(
        self,
        system_prompt: str,
        history: list[dict[str, str]],
        user_message: str,
    ) -> AsyncIterator[str]:
        if not await self._probe():
            # Ollama not running or model not present — yield a single
            # filler so callers see SOMETHING and can fall back.
            yield (
                "(Local Ollama brain isn't reachable — start ollama and "
                "pull a model, e.g. `ollama pull llama3.2`.)"
            )
            return

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]
        for turn in history:
            role = "user" if turn["role"] == "user" else "assistant"
            messages.append({"role": role, "content": turn["text"]})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {"temperature": 0.85},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except Exception:
                        continue
                    msg = chunk.get("message") or {}
                    text = msg.get("content")
                    if text:
                        yield text
                    if chunk.get("done"):
                        break


# --- self-test -------------------------------------------------------------
if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        b = OllamaBrain()
        print(f"model: {b.model_name}  base: {b.base_url}")
        out = []
        async for piece in b.stream_reply(
            "Reply in one short sentence.",
            [],
            "Hi.",
        ):
            out.append(piece)
        print("".join(out))

    asyncio.run(main())
