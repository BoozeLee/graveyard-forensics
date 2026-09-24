# Estate Sale — Graveyard Forensics

**By Kiliaan Vanvoorden** ([@BoozeLee](https://github.com/BoozeLee)) · [Bakery-street-project](https://github.com/Bakery-street-project) · scanned **2026-09-23**

I audited my own GitHub graveyard with the scanner I sell. Full identity, full numbers, zero invented revenue.

---

## The headline

| Estate | Public non-fork repos* | Grave score | Zero-star | Price claims | “Migrated to” stubs | `bakery-*` rename | Keepers |
|---|---:|---:|---:|---:|---:|---:|---:|
| `BoozeLee` (user) | **200** | **99/100** open-casket | **199** | **15** | **70** | **62** | **21** |
| `Bakery-street-project` (org) | **60** | **53/100** shallow-grave | **57** | **1** | **0** | **0** | **9** |

\*GraphQL `privacy: PUBLIC`, user query `isFork: false`. Org = all public org repos.

**Real money from these GitHub products to date: €0.**  
Stripe charges on this account that I can list are `livemode: false` (test). A June 2026 monetization push created templates and test links — no production sales. The configured **live** restricted key currently returns **401**; live checkout for *this* product stays gated until that key is repaired and the approval phrase is provided.

---

## Crime scene

### 1. Price tags without a checkout

Fifteen user-repo descriptions still read like a pitch deck:

- `dream-analyzer` — “Freemium $19/month”
- `quantum-encryption` — “Premium $299/month”
- `health-optimizer` — “$299/month”
- `green-supply-chain` — “$2,999/month enterprise”
- `personalized-medicine` — “Premium $499/month”
- `supply-chain-resilience`, `renewable-energy-planner`, `renewable-energy-predictor`, `skill-gap-analyzer`, `fair-trade-platform`, `ecosystem-simulator`, `drug-discovery-optimizer`, `infrastructure-resilience`, `procrastination-breaker`, `ptcg-ai-porygon`, …

None of these are wired to a product I can fulfill. That is fraud-adjacent branding even when nobody pays.

### 2. Migration theater

- **70** user repos have “Migrated to …” descriptions.
- **62** are `bakery-*` rename debris (heavy overlap with the 70).
- Grave score counts both as stub debt.
- Non-`bakery` redirects still in the set include `conduit`, `codex-superlab`, `neuroforge-agent`, `beeai-hive-999`, `hiem-app`, `Laboratory-Templates`, …

### 3. Dead links

Live probe at scan time (HEAD/GET → failure or 404/410):

- `BoozeLee/mixhive` → `https://mixhive.app` — **down**
- `BoozeLee/Baker-Street-Laboratory-1` → GitHub dev preview URL — **404**
- Org: `ai-development-framework` → `bakerstreetproject221b.store` — **down**; `go-ai-coder` homepage failed

### 4. Humanitarian inflation

**22** descriptions say “FREE for …” (governments, clinics, WHO/CDC, NGOs, astronomers, …). Nice bit. Still a claim list, not customers.

### 5. Do-not-monetize (flagged automatically)

Medical/regulated names in the sample: `disease-predictor`, `drug-discovery-optimizer`, `personalized-medicine`, `steady-state-doctor`, `BakerStreet-Oncology-Research`, `mental-health-companion`, … → **legal review before any dollar**.

---

## What is still alive (keepers)

Not “everything with a README” — allowlist + star/homepage rules, mirrors excluded (`coolify`, `openmanus`, `beehive`, `common`, `footprinter`, …):

**User (21):** `BoozeLee.github.io`, `Dex223-contracts`, `RhythmicRitual`, `ai-template-engine`, `automationcodex-core`, `azure-security-hardening`, `beehive-studio`, `capo`, `codeqai`, `elite-engineering-codex`, `elohim-forge`, `go-ai-coder`, `mistral-vibe-cli-docs`, `mistral-vibe-configuration`, `mixhive`, `pauliens-sky-app`, `synapse-ace-agent`, `terminal221b`, `trendforge-agent`, `universal-treasury`, `vlaio-webapp` — mirrors excluded (`coolify`, `openmanus`, `beehive`, `common`, `footprinter`, …); medical/regulated **do-not-monetize** excluded from keepers (`steady-state-doctor`, `disease-predictor`, …).

**Org (9):** `Baker-Street-Laboratory`, `Linty-McLintface`, `MYTHICNODE-Neuromorphic-Psychedelic-AI`, `Terminal221b`, `dynamic-asynchronous-data-streamliner`, `elohim-forge`, `gitcrate`, `go-ai-coder`, `symmetrical-waffle`.

### Extracted wallet (sellable candidates)

| Repo | Angle |
|---|---|
| `beehive-studio` | Local-first AI music license / early access |
| `capo` | Viral OSS + paid team configs |
| `mixhive` | DJ niche pilot (fix domain first) |
| `trendforge-agent` | SAP research packs |
| `azure-security-hardening` | Fixed-price hardening kit / audit |
| `ai-template-engine` | AutomationCodex template pack |
| `go-ai-coder` | Local coding-agent support tier |

---

## 14-day cleanup (my own hit list)

1. Archive `bakery-*` rename debris and empty placeholders (`Test44`, `myproduct`, `poc`, …).
2. Strip every unverified `$X/month` from descriptions/READMEs **or** wire a real payment link the same day.
3. Rewrite keepers: problem → who → install command.
4. LICENSE + topics on keepers; delete noise.
5. Kill dead homepages (or fix DNS).
6. Pin three keepers on the profile README; stop featuring vapor SaaS prices.
7. Re-run `graveyard scan --owner BoozeLee` weekly; require score to drop.

---

## Methodology (reproducible)

```bash
gh auth status
git clone https://github.com/BoozeLee/graveyard-forensics
cd graveyard-forensics && uv sync
uv run graveyard scan --owner BoozeLee --out reports
uv run graveyard scan --owner Bakery-street-project --kind org --out reports
```

Signals: GraphQL public repos → description regex (`price_claim`, `humanitarian_claim`, `migration_stub`) → homepage HTTP status → keeper/mirror allowlists → grave score.

**Limits:** public metadata only · not a revenue audit · not legal advice · score measures cleanup debt, not quality of code.

---

## What I am selling

**Estates Sale report — $79**

You get the same PDF + row-level CSV I ran on myself:

- Grave score + band
- Every price claim / stub / dead homepage / do-not-monetize
- Keepers + sellable candidates
- 14-day cleanup checklist

**Free teaser:** open an issue with template `teaser` (or a Discussion thread) with your `owner` login → score + top smells.

**Checkout:** see [OFFER.md](./OFFER.md). Live Stripe payment link activates after (1) live key repair and (2) approval phrase `APPROVE LIVE STRIPE DRAFTS FOR: Graveyard Forensics — Estates Sale Report`. Until then: free teaser or email for a manual $79 run.

Sample artifacts: [examples/](./examples/) · full pipeline: `uv run graveyard scan --owner …`

---

*If your profile looks like mine, you do not have 200 products. You have a landfill with three shovels in it. I sell the shovel audit.*
