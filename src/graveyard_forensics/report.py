from __future__ import annotations

import csv
import json
from pathlib import Path

from jinja2 import Template

from .models import EstateFindings

CSV_COLUMNS = [
    "full_name",
    "classification",
    "stars",
    "pushed_at",
    "language",
    "license_spdx",
    "homepage",
    "homepage_status",
    "is_fork",
    "is_archived",
    "smells",
    "description",
    "html_url",
]


def write_json(findings: EstateFindings, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(findings.to_dict(), indent=2) + "\n", encoding="utf-8")


def write_csv(findings: EstateFindings, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for repo in findings.repos:
            writer.writerow(
                {
                    "full_name": repo.full_name,
                    "classification": repo.classification,
                    "stars": repo.stars,
                    "pushed_at": repo.pushed_at or "",
                    "language": repo.language or "",
                    "license_spdx": repo.license_spdx or "",
                    "homepage": repo.homepage or "",
                    "homepage_status": "" if repo.homepage_status is None else repo.homepage_status,
                    "is_fork": repo.is_fork,
                    "is_archived": repo.is_archived,
                    "smells": "|".join(repo.smells),
                    "description": (repo.description or "").replace("\n", " "),
                    "html_url": repo.html_url,
                }
            )


HTML_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Graveyard Forensics — {{ findings.estate_name }}</title>
<style>
  @page { size: A4; margin: 18mm 16mm; }
  body { font-family: DejaVu Sans, Helvetica, Arial, sans-serif; color: #18202a; font-size: 11.5px; line-height: 1.45; }
  h1 { font-size: 24px; margin: 0 0 4px; }
  h2 { font-size: 16px; margin: 22px 0 8px; border-bottom: 1px solid #d8dde5; padding-bottom: 4px; }
  .meta { color: #5b6673; margin-bottom: 14px; }
  .banner { background: #18202a; color: #fff; padding: 12px 14px; border-radius: 6px; margin: 10px 0 16px; }
  .banner strong { color: #ffd166; }
  .kpis { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 4px; }
  .kpi { border: 1px solid #d8dde5; border-radius: 6px; padding: 8px 10px; min-width: 110px; background: #f7f8fa; }
  .kpi b { display: block; font-size: 18px; }
  table { width: 100%; border-collapse: collapse; margin-top: 6px; }
  th, td { text-align: left; padding: 5px 6px; border-bottom: 1px solid #e6eaef; vertical-align: top; }
  th { background: #f0f2f5; font-size: 10.5px; text-transform: uppercase; letter-spacing: .03em; }
  ul { margin: 6px 0; padding-left: 18px; }
  .tag { display: inline-block; background: #fff5ef; border: 1px solid #f0d7c8; color: #a64f21; border-radius: 999px; padding: 1px 7px; font-size: 10px; margin: 1px 2px 1px 0; }
  .foot { margin-top: 24px; color: #5b6673; font-size: 10px; }
  .cols { display: flex; gap: 16px; }
  .col { flex: 1; }
</style>
</head>
<body>
  <h1>Graveyard Forensics</h1>
  <div class="meta">Estates Sale Report · {{ findings.estate_kind }} <strong>{{ findings.estate_name }}</strong> · scanned {{ findings.scanned_at[:10] }}</div>

  <div class="banner">
    Grave score <strong>{{ findings.score }}/100</strong> ({{ findings.score_band }}).
    This report is generated from public GitHub metadata only. Price-claim rows are marketing text, not verified revenue.
  </div>

  <div class="kpis">
    <div class="kpi"><b>{{ findings.total_public_repos }}</b>public repos</div>
    <div class="kpi"><b>{{ findings.zero_star_count }}</b>zero-star</div>
    <div class="kpi"><b>{{ findings.price_claim_repos|length }}</b>price claims</div>
    <div class="kpi"><b>{{ findings.migration_stub_repos|length }}</b>migration stubs</div>
    <div class="kpi"><b>{{ findings.keepers|length }}</b>keepers</div>
    <div class="kpi"><b>{{ findings.dead_homepage_repos|length }}</b>dead homepages</div>
  </div>

  <h2>1. Estate overview</h2>
  <p>
    Scanned {{ findings.scanned_repos }} repositories under <code>{{ findings.estate_name }}</code>.
    {{ findings.missing_description_count }} missing descriptions ·
    {{ findings.fork_count }} forks in scan set ·
    {{ findings.archived_count }} archived ·
    {{ findings.humanitarian_claim_repos|length }} “free for X” claims.
  </p>

  <h2>2. Crime scene smells</h2>
  <div class="cols">
    <div class="col">
      <h3 style="margin:8px 0 4px;font-size:13px;">Price claims ({{ findings.price_claim_repos|length }})</h3>
      <ul>
      {% for r in findings.price_claim_repos %}<li><code>{{ r }}</code></li>{% endfor %}
      {% if not findings.price_claim_repos %}<li>None detected</li>{% endif %}
      </ul>
    </div>
    <div class="col">
      <h3 style="margin:8px 0 4px;font-size:13px;">Migration stubs ({{ findings.migration_stub_repos|length }})</h3>
      <ul>
      {% for r in findings.migration_stub_repos[:25] %}<li><code>{{ r }}</code></li>{% endfor %}
      {% if findings.migration_stub_repos|length > 25 %}<li>… +{{ findings.migration_stub_repos|length - 25 }} more</li>{% endif %}
      {% if not findings.migration_stub_repos %}<li>None detected</li>{% endif %}
      </ul>
      <h3 style="margin:8px 0 4px;font-size:13px;">Rename-prefix stubs ({{ findings.rename_stub_repos|length }})</h3>
      <p style="margin:4px 0;color:#5b6673;">Combined stub debt used in grave score: {{ findings.migration_stub_repos|length + findings.rename_stub_repos|length }}</p>
    </div>
  </div>
  <div class="cols">
    <div class="col">
      <h3 style="margin:8px 0 4px;font-size:13px;">Dead / broken homepages</h3>
      <ul>
      {% for r in findings.dead_homepage_repos %}<li><code>{{ r }}</code></li>{% endfor %}
      {% if not findings.dead_homepage_repos %}<li>None detected</li>{% endif %}
      </ul>
    </div>
    <div class="col">
      <h3 style="margin:8px 0 4px;font-size:13px;">Do not monetize ({{ findings.do_not_monetize|length }})</h3>
      <ul>
      {% for r in findings.do_not_monetize %}<li><code>{{ r }}</code></li>{% endfor %}
      {% if not findings.do_not_monetize %}<li>None flagged</li>{% endif %}
      </ul>
    </div>
  </div>

  <h2>3. Keepers ({{ findings.keepers|length }})</h2>
  <ul>
  {% for r in findings.keepers %}<li><code>{{ r }}</code></li>{% endfor %}
  {% if not findings.keepers %}<li>No keepers — everything is noise or unproven.</li>{% endif %}
  </ul>

  <h2>4. Extracted wallet — sellable candidates</h2>
  <ul>
  {% for s in findings.sellables %}<li>{{ s }}</li>{% endfor %}
  {% if not findings.sellables %}<li>No obvious sellable allowlist hits. Promote from active unproven repos after productizing one.</li>{% endif %}
  </ul>

  <h2>5. Fourteen-day cleanup checklist</h2>
  <ol>
    <li>Archive or delete migration stubs and <code>myproduct</code>/<code>Test</code> placeholders.</li>
    <li>Strip unverified <code>$X/month</code> claims from READMEs and descriptions (or wire a real checkout).</li>
    <li>Rewrite descriptions for keepers: problem, who it’s for, install command.</li>
    <li>Add LICENSE + topics to every keeper; delete empty repos.</li>
    <li>Point dead homepages at GitHub READMEs; fix DNS or remove links.</li>
    <li>Pin 3 keepers on the profile README; move the rest under an org archive.</li>
    <li>Re-run <code>graveyard scan --owner …</code> and diff CSV week-over-week.</li>
  </ol>

  <h2>6. Sample inventory (top 40 by stars, then name)</h2>
  <table>
    <thead><tr><th>Repo</th><th>Class</th><th>★</th><th>Smells</th></tr></thead>
    <tbody>
    {% for r in sample %}
      <tr>
        <td><code>{{ r.full_name }}</code></td>
        <td>{{ r.classification }}</td>
        <td>{{ r.stars }}</td>
        <td>{% for s in r.smells %}<span class="tag">{{ s }}</span>{% endfor %}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>

  <div class="foot">
    <p><strong>Methodology:</strong> GitHub GraphQL/REST public API · description regex for price/humanitarian/migration smells · homepage HTTP status probe · keeper allowlist + star/homepage rules. Full row-level CSV ships with purchase.</p>
    <p><strong>Limitations:</strong> Not a revenue audit. Not legal advice. Medical/regulated repos are flagged do-not-monetize only.</p>
    <p>Generated by Graveyard Forensics · {{ findings.scanned_at }} · https://github.com/BoozeLee/graveyard-forensics</p>
  </div>
</body>
</html>
"""
)


def render_html(findings: EstateFindings) -> str:
    sample = sorted(
        findings.repos,
        key=lambda r: (-r.stars, r.full_name.lower()),
    )[:40]
    return HTML_TEMPLATE.render(findings=findings, sample=sample)


def write_html(findings: EstateFindings, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(findings), encoding="utf-8")


def write_pdf(findings: EstateFindings, path: Path) -> None:
    from weasyprint import HTML

    path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=render_html(findings)).write_pdf(path)


def write_markdown(findings: EstateFindings, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Graveyard Forensics — {findings.estate_name}",
        "",
        f"- Scanned: {findings.scanned_at}",
        f"- Kind: {findings.estate_kind}",
        f"- Score: {findings.score}/100 ({findings.score_band})",
        f"- Public repos: {findings.total_public_repos}",
        f"- Zero-star: {findings.zero_star_count}",
        f"- Price claims: {len(findings.price_claim_repos)}",
        f"- Migration stubs: {len(findings.migration_stub_repos)}",
        f"- Rename-prefix stubs: {len(findings.rename_stub_repos)}",
        f"- Keepers: {len(findings.keepers)}",
        "",
        "## Price claims",
    ]
    lines.extend(f"- `{r}`" for r in findings.price_claim_repos)
    lines.extend(["", "## Migration stubs"])
    lines.extend(f"- `{r}`" for r in findings.migration_stub_repos)
    lines.extend(["", "## Rename-prefix stubs"])
    lines.extend(f"- `{r}`" for r in findings.rename_stub_repos)
    lines.extend(["", "## Keepers"])
    lines.extend(f"- `{r}`" for r in findings.keepers)
    lines.extend(["", "## Sellables"])
    lines.extend(f"- {s}" for s in findings.sellables)
    lines.extend(["", "## Notes"])
    lines.extend(f"- {n}" for n in findings.notes)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
