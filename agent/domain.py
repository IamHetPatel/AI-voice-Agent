"""Load a domain config (FNOL / banking / telco / …) for Jamie.

A domain config is a JSON file under data/domains/ that defines:
  - role + tone for the persona
  - opening line template (uses {first_name} / {company} placeholders)
  - the list of TARGETS (data points to capture, replaces hardcoded PILLARS)
  - fraud signals + escalations specific to this domain
  - which tools the persona may invoke

Same Jamie engine, different config.  This is the architecture answer to
Inca's 'don't focus only on car-accident insurance' feedback.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
DOMAINS_DIR = REPO / "data" / "domains"


@dataclass(frozen=True)
class DomainConfig:
    id: str
    name: str
    role_label: str
    role_description: str
    opening_template: str
    targets: list[tuple[str, str]]   # (id, descriptor)
    fraud_signals: list[str]
    escalations: list[str]
    tools: list[str]
    tone_notes: str

    @property
    def target_ids(self) -> list[str]:
        return [t[0] for t in self.targets]

    @property
    def target_descriptor_map(self) -> dict[str, str]:
        return dict(self.targets)


def list_domains() -> list[str]:
    """Available domain IDs (filenames sans .json)."""
    if not DOMAINS_DIR.exists():
        return []
    return sorted(p.stem for p in DOMAINS_DIR.glob("*.json"))


def load_domain(domain_id: str) -> DomainConfig:
    """Load a domain config by id; raises FileNotFoundError if missing."""
    path = DOMAINS_DIR / f"{domain_id}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    targets = [(t["id"], t["descriptor"]) for t in raw["targets"]]
    return DomainConfig(
        id=raw["id"],
        name=raw["name"],
        role_label=raw["role_label"],
        role_description=raw["role_description"],
        opening_template=raw["opening_template"],
        targets=targets,
        fraud_signals=raw.get("fraud_signals", []),
        escalations=raw.get("escalations", []),
        tools=raw.get("tools", []),
        tone_notes=raw.get("tone_notes", ""),
    )


def render_opening(domain: DomainConfig, crm: dict[str, Any]) -> str:
    """Substitute {first_name} / {company} into the opening template."""
    name = (
        crm.get("policyholder", {}).get("name")
        or crm.get("customer", {}).get("name")
        or crm.get("policyholder", {}).get("contact_person")
        or "there"
    )
    first = name.split()[0] if isinstance(name, str) else "there"
    company = (
        crm.get("policyholder", {}).get("name")
        or crm.get("organization", {}).get("name")
        or ""
    )
    try:
        return domain.opening_template.format(
            first_name=first, company=company, name=name,
        )
    except KeyError:
        return domain.opening_template
