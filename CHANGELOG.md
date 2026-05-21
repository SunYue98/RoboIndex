# Changelog

Tracks notable changes to the RoboIndex dataset and tooling. Dataset
versions follow `YYYY.MM.DD.N`. Schema version follows semver-major;
bumped only when Entity / Relation / Claim shape changes.

For real-time dataset version, fetch
`https://sunyue.github.io/RoboIndex/api/summary.json` — the top of that
file carries the current `schema_version`, `dataset_version`, and
`snapshot_sha`.

---

## schema_version 1

Stable shape since Phase 7 (2026-05-21).

```ts
Entity {
  id, name, company, category, imageUrl, websiteUrl?,
  year, isNew, specs,
  relatedIds?, relations?[Relation],
  tags?, paperInfo?, orgInfo?, importance?,
  sources?[Source],
  seriesId?, seriesOrder?, seriesLabel?,
  fundingRounds?[FundingRound], portfolio?[PortfolioInvestment],
  sourcedSpecs?[key: Claim]
}

Relation { targetId, role, source?, asOf?, notes?, isInverse? }
Claim<T> { value: T, source?, asOf?, confidence?, notes? }
Source { title, url, type? }
```

Allowed Relation roles, allowed Categories, and per-category claim
schemas are documented in `src/data/entities.ts` and
`src/data/categoryClaimSchema.ts`.

---

## Dataset snapshots

Newer entries on top. Each entry corresponds to a notable PR / commit.

### 2026.05.21 — Phase 8: Contribution workflow + versioning (current)

- Added `CONTRIBUTING.md` with 8 recipe-driven contribution types,
  designed for both humans and AI agents.
- Added `.github/pull_request_template.md` with structured tickboxes.
- Added `scripts/precommit.sh` — one-shot validation + API rebuild +
  version bump + health refresh pipeline.
- Added `research/_tools/version_bump.py` — emits
  `schema_version` / `dataset_version` / `snapshot_sha` into
  `summary.json`.

### 2026.05.21 — Phase 7: Health / reflection tooling

- Added `check_bias.py` (region / era / stage / gender / source-type /
  language breakdowns).
- Added `check_url_liveness.py` (cached HEAD checks).
- Added `health_report.py` → `research/HEALTH.md` committed snapshot.
- Surfaced bias findings: China 42% + USA 39% = 81% concentration,
  Japan 1%, South Korea <1%; 56% of entities founded ≥2015.
- 71 client-error URLs identified; most are anti-bot 403s, a few real
  404s found (muksrobotics.com/spaceo-pro-01,
  humanoid.press/database/...-robotera-l7).

### 2026.05.21 — Phase 6: Public API layer

- Generated 11 endpoints at `public/api/*`:
  `entities.json` (1.2 MB), `relations.json` (411 KB),
  `funding-rounds.json`, `summary.json`, `by-{category,country,year}.json`,
  `entities.csv`, `relations.csv`, `narrative.md`, `README.md`.
- 667 entities, 1514 typed edges available to external consumers.

### 2026.05.20 — Phase 5: People as first-class entities

- Added category `人物` under `参与实体`.
- 4 new relation roles: `founder-of`, `employed-at`, `alumni-of`,
  `advised-by`.
- Seeded 20 persons: 10 humanoid founders (Brett Adcock, Bernt Børnich,
  Wang Xingxing, Peng Zhihui, etc.) + 10 lab PIs (Sergey Levine,
  Chelsea Finn, Daniela Rus, Ken Goldberg, etc.).
- Total entities: 647 → 667.

### 2026.05.20 — Phase 3+4: Claim-level sourcing + typed per-category schemas

- Added `Claim<T>` interface and `sourcedSpecs?: Record<string, Claim>`
  to Entity.
- Defined `CATEGORY_CLAIM_SCHEMA` for 20 categories with ~3-8 typed
  fields each (height_cm, weight_kg, dof, payload_kg, …).
- Migrated 845 spec values across 398 entities into Claim form, with
  strict parsing (unit matching, imperial→metric, plausibility ranges,
  relative-claim rejection).
- SpecsList UI renders claims with per-field source ↗ icons.

### 2026.05.20 — Phase 2: Relation semantic types

- Added `Relation` interface with 12 typed roles (forward + inverse
  reflection).
- Migrated 1409 of 1472 edges from untyped `relatedIds: string[]` to
  typed `relations: Relation[]`. 12 entities have legacy-only
  `relatedIds` remaining (super-niche pairs).
- RelatedLinksList groups by role with directional labels
  ("制造方"/"创始人"/"投资人"/etc.).

### 2026.05.20 — Phase 1: Schema foundation

- Added `Relation`, `Claim` TypeScript interfaces.
- Added `validate_schema.py` with referential integrity, source
  coverage, migration-progress baseline tracking.
- Zero validation errors on initial pass.

### 2026.05.19 — Image collection v1: 100+ logos

- Built fetch_logos.py (Wikipedia infobox + website grep fallback).
- Collected ~100 company / VC / lab logos via cairosvg → process_image.py
  pipeline. Coverage moved: 产业 2%→66%, 资本 0%→45%, 实验室 3%→58%.
- Synthetic title cards introduced (`generate_synthetic_cards.py`) for
  ~450 entries lacking real images.

### 2026.05.18 — China coverage expansion

- +134 Chinese entities (humanoid companies, dexterous hand makers,
  VCs, labs) with verified sources.
- Funding rounds with mandatory source URLs added on 14 companies.

### 2026.05.17 — Catalog v0 → v1

- Initial catalog of ~234 entities (heavy on humanoids + grippers).
- Audit identified 14 placeholder entries with wrong years /
  fabricated specs; replacements drafted in research/audit.md.
- Sources field made mandatory ("出处第一公民" principle).
