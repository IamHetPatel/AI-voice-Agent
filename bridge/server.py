"""FastAPI WebSocket fan-out server.

Event schema (JSON, all events have `type` + `ts`):

  {type: "transcript", speaker: "jamie"|"caller", text: "..."}
  {type: "entity", label: "...", value: "...", confidence: 0.87}
  {type: "fraud_signal", signal: "...", severity: "low"|"medium"|"high"}
  {type: "emotional_state", state: "calm"|"distressed"|"noisy"}
  {type: "tool_call", name: "tavily_lookup_weather", args: {...}}
  {type: "tool_result", name: "...", result: {...}}
  {type: "call_start", crm: {...}}
  {type: "call_end", claim_json: {...}}

Run:
    uvicorn bridge.server:app --host 0.0.0.0 --port 8765 --reload
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse


app = FastAPI(title="Turing Adjuster — bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Hub:
    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._history: list[dict[str, Any]] = []  # last 200 events for late joiners

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._clients.add(ws)
        # replay recent history
        for ev in self._history[-200:]:
            try:
                await ws.send_text(json.dumps(ev))
            except Exception:
                break

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def publish(self, event: dict[str, Any]) -> None:
        event.setdefault("ts", datetime.now(timezone.utc).isoformat())
        self._history.append(event)
        self._history = self._history[-500:]
        dead: list[WebSocket] = []
        for ws in list(self._clients):
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)


hub = Hub()


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return (
        "<h2>Turing Adjuster bridge</h2>"
        "<p>WebSocket: <code>/ws</code></p>"
        "<p>Push events: <code>POST /publish</code></p>"
    )


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"ok": True, "clients": len(hub._clients), "events": len(hub._history)}


@app.post("/publish")
async def publish(event: dict[str, Any]) -> dict[str, Any]:
    """Publish from anywhere (voice loop, extractor, juror bot)."""
    if "type" not in event:
        return {"error": "missing 'type'"}
    await hub.publish(event)
    return {"ok": True}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await hub.connect(ws)
    try:
        while True:
            # tolerate inbound pings from the dashboard
            msg = await ws.receive_text()
            try:
                payload = json.loads(msg)
            except Exception:
                payload = {"type": "ping", "raw": msg}
            if payload.get("type") == "publish":
                await hub.publish(payload.get("event", {}))
    except WebSocketDisconnect:
        await hub.disconnect(ws)


# --- programmatic publisher (used by voice loop / extractor in-process) ---

async def emit(event: dict[str, Any]) -> None:
    await hub.publish(event)


def serve() -> None:
    import uvicorn
    host = os.environ.get("BRIDGE_HOST", "0.0.0.0")
    port = int(os.environ.get("BRIDGE_PORT", "8765"))
    uvicorn.run("bridge.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    serve()
