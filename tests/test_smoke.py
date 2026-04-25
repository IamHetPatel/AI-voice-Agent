"""Smoke tests — fast, no network, no API keys.

These prove the modules import + the core data path works.
Run with:  pytest -q
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_crm_profiles_load():
    for name in ["max_mueller", "helga_schmidt", "thomas_weber_fleet"]:
        p = REPO / "data" / "crm" / f"{name}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["policyholder"]["name"]
        assert data["policy"]["policy_number"]


def test_pii_redact():
    from agent.pii_redact import redact
    sample = "policy DE-HUK-2024-884421 plate B-MM 4421 vin WVWZZZ1JZ3W386752"
    out = redact(sample)
    assert "884421" not in out
    assert "[POLICY]" in out
    assert "[PLATE]" in out
    assert "[VIN]" in out


def test_claim_state_priorities():
    from agent.claim_state import ClaimState, PILLARS
    s = ClaimState(call_id="t")
    assert len(s.unfilled_pillars()) == len(PILLARS)
    s.fill("injuries", "no injuries")
    assert "injuries" not in dict(s.unfilled_pillars())
    s.flag_fraud("delayed_reporting", "three weeks", "high")
    assert s.fraud_risk_score() >= 4


def test_extractor_stub_path():
    from extraction.gliner2_service import ExtractionService
    svc = ExtractionService()
    out = svc.extract(
        "I was on the A4 today, plate K-AB 1234, the police came, "
        "I have whiplash, three weeks ago I noticed the dent."
    )
    # In stub mode we should still pull at least a couple of these:
    keys = set(out["pillars"]) | set(out["fraud"])
    assert {"other_party_plate", "road_type"} <= keys or svc.mode == "gliner"


def test_prompt_builder_includes_crm():
    from agent.claim_state import ClaimState
    from agent.prompts import build_jamie_system_prompt
    crm = json.loads((REPO / "data" / "crm" / "max_mueller.json").read_text())
    p = build_jamie_system_prompt(crm, ClaimState(call_id="t"))
    assert "Max Müller" in p
    assert "Volkswagen" in p
    assert "DO NOT ASK" in p


def test_tavily_stub_runs():
    from tools.tavily_lookup import lookup_weather
    r = lookup_weather("A4 Köln")
    assert "summary" in r
