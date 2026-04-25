"""OpenAI brain — opt-in fallback if you have an OpenAI key.

Verified API against the openai>=1.0 Python SDK's chat.completions.create
streaming surface.  Not added to requirements.txt by default; install with
`pip install openai` if you want this provider available.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator


class OpenAIBrain:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model_name = model or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._real = False
        self._client = None
        if not self.api_key:
            return
        try:
            from openai import AsyncOpenAI  # type: ignore
            self._client = AsyncOpenAI(api_key=self.api_key)
            self._real = True
        except Exception:
            return

    async def stream_reply(
        self,
        system_prompt: str,
        history: list[dict[str, str]],
        user_message: str,
    ) -> AsyncIterator[str]:
        if not self._real:
            yield "(OpenAI brain not configured — set OPENAI_API_KEY and `pip install openai`.)"
            return
        msgs = [{"role": "system", "content": system_prompt}]
        for turn in history:
            role = "user" if turn["role"] == "user" else "assistant"
            msgs.append({"role": role, "content": turn["text"]})
        msgs.append({"role": "user", "content": user_message})

        stream = await self._client.chat.completions.create(  # type: ignore[union-attr]
            model=self.model_name,
            messages=msgs,
            temperature=0.85,
            stream=True,
        )
        async for chunk in stream:
            choices = getattr(chunk, "choices", None) or []
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            text = getattr(delta, "content", None) if delta else None
            if text:
                yield text
