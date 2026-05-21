# Contributing to RoboIndex

This guide is written so that **both humans and AI agents** can submit
changes without ambiguity. Every section either gives an exact recipe
(file paths, JSON shape, validation commands) or points to one.

> **TL;DR for agents.** Edit `public/data/<partition>.json`, then run
> `bash scripts/precommit.sh`. It validates, regenerates the API layer,
> updates the version stamp, and stages everything. Commit with a
> structured message, then ask the human to push.

---

## 1. What you can contribute

| Contribution type | Recipe (link to section) |
|---|---|
| Add a new entity (any of 21 categories) | [§3.1](#31-add-a-new-entity) |
| Update existing entity (year, specs, sources) | [§3.2](#32-update-an-existing-entity) |
| Add typed relations between entities | [§3.3](#33-add-typed-relations) |
| Migrate freeform `specs` → `sourcedSpecs` claims | [§3.4](#34-migrate-specs-to-claims) |
| Add a funding round to a 产业 entity | [§3.5](#35-add-a-funding-round) |
| Add a person + their founder/employed relations | [§3.6](#36-add-a-person) |
| Fix a dead source URL | [§3.7](#37-fix-a-dead-source-url) |
| Add an image (real product photo / logo) | [§3.8](#38-add-an-image) |

---

## 2. Hard rules

These are non-negotiable. PRs violating them will be rejected.

1. **Every public-facing fact must have a source URL.** Sources are
   first-class. The project lead's quote: "钱的问题要谨慎，不要让我惹上
   麻烦" — funding claims especially must cite a real article or filing.
2. **Source-tier discipline**: only `official` / `paper` / `wiki` /
   `news` / `datasheet` URLs. No blog posts without primary citations,
   no AI-generated content, no Unsplash stock.
3. **No fabrication.** If you can't verify a number/year/affiliation
   from a real source, omit it. Skip > make-up.
4. **Schema validation must pass with zero errors.** Run
   `validate_schema.py` before committing.
5. **JSON must remain valid and importable.** UTF-8, 2-space indent,
   `ensure_ascii=False` (so Chinese characters are readable in diffs).
6. **Never push to `origin/main` directly.** Always go via PR. The
   project lead has historically preferred "commit but don't push" —
   ask before pushing.
7. **Don't `git add` everything blindly.** Stage specific files. Never
   commit `.env`, `raw_images/`, `research/_health_cache/`,
   `research/_preview/`.

---

## 3. Recipes

### 3.1. Add a new entity

**File**: `public/data/<partition>.json` where partition is one of:

| Top-level group | partition | Allowed categories |
|---|---|---|
| 硬件 | `hardware` | 整机平台, 机械臂, 灵巧手 & 夹爪, 关节模组, 核心零部件, 传感器, 能源动力, 数采 & 遥操, 计算平台 |
| 软件 | `software` | 基础模型, 算法框架, 控制算法, 仿真平台, 数据集, 评测基准 |
| 生态与应用 | `ecosystem` | 开发生态, 应用场景 |
| 参与实体 | `players` | 资本, 产业, 实验室, 人物 |

**Minimum entity shape**:

```json
{
  "id": "stable-kebab-case-id",
  "name": "Display Name",
  "company": "Company / Org / Affiliation",
  "category": "整机平台",
  "imageUrl": "",
  "year": "2025",
  "isNew": true,
  "specs": { "freeform": "key-value pairs OK here" },
  "tags": ["China", "Humanoid"],
  "sources": [
    { "title": "Official product page", "url": "https://example.com/x", "type": "official" }
  ]
}
```

**Optional / recommended fields**:

| Field | Shape | When to use |
|---|---|---|
| `orgInfo` | `{description, location, website}` | For 产业 / 实验室 / 资本 / 人物 entities |
| `paperInfo` | `{abstract, authors, arxivUrl, codeUrl, projectUrl}` | For 基础模型 / 数据集 / 评测基准 |
| `relations` | `[{targetId, role, source?, asOf?, isInverse?}]` | Typed edges — see §3.3 for allowed roles |
| `sourcedSpecs` | `{key: {value, source?, asOf?, confidence?}}` | Typed claims — see §3.4 |
| `fundingRounds` | `[{round, year, amount, leadInvestor, investors[], source}]` | Companies — see §3.5 |
| `seriesId`, `seriesOrder`, `seriesLabel` | strings | For product generations (Optimus Gen 1 → 2 → 3) |
| `websiteUrl` | URL string | For the "访问官网" button on the card |

**ID conventions**: lowercase, kebab-case, prefix by partition role
(`ind-` for company, `vc-` for VC, `lab-` for academic lab, `person-`
for people, `f`/`a`/`h`/`s`/`cp`/`j`/`c`/`pwr`/`d`/`sensor-` for
hardware short codes per existing convention).

**Workflow**:

```bash
# 1. Find the right partition and add entity to the JSON array
# 2. Validate
python3 research/_tools/validate_schema.py
# 3. Regenerate API layer
python3 research/_tools/build_api.py
# 4. If no real image, generate the synthetic placeholder card
python3 research/_tools/generate_synthetic_cards.py
# 5. Update health report
python3 research/_tools/health_report.py
# 6. Commit
git add public/data/<partition>.json public/api/ public/images/_synthetic/<id>.png research/HEALTH.md
```

Or run `bash scripts/precommit.sh` which does steps 2-5 in one go.

---

### 3.2. Update an existing entity

Same files. Specifically common updates:

- **Add a missing source**: append to `entity.sources[]`.
- **Fix a wrong year**: update `entity.year` and add a source citing the
  correct year.
- **Refine specs**: update `entity.specs[key]` or — preferably — add a
  typed `entity.sourcedSpecs[canonical_key]` per [§3.4](#34-migrate-specs-to-claims).
- **Update funding stage / status**: edit `entity.specs.status`.

After change, run `scripts/precommit.sh` and commit.

---

### 3.3. Add typed relations

**Allowed `role` values** (canonical authoring side noted):

| Role | Direction (authored on) | Meaning |
|---|---|---|
| `manufacturer` | hardware → company | "I am made by them" |
| `invested-in` | VC → company | "I invested in them" |
| `founder-of` | person → org | "I founded this" |
| `employed-at` | person → org | "I work here" |
| `alumni-of` | person → institution | "I attended" |
| `advised-by` | person → person | "X advised Y" |
| `competitor` | symmetric | both sides author |
| `customer-of` | customer → supplier | |
| `supplier-to` | supplier → customer | |
| `subsidiary-of` | subsidiary → parent | |
| `affiliated-with` | symmetric | for lab affiliations |
| `series-member` | symmetric | for product generation chains |
| `tech-base` | dependent → base | software dependencies / component use |
| `trained-on` | model → dataset | |
| `deployed-at` | product → application | |
| `related` | symmetric fallback | only when no other role fits |

**Authoring rule**: each edge should be authored once on its canonical
side. The UI builds the reverse view automatically. (You can still
mark inverse edges with `isInverse: true` — see existing data for
examples.)

**JSON shape**:

```json
"relations": [
  { "targetId": "ind-figure", "role": "founder-of" },
  { "targetId": "lab-bair-autolab", "role": "alumni-of",
    "source": { "title": "CV", "url": "https://...", "type": "official" } }
]
```

Per-edge `source` is optional but recommended for non-obvious relations
(e.g., a person's claimed founding role).

---

### 3.4. Migrate `specs` → `sourcedSpecs`

The canonical schema per category is in `src/data/categoryClaimSchema.ts`.
Each entry declares a `key`, `label`, optional `unit`, `type`, and
`aliases`.

Example for 整机平台:

```json
"sourcedSpecs": {
  "height_cm":  { "value": 172, "source": { "url": "https://...", "title": "..." }, "asOf": "2024" },
  "weight_kg":  { "value": 60,  "source": { "url": "https://...", "title": "..." } },
  "dof":        { "value": 28,  "source": { "url": "https://..." } }
}
```

For bulk migration of an existing entity, the easiest path is:

```bash
python3 research/_tools/migrate_specs_to_claims.py
```

It walks all entities, parses values strictly (rejects relative claims,
converts imperial → metric, validates plausibility ranges), and wraps
matched values as Claims with the entity's first source as default.

**Do NOT** add a Claim with no `source` if the entity has no
entity-level sources — that violates [§2 rule 1](#2-hard-rules).

---

### 3.5. Add a funding round

**Mandatory shape** (every field except optionals):

```json
"fundingRounds": [
  {
    "round": "Series B",
    "year": "2024-02",
    "amount": "$675M",
    "leadInvestor": "Microsoft",
    "investors": [
      { "name": "Microsoft", "id": "stg-vc-msft" },
      { "name": "NVIDIA", "id": "ind1" }
    ],
    "valuation": "$2.6B post-money",
    "source": {
      "title": "Figure raises $675M",
      "url": "https://www.figure.ai/news/figure-raises-675m",
      "type": "official"
    }
  }
]
```

- `source` is **mandatory** — no round goes in without one.
- Set `investors[].id` to the existing VC/company entity id where one
  exists; leave `id` blank for unmatched investors (rendered as plain
  text).
- After committing, run
  `python3 research/_tools/apply_funding_rounds.py` to derive the
  reverse `portfolio` view on each VC entity.

---

### 3.6. Add a person

**File**: `public/data/players.json`. **Category**: `人物`. **ID**:
`person-<firstname>-<lastname>` (lowercase, hyphen-separated).

See `research/_tools/seed_persons.py` for 20 working examples.
Minimum shape:

```json
{
  "id": "person-jane-doe",
  "name": "Jane Doe",
  "company": "Acme Robotics",
  "category": "人物",
  "imageUrl": "",
  "year": "2020",
  "isNew": false,
  "specs": { "role": "CTO", "expertise": "Robot learning" },
  "orgInfo": { "description": "...", "location": "City, Country" },
  "tags": ["人物"],
  "sources": [{ "title": "Wikipedia", "url": "https://...", "type": "wiki" }],
  "relations": [
    { "targetId": "ind-acme", "role": "founder-of" },
    { "targetId": "ind-acme", "role": "employed-at" }
  ]
}
```

After commit, regenerate the synthetic card:
```bash
python3 research/_tools/generate_synthetic_cards.py
```

---

### 3.7. Fix a dead source URL

1. Identify the dead URL from the latest health report
   (`research/HEALTH.md` § Dead source URLs).
2. Find a replacement: ideally an archive.org snapshot or an
   alternative authoritative URL.
3. Edit the relevant `sources[]` entry in `public/data/<partition>.json`.
4. Run `python3 research/_tools/check_url_liveness.py --full` to
   confirm the new URL works.
5. `scripts/precommit.sh` + commit.

---

### 3.8. Add an image

**Workflow**:

```bash
# 1. Drop the raw image into the gitignored staging dir
mkdir -p raw_images
cp ~/Downloads/some-robot.jpg raw_images/<entity-id>.jpg
# 2. Process (crop to 1:1, resize to 1000×1000, compress)
python3 research/_tools/process_image.py raw_images/<entity-id>.jpg --entity <entity-id>
# For a logo (transparent PNG, padded not cropped):
python3 research/_tools/process_image.py raw_images/<id>.png --entity <id> --format png --pad
# Add --remove-bg if the source has a non-white background and you want it isolated
# 3. Update the entity's imageUrl field in the relevant partition JSON
# 4. Validate + commit
```

See `research/IMAGE_SPEC.md` for the 4 prototype patterns
(A: product hero, B: synthetic card, C: pure logo, D: deployment scene).

---

## 4. Pre-commit checklist

Run `bash scripts/precommit.sh`. It will:

1. `validate_schema.py` — must return 0 errors. Warnings OK.
2. `build_api.py` — regenerates `public/api/*.json,csv,md`.
3. `version_bump.py` — updates `dataset_version` + `snapshot_sha`.
4. `health_report.py` — refreshes `research/HEALTH.md`.
5. Stages: `public/data/*.json`, `public/api/*`, `research/HEALTH.md`.

If any step fails, the script exits non-zero. Fix and re-run.

---

## 5. Commit message format

```
<type>(<scope>): <subject>

<body — what changed and why>

<footer with Co-Authored-By if AI-generated>
```

`<type>`: `data` (new/updated entities), `feat` (new feature), `fix`
(bug or data correction), `docs` (CONTRIBUTING/README/HEALTH only),
`chore` (tool/script).

`<scope>`: rough area — `hardware`, `players`, `schema`, `api`, etc.

For AI-generated commits, include:
```
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## 6. Pull request

Use `.github/pull_request_template.md` (auto-populated when opening a
PR via the GitHub web UI). The template asks for change-type tickboxes,
affected entity IDs, source URLs, and validation evidence.

For PRs from automation, the template's "Agent metadata" section asks
for the agent model + prompt template — this is for auditability, not
gating.

---

## 7. Agent prompt templates

These are copy-paste-ready prompts for spawning sub-agents to make
common contributions. Each is self-contained: the spawned agent
shouldn't need additional context beyond what's in the prompt.

### Add a new humanoid platform

```
You are contributing to RoboIndex (a static knowledge graph of the
embodied-AI ecosystem). Read CONTRIBUTING.md if you have access to
the repo.

Task: Add the following humanoid platform as a new entity in
public/data/hardware.json with category="整机平台":

- Product name: <X>
- Manufacturer: <Y> (id = <ind-y> if exists, else "")
- Release year: <YYYY>
- Specs to source: height_cm, weight_kg, dof, payload_kg, top_speed_mps
- Required: at least 1 official source URL + 1 secondary (Wikipedia,
  IEEE Spectrum, Robot Report). Source URLs must be live.

After editing:
1. Run validate_schema.py — must return 0 errors
2. Run build_api.py
3. Commit with format: `data(hardware): add <X> humanoid (<manufacturer>)`

Do NOT push. Report the diff and ask for review.
```

### Add a funding round

```
Task: Add the following funding round to public/data/players.json
on entity id <ind-company-id>:

- Round: <Seed/Series A/B/...>
- Year: <YYYY-MM>
- Amount: <as-stated, e.g. "$50M">
- Lead investor: <name>
- Co-investors: <comma-separated names, mark IDs where they exist>
- Source URL: <must be a press release or major news outlet>

The source field is mandatory. Reject the task if the source URL
can't be verified.

After:
1. Add round to ind-<id>.fundingRounds[]
2. Run apply_funding_rounds.py to derive VC portfolio views
3. validate_schema → build_api → commit:
   `data(players): add <X> Series B for <company>`
```

### Add a person

```
Task: Add <person name> as a new 人物 entity per CONTRIBUTING.md §3.6.

Required:
- name + Chinese name if applicable
- current affiliation (company id)
- one role: Founder & CEO / Professor / etc.
- expertise: 1-line summary
- ≥1 source (Wikipedia + official bio preferred)
- relations: founder-of and/or employed-at to existing entities

Use seed_persons.py as the reference example.

After editing players.json:
1. Run validate_schema.py
2. generate_synthetic_cards.py (creates the title card)
3. Commit: `data(players): seed person-<name>`
```

### Audit and refresh URL liveness

```
Task: Run check_url_liveness.py --full and report:
- How many URLs are dead (4xx).
- For each dead URL, try to find a working replacement
  (archive.org snapshot OR alternative authoritative URL).
- Patch the relevant sources[] entries in public/data/*.json.
- Re-run validate_schema → build_api → health_report.
- Commit each fix with: `fix(<scope>): replace dead source for <entity>`
```

---

## 8. What we DON'T accept

- Entities without sources (no fabrication).
- "Coming soon" / unreleased products with no announcement source.
- Marketing copy in `orgInfo.description` ("revolutionary" / "world's
  first" without citation).
- Duplicate entries (run `validate_schema.py` — it catches canonical
  name duplicates).
- AI-generated images (per `research/IMAGE_SPEC.md` reverse list).
- Entity removal without a paper-trail in the commit message
  explaining why.

---

## 9. Where to ask

- Bug or feature: GitHub issue.
- Data question: open a draft PR with the question in the description.
- For agents: if the recipe is unclear, fail-fast and open a draft PR
  noting the ambiguity — don't guess.
