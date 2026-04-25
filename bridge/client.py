"""Tiny client used by the voice loop / extractor / demo runner to push
events to the bridge.  No coupling to the FastAPI app — uses HTTP POST.
"""

from __future__ import annotations

import os
from typing import Any

import httpx


_BASE = (
    f"http://{os.environ.get('BRIDGE_HOST', '127.0.0.1')}:"
    f"{os.environ.get('BRIDGE_PORT', '8765')}"
)


async def publish(event: dict[str, Any]) -> None:
    """Fire-and-forget publish.  Errors are swallowed (the bridge is optional)."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(f"{_BASE}/publish", json=event)
    except Exception:
        pass


def publish_sync(event: dict[str, Any]) -> None:
    try:
        with httpx.Client(timeout=2.0) as client:
            client.post(f"{_BASE}/publish", json=event)
    except Exception:
        pass
