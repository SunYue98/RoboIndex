# `research/` — Staging area for RoboIndex data collection

This directory is **not shipped to GitHub Pages**. It's a reviewable scratchpad where new and audited entries live until the user approves them for merging into `public/data/`.

## Why this exists

`public/data/*.json` is the live data the site reads. We don't write to it directly during collection for two reasons:

1. **Reviewability.** The user wants to inspect a batch of new entries (and re-verify any auto-generated facts) before they ship.
2. **Source-attribution integrity.** Every entry that lands in `public/data/` must carry at least one fact-checkable source URL that surfaces on the live site. This staging area enforces that contract before anything merges.

## Files in this directory

| File | What it holds |
|---|---|
| `README.md` | This file. Workflow + tier definitions. |
| `inventory.md` | Frozen snapshot of `public/data/` at the time collection started — per-category counts, real-vs-placeholder split, known broken refs. |
| `staging.json` | The data table. Array of objects matching the `Entity` interface in `src/data/entities.ts`, **plus** a `_provenance` block on each entry. |
| `sources.md` | Per-entry source list grouped by id. Also holds a "needs-source" parking lot for leads that couldn't be verified to A/B tier. |
| `audit.md` | Existing entries flagged for replacement or fact-correction, with proposed action. Includes the 14 known placeholders + 3 broken image refs as of Phase 0. |

## Confidence tiers

Every fact-claim in `staging.json` is anchored to one or more sources. Sources are classified:

- **A — Primary.** Official product page / official spec sheet / arxiv paper. The party who built the thing is telling us about it.
- **B — Secondary authoritative.** Wikipedia with inline citation, IEEE Spectrum, TechCrunch (with reporter byline), manufacturer datasheet hosted by a distributor. Third-party but reputable and traceable.
- **C — Secondary, weak.** Blog post, news article without primary citation, vendor marketing without specs. Records the existence of a claim but not enough to anchor it.
- **D — Unverified.** LLM-recalled, no source confirmed. **Never enters `staging.json`.** Parked in `sources.md` under "Needs source" so leads aren't lost.

**Promotion rule:** an entry only enters `staging.json` if it has **≥1 A or B source**. C-only entries stay in the needs-source pile until someone finds an A/B.

## Entity shape in `staging.json`

Standard `Entity` shape (see `src/data/entities.ts`) plus a `_provenance` block:

```json
{
  "id": "stg-sw-openvla",
  "name": "OpenVLA",
  "company": "Stanford / Toyota Research / UC Berkeley",
  "category": "基础模型",
  "imageUrl": "https://example.com/openvla.png",
  "year": "2024",
  "isNew": true,
  "specs": {
    "parameters": "7B",
    "architecture": "Llama 2 + DINOv2/SigLIP",
    "paradigm": "Vision-Language-Action",
    "status": "Open Source"
  },
  "tags": ["Vision-Language", "Open Source"],
  "paperInfo": {
    "authors": "Moo Jin Kim et al.",
    "arxivUrl": "https://arxiv.org/abs/2406.09246",
    "codeUrl": "https://github.com/openvla/openvla"
  },
  "_provenance": {
    "confidence": "A",
    "sources": [
      { "url": "https://arxiv.org/abs/2406.09246", "title": "OpenVLA: An Open-Source Vision-Language-Action Model", "type": "paper", "fetched": "2026-05-19" },
      { "url": "https://openvla.github.io/", "title": "OpenVLA project page", "type": "official", "fetched": "2026-05-19" }
    ],
    "fields_verified": ["year", "specs.parameters", "specs.architecture", "paperInfo.arxivUrl"],
    "fields_uncertain": [],
    "notes": ""
  }
}
```

### Convention: staging IDs

All new entries use **`stg-`-prefixed ids** to avoid collisions with live data. On merge, the prefix is stripped and the id is reconciled with the live partition's id space.

For Phase 6 backfill, existing entries are referenced by their **original** id (no `stg-` prefix) — they aren't new, we're just attaching sources.

## Workflow

```
WebSearch (discover curator page)
    ↓
WebFetch (extract candidate rows with a tight prompt)
    ↓
Cross-check each candidate's official page → assign A/B/C/D tier
    ↓
A or B?  → write to staging.json + add to sources.md (with _provenance.sources)
C or D?  → write to sources.md "Needs source" section, leave out of staging.json
    ↓
At end of phase: run validation scripts (see plan), summarize for user
```

## Validation

Two scripted invariants checked at end of every phase:

```bash
# Every staging.json entry has _provenance with ≥1 A/B source
python3 -c "
import json
data = json.load(open('research/staging.json'))
bad = [d['id'] for d in data
       if not d.get('_provenance') or
          d['_provenance'].get('confidence') not in ('A','B') or
          not d['_provenance'].get('sources')]
print('OK' if not bad else f'BAD: {bad}')
"

# Forward-compat with Entity interface (every staging entry maps cleanly after stripping _provenance)
python3 -c "
import json
required = {'id','name','company','category','imageUrl','year','isNew','specs'}
data = json.load(open('research/staging.json'))
bad = [d.get('id','?') for d in data if not required.issubset(d.keys())]
print('OK' if not bad else f'MISSING REQUIRED FIELDS: {bad}')
"
```

Spot-check: pick 10 random staging entries, open each cited source, confirm spec/year/company match. Any miss → demote the entry and note the lesson here.

## Merge (Phase 8)

When the user approves, a one-shot script will:
1. Strip `_provenance` from each staging entry, promoting `_provenance.sources` (minus `fetched`) to a public `sources` field.
2. Reconcile `stg-`-prefixed ids with the live partition's id space.
3. Apply audit corrections from `audit.md` (remove placeholders, swap in replacements).
4. Write the result back to `public/data/*.json`.

That script doesn't exist yet — built in Phase 8 once the staging contents are stable.
