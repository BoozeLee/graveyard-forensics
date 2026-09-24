from __future__ import annotations

import re
from datetime import datetime, timezone

PRICE_CLAIM = re.compile(
    r"(\$[0-9][\d,]*(?:\.\d+)?(?:\s*/\s*month|/mo|/month)?|"
    r"\b(?:freemium|premium)\b.*?\$[0-9]+|"
    r"\b[€$][0-9]+(?:\.[0-9]+)?\s*/\s*month\b|"
    r"\b(?:enterprise|government|research|commercial)\s+licen[cs]e\b)",
    re.IGNORECASE,
)

HUMANITARIAN_CLAIM = re.compile(
    r"\bfree\s+for\s+(?:humanity|all|everyone|clinics|governments|ngos|"
    r"journalists|astronomers|researchers|activists|humanitarian|"
    r"emergency|conservation|education|writers|therap[y|ists]+|"
    r"policymakers|regulators|who|cdc|space agencies|utilities|citizens)\b",
    re.IGNORECASE,
)

MIGRATION_STUB = re.compile(
    r"(migrated\s+to\s+\S+|see\s+https://github\.com/\S+)",
    re.IGNORECASE,
)

SENSITIVE_NAME = re.compile(
    r"(disease|drug[-_]?discovery|medical|patient|oncology|diagnos|"
    r"pandemic|mental[-_]?health|disease[-_]?predictor|steady[-_]?state[-_]?doctor)",
    re.IGNORECASE,
)

PRICE_WORDS = re.compile(r"(?:\$|€)\s?\d|/month|/mo\b|freemium|premium\s+\$", re.IGNORECASE)


def classify_smells(
    *,
    description: str | None,
    name: str,
    homepage: str | None,
    homepage_status: int | None,
    is_fork: bool,
    is_archived: bool,
    stars: int,
    pushed_at: str | None,
) -> tuple[list[str], str]:
    smells: list[str] = []
    desc = description or ""

    if not desc.strip():
        smells.append("missing_description")
    if PRICE_CLAIM.search(desc):
        smells.append("price_claim")
    if HUMANITARIAN_CLAIM.search(desc):
        smells.append("humanitarian_claim")
    if MIGRATION_STUB.search(desc):
        smells.append("migration_stub")
    if is_fork:
        smells.append("fork")
    if is_archived:
        smells.append("archived")
    if stars == 0:
        smells.append("zero_stars")
    if homepage:
        if homepage_status is None:
            smells.append("homepage_unchecked")
        elif homepage_status == 0:
            smells.append("dead_homepage")
        elif homepage_status >= 400:
            smells.append("broken_homepage")
    if re.match(r"^(bakery[-_])", name, re.IGNORECASE):
        smells.append("rename_stub_prefix")
    if name.startswith("myproduct") or name in {"test-repo", "Test44", "poc"}:
        smells.append("placeholder_name")

    if is_fork:
        classification = "fork_noise"
    elif is_archived:
        classification = "archived"
    elif "migration_stub" in smells or "rename_stub_prefix" in smells:
        classification = "migration_stub"
    elif "price_claim" in smells and stars == 0 and "dead_homepage" in smells + ["broken_homepage"]:
        classification = "vapor_price_claim"
    elif "price_claim" in smells and stars == 0:
        classification = "vapor_price_claim"
    elif stars >= 1 and not is_fork:
        classification = "signal"
    elif _is_recent(pushed_at) and not is_fork:
        classification = "active_unproven"
    else:
        classification = "graveyard"

    return smells, classification


def _is_recent(pushed_at: str | None, days: int = 90) -> bool:
    if not pushed_at:
        return False
    try:
        ts = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    now = datetime.now(timezone.utc)
    return (now - ts).days <= days


def estate_score(counts: dict[str, object]) -> tuple[int, str]:
    """Higher score = deeper grave (more cleanup debt, better specimen)."""
    total = max(counts.get("total_public_repos", 0), 1)
    zero_ratio = counts.get("zero_star_count", 0) / total
    price = len(counts.get("price_claim_repos", []))
    stubs = len(counts.get("migration_stub_repos", []))
    missing = counts.get("missing_description_count", 0) / total
    dead_raw = counts.get("dead_homepage_repos", 0)
    dead = len(dead_raw) if isinstance(dead_raw, list) else int(dead_raw or 0)

    score = int(
        min(100, zero_ratio * 40 + min(price, 20) * 1.5 + min(stubs, 20) * 1.5 + missing * 20 + min(dead, 10) * 2)
    )
    if score >= 75:
        band = "open-casket"
    elif score >= 50:
        band = "shallow-grave"
    elif score >= 25:
        band = "needs-dusting"
    else:
        band = "relatively-tidy"
    return score, band
