from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Iterable

from .models import EstateFindings, RepoRecord
from .signals import SENSITIVE_NAME, classify_smells, estate_score

KEEPER_ALLOWLIST = {
    "capo",
    "beehive-studio",
    "mixhive",
    "trendforge-agent",
    "vlaio-webapp",
    "ai-template-engine",
    "terminal221b",
    "gitcrate",
    "azure-security-hardening",
    "ubuntu-security-hardening-script",
    "ubuntu-live-security",
    "go-ai-coder",
    "steady-state-doctor",
    "dex223-contracts",
    "rhythmicritual",
    "codeqai",
    "automationcodex-core",
    "linty-mclintface",
    "elohim-forge",
    "synapse-ace-agent",
}

SELLABLE_HINTS = {
    "beehive-studio": "Local-first AI music product (license / early access)",
    "mixhive": "DJ niche platform (pilot / pro tier)",
    "capo": "Viral OSS + paid team configs",
    "trendforge-agent": "SAP research packs / consultant sidekick",
    "azure-security-hardening": "Fixed-price hardening audit kit",
    "ubuntu-security-hardening-script": "STIG compliance service collateral",
    "ai-template-engine": "AutomationCodex template pack",
    "go-ai-coder": "Local coding agent support tier",
    "rhythmicritual": "Creative bundle with cleared demo media",
    "codeqai": "Local code-search pro features",
}

# Upstream mirrors / borrowed repos that must not rank as personal keepers.
MIRROR_NAMES = {
    "coolify",
    "openmanus",
    "beehive",
    "common",
    "footprinter",
    "rp2040-zero",
    "popcorntime-flatpak",
}


def run_gh(args: list[str]) -> str:
    result = subprocess.run(
        ["gh", *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def gh_json(args: list[str]) -> Any:
    return json.loads(run_gh(args))


def gh_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    # gh treats every field except query/operationName as a GraphQL variable.
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is None:
            continue
        args.extend(["-f", f"{key}={value}"])
    raw = run_gh(args)
    data = json.loads(raw)
    if data.get("errors"):
        raise RuntimeError(str(data["errors"]))
    return data


def probe_homepage(url: str | None, timeout: float = 5.0) -> int | None:
    if not url:
        return None
    target = url if url.startswith(("http://", "https://")) else f"https://{url}"
    req = urllib.request.Request(target, method="HEAD", headers={"User-Agent": "graveyard-forensics/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except Exception:
        return 0


def _user_repositories(owner: str) -> tuple[list[dict[str, Any]], int]:
    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        repositories(
          first: 100
          after: $cursor
          privacy: PUBLIC
          isFork: false
          ownerAffiliations: OWNER
          orderBy: {field: PUSHED_AT, direction: DESC}
        ) {
          totalCount
          pageInfo { hasNextPage endCursor }
          nodes {
            name description stargazerCount pushedAt isFork isArchived
            homepageUrl url primaryLanguage { name }
            licenseInfo { spdxId }
            repositoryTopics(first: 20) { nodes { topic { name } } }
          }
        }
      }
    }
    """
    repos: list[dict[str, Any]] = []
    cursor: str | None = None
    total = 0
    while True:
        data = gh_graphql(query, {"login": owner, "cursor": cursor})
        block = data["data"]["user"]["repositories"]
        total = block["totalCount"]
        repos.extend(block["nodes"])
        if not block["pageInfo"]["hasNextPage"]:
            break
        cursor = block["pageInfo"]["endCursor"]
    return repos, total


def _org_repositories(org: str) -> tuple[list[dict[str, Any]], int]:
    query = """
    query($login: String!, $cursor: String) {
      organization(login: $login) {
        repositories(
          first: 100
          after: $cursor
          privacy: PUBLIC
          orderBy: {field: PUSHED_AT, direction: DESC}
        ) {
          totalCount
          pageInfo { hasNextPage endCursor }
          nodes {
            name description stargazerCount pushedAt isFork isArchived
            homepageUrl url primaryLanguage { name }
            licenseInfo { spdxId }
            repositoryTopics(first: 20) { nodes { topic { name } } }
          }
        }
      }
    }
    """
    repos: list[dict[str, Any]] = []
    cursor: str | None = None
    total = 0
    while True:
        data = gh_graphql(query, {"login": org, "cursor": cursor})
        block = data["data"]["organization"]["repositories"]
        total = block["totalCount"]
        repos.extend(block["nodes"])
        if not block["pageInfo"]["hasNextPage"]:
            break
        cursor = block["pageInfo"]["endCursor"]
    return repos, total


def _probe_many(urls: Iterable[str]) -> dict[str, int | None]:
    return {url: probe_homepage(url) for url in urls if url}


def _to_record(node: dict[str, Any], owner: str, homepage_status: dict[str, int | None]) -> RepoRecord:
    homepage = node.get("homepageUrl") or None
    desc = node.get("description")
    smells, classification = classify_smells(
        description=desc,
        name=node["name"],
        homepage=homepage,
        homepage_status=homepage_status.get(homepage or "", None) if homepage else None,
        is_fork=bool(node.get("isFork")),
        is_archived=bool(node.get("isArchived")),
        stars=int(node.get("stargazerCount") or 0),
        pushed_at=node.get("pushedAt"),
    )
    if SENSITIVE_NAME.search(node["name"]) or (desc and SENSITIVE_NAME.search(desc)):
        classification = "do_not_monetize"
        smells = [*smells, "sensitive_domain"]
    topics = tuple(
        t["topic"]["name"] for t in (node.get("repositoryTopics") or {}).get("nodes", [])
    )
    lang = node.get("primaryLanguage")
    lic = node.get("licenseInfo")
    return RepoRecord(
        name=node["name"],
        full_name=f"{owner}/{node['name']}",
        owner=owner,
        description=desc,
        stars=int(node.get("stargazerCount") or 0),
        pushed_at=node.get("pushedAt"),
        is_fork=bool(node.get("isFork")),
        is_archived=bool(node.get("isArchived")),
        homepage=homepage,
        html_url=node.get("url") or f"https://github.com/{owner}/{node['name']}",
        language=(lang or {}).get("name"),
        license_spdx=(lic or {}).get("spdxId"),
        topics=topics,
        homepage_status=homepage_status.get(homepage, None) if homepage else None,
        smells=tuple(smells),
        classification=classification,
    )


def scan_estate(owner: str, *, kind: str = "auto", probe_homepages: bool = True) -> EstateFindings:
    if kind == "auto":
        try:
            gh_json(["api", f"orgs/{owner}", "--jq", ".login"])
            kind = "org"
        except Exception:
            kind = "user"

    if kind == "org":
        nodes, total = _org_repositories(owner)
        estate_kind = "org"
    else:
        nodes, total = _user_repositories(owner)
        estate_kind = "user"

    homepages = sorted({n.get("homepageUrl") for n in nodes if n.get("homepageUrl")})
    status_map = _probe_many(homepages) if probe_homepages else {}
    records = [_to_record(n, owner, status_map) for n in nodes]

    price_claims = [r.full_name for r in records if "price_claim" in r.smells]
    humanitarian = [r.full_name for r in records if "humanitarian_claim" in r.smells]
    stubs = sorted({r.full_name for r in records if "migration_stub" in r.smells})
    rename_prefix = sorted({r.full_name for r in records if "rename_stub_prefix" in r.smells})
    stub_or_rename = sorted(set(stubs) | set(rename_prefix))
    dead = [
        r.full_name
        for r in records
        if r.homepage and r.homepage_status in {0, 404, 410}
    ]
    keepers = sorted(
        {
            r.full_name
            for r in records
            if (not r.is_fork)
            and r.name.lower() not in MIRROR_NAMES
            and (
                r.name.lower() in KEEPER_ALLOWLIST
                or r.stars >= 1
                or (
                    r.homepage
                    and r.homepage_status
                    and 200 <= r.homepage_status < 400
                    and "migration_stub" not in r.smells
                    and "rename_stub_prefix" not in r.smells
                )
            )
        }
    )
    # Drop rename/migration stubs from keepers even if allowlisted by accident
    stub_names = {s.split("/")[-1].lower() for s in stub_or_rename}
    dnm_names = {r.full_name for r in records if r.classification == "do_not_monetize"}
    keepers = [
        k
        for k in keepers
        if k.split("/")[-1].lower() not in stub_names and k not in dnm_names
    ]

    sellables = [f"{r.full_name}: {SELLABLE_HINTS[r.name.lower()]}" for r in records if r.name.lower() in SELLABLE_HINTS]
    do_not = [r.full_name for r in records if r.classification == "do_not_monetize"]

    zero_stars = sum(1 for r in records if r.stars == 0 and not r.is_fork)
    missing_desc = sum(1 for r in records if not (r.description or "").strip())
    forks = sum(1 for r in records if r.is_fork)
    archived = sum(1 for r in records if r.is_archived)

    counts = {
        "total_public_repos": total,
        "zero_star_count": zero_stars,
        "price_claim_repos": price_claims,
        "migration_stub_repos": stub_or_rename,  # score uses combined stub debt
        "missing_description_count": missing_desc,
        "dead_homepage_repos": dead,
    }
    score, band = estate_score(counts)

    notes = [
        "Public GitHub metadata only. No private repo contents are read.",
        "Price-claim detection is pattern matching on descriptions, not proof of billing.",
        "Dead homepage = HEAD/GET failed or HTTP 404/410 at scan time.",
        "migration_stub_repos = explicit Migrated-to stubs; rename_stub_repos = bakery-* prefix noise; grave score counts both.",
    ]

    return EstateFindings(
        estate_name=owner,
        estate_kind=estate_kind,
        scanned_at=datetime.now(timezone.utc).isoformat(),
        total_public_repos=total,
        scanned_repos=len(records),
        zero_star_count=zero_stars,
        missing_description_count=missing_desc,
        fork_count=forks,
        archived_count=archived,
        price_claim_repos=price_claims,
        humanitarian_claim_repos=humanitarian,
        migration_stub_repos=stubs,
        rename_stub_repos=rename_prefix,
        dead_homepage_repos=dead,
        keepers=keepers,
        sellables=sellables,
        do_not_monetize=do_not,
        score=score,
        score_band=band,
        repos=records,
        notes=notes,
    )
