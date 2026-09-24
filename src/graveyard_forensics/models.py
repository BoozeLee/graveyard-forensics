from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class RepoRecord:
    name: str
    full_name: str
    owner: str
    description: str | None
    stars: int
    pushed_at: str | None
    is_fork: bool
    is_archived: bool
    homepage: str | None
    html_url: str
    language: str | None = None
    license_spdx: str | None = None
    topics: tuple[str, ...] = ()
    homepage_status: int | None = None
    smells: tuple[str, ...] = ()
    classification: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["topics"] = list(self.topics)
        data["smells"] = list(self.smells)
        return data


@dataclass
class EstateFindings:
    estate_name: str
    estate_kind: str
    scanned_at: str
    total_public_repos: int
    scanned_repos: int
    zero_star_count: int
    missing_description_count: int
    fork_count: int
    archived_count: int
    price_claim_repos: list[str] = field(default_factory=list)
    humanitarian_claim_repos: list[str] = field(default_factory=list)
    migration_stub_repos: list[str] = field(default_factory=list)
    rename_stub_repos: list[str] = field(default_factory=list)
    dead_homepage_repos: list[str] = field(default_factory=list)
    keepers: list[str] = field(default_factory=list)
    sellables: list[str] = field(default_factory=list)
    do_not_monetize: list[str] = field(default_factory=list)
    score: int = 0
    score_band: str = ""
    repos: list[RepoRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["repos"] = [r.to_dict() if isinstance(r, RepoRecord) else r for r in self.repos]
        return data
