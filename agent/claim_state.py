"""Tracks the 13 data pillars Inca expects to see in a complete FNOL claim
(plus a few sub-pillars we collect so the dashboard looks rich).

The state is the source of truth for *what Jamie still needs to ask*.  The
GLiNER2 extractor pushes updates here; the prompt builder reads from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


# Order = priority order Jamie should gather these.  Pillar 1 ("policy &
# vehicle ID") is intentionally absent — it lives in the CRM, Jamie must
# never ask for it.
#
# Each entry is (id, short_descriptor).  We deliberately do NOT include a
# pre-written sample question — putting one in the system prompt biases
# the LLM to use that exact phrasing every turn (we observed this).
PILLARS: list[tuple[str, str]] = [
    ("injuries",              "anyone hurt — caller, passengers, third party"),
    ("accident_datetime",     "when (date + time)"),
    ("accident_location",     "where (address / road name)"),
    ("road_type",             "Autobahn / city street / parking lot / other"),
    ("how_it_happened",       "free-form description of the incident"),
    ("vehicle_drivable",      "is the car drivable + current location"),
    ("other_party_involved",  "was anyone else involved"),
    ("other_party_plate",     "other vehicle license plate"),
    ("other_party_insurer",   "other party's insurer"),
    ("police_involved",       "was police called"),
    ("police_case_number",    "police case / reference number"),
    ("witnesses",             "independent witnesses (name + contact)"),
    ("driver_identity",       "who was driving (if not policyholder)"),
    ("fault_admission",       "anything said about fault at the scene"),
    ("settlement_preference", "preferred repair shop / need a rental"),
]

FRAUD_LABELS: list[str] = [
    "delayed_reporting",
    "known_to_other_party",
    "vehicle_listed_for_sale",
    "prior_similar_incident",
    "timeline_inconsistency",
]


@dataclass
class ClaimState:
    """Mutable per-call state.  One instance per call."""

    call_id: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    pillars: dict[str, Any] = field(default_factory=dict)
    fraud_signals: dict[str, Any] = field(default_factory=dict)
    emotional_mode: str = "calm"  # calm | distressed | noisy
    notes: list[str] = field(default_factory=list)

    # ----- pillar updates -----
    def fill(self, label: str, value: str, confidence: float = 1.0) -> None:
        """Record a pillar value.  No-op if already filled with high confidence."""
        existing = self.pillars.get(label)
        if existing and existing.get("confidence", 0) >= confidence:
            return
        self.pillars[label] = {"value": value, "confidence": confidence,
                               "ts": datetime.now(timezone.utc).isoformat()}

    def flag_fraud(self, signal: str, evidence: str, severity: str = "medium") -> None:
        self.fraud_signals[signal] = {"evidence": evidence, "severity": severity,
                                       "ts": datetime.now(timezone.utc).isoformat()}

    def set_mode(self, mode: str) -> None:
        if mode in ("calm", "distressed", "noisy"):
            self.emotional_mode = mode

    # ----- prompt-builder helpers -----
    def filled_summary(self) -> str:
        if not self.pillars:
            return "(none yet)"
        lines = []
        for label, data in self.pillars.items():
            lines.append(f"  - {label}: {data['value']}")
        return "\n".join(lines)

    def unfilled_pillars(self) -> list[tuple[str, str]]:
        return [(k, q) for (k, q) in PILLARS if k not in self.pillars]

    def unfilled_summary(self) -> str:
        """Legacy — keep for backwards compat.  Prefer unfilled_summary_compact."""
        unfilled = self.unfilled_pillars()
        if not unfilled:
            return "(all gathered — wrap up the call warmly)"
        return "\n".join(f"  - {label}: {hint}" for label, hint in unfilled)

    def unfilled_summary_compact(self) -> str:
        """One-line-per-pillar summary, NO scripted question phrasings.

        Used by the v2 system prompt — the absence of pre-written
        questions is by design, so Jamie phrases each ask fresh and
        in-context instead of repeating a template."""
        unfilled = self.unfilled_pillars()
        if not unfilled:
            return "(all 15 pillars gathered — wrap up warmly with a claim reference)"
        # Top-3 are highest priority, the rest are reference-only
        top = unfilled[:3]
        rest = unfilled[3:]
        out = ["FOCUS NOW (priority order):"]
        for lab, desc in top:
            out.append(f"  • {lab}  —  {desc}")
        if rest:
            out.append("Later (reference only, don't read as a list):")
            for lab, desc in rest:
                out.append(f"  · {lab}  —  {desc}")
        return "\n".join(out)

    def fraud_risk_score(self) -> int:
        """Return 0..10 based on number/severity of flagged signals."""
        weight = {"low": 1, "medium": 2, "high": 4}
        total = sum(weight.get(s["severity"], 1) for s in self.fraud_signals.values())
        return min(10, total)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
