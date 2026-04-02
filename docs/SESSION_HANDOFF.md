# Session Handoff — 2026-04-01

## Current State

**Data collection: COMPLETE.** 16+ sources, ~1 million records, all enriched.
**Next.js frontend: DEPLOYED on Vercel.** 10 functional pages + 2 placeholders.
**FastAPI backend: DEPLOYED on Railway.** 13 routers, ~55 endpoints.
**Streamlit app: RETAINED as internal tool.** 15 pages, runs locally via `uv run streamlit run app/app.py`.

## Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Next.js 16     │────▶│   FastAPI         │────▶│   DuckDB         │
│   (Vercel)       │     │   (Railway)       │     │   (parquet)      │
│   10 pages       │     │   13 routers      │     │   16+ sources    │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

- **Frontend**: `web/` — Next.js App Router, Tailwind v4, shadcn/ui, Recharts, MapLibre
- **Backend**: `api/` — FastAPI, DuckDB, 13 routers (~2,933 LOC)
- **Data pipeline**: `src/licenciaminer/` — Python collectors, processors, CLI
- **Streamlit**: `app/` — Internal tool, 15 pages

## What Was Done This Session (Quality Review)

Systematic page-by-page review of the Next.js app:
- **Phase 1**: Full app map — 12 pages, 14 components, 13 API routers, 9 DuckDB views, 8 user flows, 48 enhancement items ranked by impact × feasibility
- **Phase 2**: Implemented 12 items (net zero LOC change: +143/−143)
- **Phase 3**: Documentation consolidation (this file, README, CHANGELOG, plan updates)

### Key Changes
- Global error boundary (`error.tsx`)
- Lazy tab loading on Decisoes (13→5 API calls on mount)
- Extracted shared ParecerAccordion component
- Extracted shared `miningFilterQS()` helper
- Fixed memory leak in sidebar fetchFreshness
- CNPJ auto-formatting mask
- Retry button on error states
- Relative timestamps on data sources
- Cross-page links (Concessoes → Mapa)
- KPI progress bars (Mineradora Modelo)
- Chat sidebar accessibility (`aria-label`)

## Next Session Priority

### 1. URL-based filter persistence (G.3)
Filters reset on navigation across explorar, concessoes, mapa, prospeccao. Implement `useSearchParams` pattern reusable across all four pages.

### 2. Due Diligence UX (5.1 + 5.2)
Add stepper progress indicator and sessionStorage persistence for the compliance wizard.

### 3. Data Opportunities
- Enrich Prospeccao scores with RAL production data
- Flag spatial overlaps (UC/TI) in Concessoes table
- Show filiais in empresa dossier

### 4. Remaining Quick Wins
See plan file: `.claude/plans/crispy-growing-thunder.md` — 12 low-priority quick wins skipped during Phase 2.

## Known Issues

### Frontend
- Filters reset on navigation (no URL-based state)
- Chat messages lost on page reload
- Decisoes page is 1,398 LOC (functional but could be split)
- No request deduplication (no SWR/React Query)

### Data
- 13.4% of mining PDFs are scanned (no extractable text) — mostly pre-2020
- ~30% invalid CNPJs from source (handled gracefully)
- ANM↔SEMAD join via CNPJ: 37.6% match rate
- CECAV caves: shapefile URL 404 (blocked externally)
- ANA water rights: portal returning 504 (blocked externally)

## Key Files

| File | Purpose |
|------|---------|
| `web/README.md` | Frontend setup, architecture, patterns |
| `docs/DATA_REGISTRY.md` | Every data source with refresh commands |
| `CLAUDE.md` | Project context for Claude Code |
| `.claude/plans/crispy-growing-thunder.md` | Full app map + enhancement plan with Phase 2 status |
| `plans/feat-streamlit-parity-next.md` | Streamlit→Next.js parity audit |

## CLI Reference

```bash
# Frontend
cd web && npm run dev              # Dev server
cd web && npm run build            # Production build

# Backend
uv run uvicorn api.main:app --reload   # FastAPI dev

# Data collection
uv run python -m licenciaminer collect --all
uv run python -m licenciaminer collect mg --scrape --all-activities
uv run python -m licenciaminer collect anm --uf MG

# Quality
cd web && npx eslint src/          # Frontend lint
uv run pytest tests/               # Backend tests
uv run ruff check src/ app/        # Python lint
```
