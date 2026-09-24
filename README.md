# Graveyard Forensics

Audit a GitHub user or org **estate** for migration stubs, fake price claims, dead homepages, and the few repos worth keeping — then ship a PDF + CSV **Estates Sale** report.

Public metadata only. No private repo contents.

## Install

```bash
uv sync
uv run graveyard --help
```

## Scan

```bash
# Full paid-shaped report (PDF + CSV + JSON + HTML + MD)
uv run graveyard scan --owner BoozeLee --out reports

# Free teaser (score + top smells)
uv run graveyard teaser --owner BoozeLee
```

## What it flags

| Smell | Meaning |
|---|---|
| `price_claim` | Description invents `$X/month`, freemium, enterprise license, etc. |
| `humanitarian_claim` | “FREE for humanity / governments / …” inflation |
| `migration_stub` | “Migrated to …” redirect-only repo |
| `dead_homepage` | `homepageUrl` fails HTTP or returns 404/410 |
| `zero_stars` | No traction signal |
| `rename_stub_prefix` | `bakery-*` rename noise |
| `sensitive_domain` | Medical/regulated names → do-not-monetize |

**Grave score** (0–100): higher = deeper cleanup debt. Bands: `relatively-tidy` → `needs-dusting` → `shallow-grave` → `open-casket`.

## Product

| Tier | Price | What you get |
|---|---:|---|
| **Free teaser** | $0 | `graveyard teaser --owner YOU` output shape: score + top smells (also via issue template) |
| **Estates Sale report** | **$79** | Full PDF + row-level CSV + keepers/sellables + 14-day cleanup plan |

See [OFFER.md](./OFFER.md) · self specimen [TEARDOWN.md](./TEARDOWN.md) · samples in [examples/](./examples/).

Live checkout is gated: test-mode payment link is prepared; live Stripe requires key repair + approval phrase in `monetization-launch/approvals/graveyard-forensics-estates-sale-approval.md`.

## License

MIT (tool). Generated reports © Kiliaan Vanvoorden.
