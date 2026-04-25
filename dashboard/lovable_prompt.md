# Lovable regeneration prompt

Paste this into Lovable to get a polished, production-grade version of the dashboard. The single-file `index.html` already in this folder works for live demos; Lovable gives us the "looks like a real insurance tool" finish.

---

> Build a React dashboard for a real-time German motor-insurance FNOL (first-notice-of-loss) intake tool, named **VORSICHT Claims · Live FNOL Console**.
>
> Connection: It connects to a WebSocket at `ws://localhost:8765/ws` and receives JSON events. Each event has `type` and `ts`. The five event types are:
> - `{type:"transcript", speaker:"jamie"|"caller", text:string}`
> - `{type:"entity", label:string, value:string, confidence:number}`
> - `{type:"fraud_signal", signal:string, severity:"low"|"medium"|"high", evidence:string}`
> - `{type:"emotional_state", state:"calm"|"distressed"|"noisy"}`
> - `{type:"tool_call", name:string, args:object}` and `{type:"tool_result", name:string, result:object}`
> - `{type:"call_start", crm:object}` and `{type:"call_end", claim_json:object}`
>
> Layout (3 columns × 2–3 rows, 14px gutter, full viewport, dark UI):
>
> 1. **Left column (~40%)**: large Live Transcript panel (caller bubbles aligned left, Jamie bubbles aligned right with subtle teal tint, auto-scroll), plus a smaller Tool Calls log below it.
> 2. **Middle column (~30%)**: Claim Pillars panel — a 15-item checklist that ticks off as `entity` events arrive. The 15 pillars are: injuries, accident_datetime, accident_location, road_type, weather_conditions, how_it_happened, vehicle_drivable, other_party_involved, other_party_plate, other_party_insurer, police_involved, police_case_number, witnesses, fault_admission, settlement_preference. Below that, a Fraud Signals panel showing a 0–10 risk gauge (sum of severities, low=1, medium=2, high=4, capped at 10) plus a list of flagged signals.
> 3. **Right column (~30%)**: Emotional Mode panel (one big tinted word: CALM/DISTRESSED/NOISY in green/red/amber), Known Context panel (read-only JSON viewer of the CRM profile that came in `call_start`), and Final Claim JSON panel with a Copy button (visible only after `call_end`).
>
> Header: bold "VORSICHT Claims · Live FNOL Console" with three pills on the right — connection status, "pillars X/15", "fraud risk N/10".
>
> Style: dark navy (#0b1220 bg, #111a2e panels, #1f2a44 borders, #d6dee9 ink, #5fb4ff accent, #4ade80 good, #fbbf24 warn, #f87171 bad). Inter font. 12px border-radius on panels. The whole thing should look like enterprise insurance software, not a hackathon demo.
>
> Persist nothing in localStorage. All state lives in React.
