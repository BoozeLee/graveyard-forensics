from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .gh import scan_estate
from .report import write_csv, write_html, write_json, write_markdown, write_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graveyard",
        description="Audit a GitHub user/org estate for stubs, fake price claims, and keepers.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan an owner or org")
    scan.add_argument("--owner", required=True, help="GitHub user or org login")
    scan.add_argument("--kind", choices=["auto", "user", "org"], default="auto")
    scan.add_argument("--out", type=Path, default=Path("reports"))
    scan.add_argument("--prefix", default=None, help="Output filename prefix (default: owner)")
    scan.add_argument("--skip-homepage-probe", action="store_true")
    scan.add_argument("--no-pdf", action="store_true")

    teaser = sub.add_parser("teaser", help="Free score + top smells only")
    teaser.add_argument("--owner", required=True)
    teaser.add_argument("--kind", choices=["auto", "user", "org"], default="auto")
    teaser.add_argument("--top", type=int, default=5)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "teaser":
        findings = scan_estate(
            args.owner,
            kind=args.kind,
            probe_homepages=False,
        )
        print(f"Estate: {findings.estate_name} ({findings.estate_kind})")
        print(f"Grave score: {findings.score}/100 ({findings.score_band})")
        print(f"Public repos: {findings.total_public_repos} · zero-star: {findings.zero_star_count}")
        print(f"Price claims: {len(findings.price_claim_repos)} · stubs: {len(findings.migration_stub_repos)}")
        smells = [
            ("price_claim", findings.price_claim_repos),
            ("migration_stub", findings.migration_stub_repos),
            ("dead_homepage", findings.dead_homepage_repos),
            ("humanitarian_claim", findings.humanitarian_claim_repos),
        ]
        shown = 0
        for label, items in smells:
            for item in items[: args.top]:
                print(f"  [{label}] {item}")
                shown += 1
        print("Full PDF+CSV: Estates Sale report (paid). Public metadata only.")
        return 0

    findings = scan_estate(
        args.owner,
        kind=args.kind,
        probe_homepages=not args.skip_homepage_probe,
    )
    prefix = args.prefix or findings.estate_name
    out: Path = args.out
    write_json(findings, out / f"{prefix}-findings.json")
    write_csv(findings, out / f"{prefix}-inventory.csv")
    write_html(findings, out / f"{prefix}-report.html")
    write_markdown(findings, out / f"{prefix}-report.md")
    if not args.no_pdf:
        write_pdf(findings, out / f"{prefix}-report.pdf")

    print(f"Scanned {findings.scanned_repos}/{findings.total_public_repos} repos for {findings.estate_name}")
    print(f"Score: {findings.score}/100 ({findings.score_band})")
    print(f"Wrote reports under {out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
