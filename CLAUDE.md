# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- `npm run dev` — Vite dev server on `0.0.0.0:3000`.
- `npm run build` — production build to `dist/`.
- `npm run preview` — serve the built bundle.
- `npm run lint` — type-check only (`tsc --noEmit`); there is no ESLint config and no test suite.
- `DISABLE_HMR=true npm run dev` — disables HMR and file watching (intended for agent edit sessions to prevent flicker; set by tooling, do not change `vite.config.ts` to alter this behavior).

Deployment is automated: pushes to `main` are built and published to GitHub Pages via `.github/workflows/deploy.yml`. Production `base` is `/RoboIndex/` (see `vite.config.ts`); all asset URLs must be resolved through `import.meta.env.BASE_URL` or `resolveImageUrl()` in `src/data/entities.ts` so they work both locally (`/`) and on Pages (`/RoboIndex/`).

## Architecture

Purely front-end React + Vite + Tailwind v4 + `motion/react` app. There is **no backend, no database, and no API layer** — it is a static knowledge-graph viewer for the embodied-AI / robotics landscape and must remain hostable on a static file server.

### Data flow (critical)

Data is decoupled from code. At runtime `loadEntities()` in `src/data/entities.ts`:

1. Fetches `public/data/index.json` — a manifest listing partitions.
2. Fetches every partition JSON (`hardware.json`, `software.json`, `ecosystem.json`, `players.json`) in parallel.
3. Flattens them into a single in-memory `Entity[]` registry, cached for the session.

`src/data/entities.ts` contains **only** the `Entity` / `Category` / `TopLevelGroup` types and the loader. Never hardcode entity data there — edit the JSON files under `public/data/` instead. Adding a new top-level partition requires updating both `index.json` *and* the `CATEGORY_MAP` / `Category` union in `entities.ts`.

Categories are Chinese strings and are load-bearing: they must match exactly across `entities.ts`, `index.json`, the JSON partition files, and any UI filter. The four top-level groups are `硬件 / 软件 / 生态与应用 / 参与实体` (see `CATEGORY_MAP` for the full category list per group).

### UI orchestration

`src/App.tsx` is the single orchestrator. It owns:
- The active `mainTab` (`全景架构 | 演进脉络 | 硬件 | 软件 | 生态与应用 | 参与实体`).
- The per-group selected `Category` (separate state per group so switching tabs preserves the previous category).
- The `leftId` / `rightId` entity selection and the `isComparing` flag that toggles the dual-wheel compare layout.
- `timelineFocusId` for cross-view navigation into the timeline.

View components under `src/components/` are intentionally dumb — they receive `mockData` (the loaded entity list) and callbacks. Don't introduce a global store; pass props through `App.tsx`. `handleNavigateToEntity` is the canonical way to deep-link to an entity from any view: it resolves the entity's category to the right tab and updates selection.

### Conventions worth preserving

- Animations must use `motion` from `motion/react` (not framer-motion directly).
- Layout uses precise Tailwind values (e.g. `w-[480px]`, `h-[720px]`); when resizing, update all related components together rather than mixing scales.
- `imageUrl` fields in JSON are typically repo-relative (`/images/hardware/<slug>.jpg`); always run them through `resolveImageUrl()` before rendering so the GitHub Pages base path is applied.
- i18n strings live in `src/i18n.tsx` (`DICT.zh` / `DICT.en`); UI text should use `t('key')` rather than literal strings when both languages are needed.

### Environment

`.env.example` declares `GEMINI_API_KEY` and `APP_URL`. These are injected by AI Studio at runtime; the app does not currently require them to render — they exist for future Gemini-backed features. Do not commit real keys.
