# Summo Quartile — Web Frontend

Next.js 16 dashboard for environmental, mineral, and operational intelligence in the Brazilian mining sector.

## Setup

```bash
cd web
npm install
npm run dev        # http://localhost:3000
npm run build      # production build
npx eslint src/    # lint
```

Requires the FastAPI backend running at `http://localhost:8000` (configured via `NEXT_PUBLIC_API_URL`).

```bash
cd ../api
uv run uvicorn api.main:app --reload
```

## Architecture

```
web/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout (fonts, metadata)
│   │   └── (dashboard)/            # Route group — all pages share sidebar + header
│   │       ├── layout.tsx          # Sidebar + header + chat widget
│   │       ├── error.tsx           # Global error boundary (retry + home link)
│   │       ├── page.tsx            # Home — KPIs, platform map, data sources
│   │       ├── explorar/           # Multi-dataset explorer with filters + detail
│   │       ├── empresa/            # CNPJ dossier + viability analysis
│   │       ├── decisoes/           # Risk analytics (8 tabs, lazy-loaded)
│   │       ├── due-diligence/      # DN COPAM 217/2017 compliance wizard
│   │       ├── concessoes/         # Filterable mining concessions table
│   │       ├── mapa/               # MapLibre geospatial (polygons, UCs, TIs)
│   │       ├── prospeccao/         # Opportunity ranking + portfolios
│   │       ├── inteligencia-comercial/  # PTAX, COMEX, CFEM, RAL, ANM
│   │       ├── mineradora-modelo/  # Simulated mine KPI demo
│   │       ├── monitoramento/      # Placeholder (Q3 2026)
│   │       └── gestao-interna/     # Placeholder (Q4 2026)
│   ├── components/
│   │   ├── sidebar-nav.tsx         # Desktop navigation + data freshness
│   │   ├── header.tsx              # Mobile hamburger nav
│   │   ├── chat-sidebar.tsx        # Claude chat widget (SSE streaming)
│   │   ├── data-table.tsx          # TanStack table (sort, paginate, export)
│   │   ├── mining-map.tsx          # MapLibre renderer (color-by, popups)
│   │   ├── parecer-accordion.tsx   # Lazy-loaded parecer text accordion
│   │   ├── record-detail.tsx       # Modal SEMAD record detail
│   │   ├── inline-record-detail.tsx # Inline SEMAD record detail
│   │   ├── multi-select.tsx        # Combobox multi-select with search
│   │   ├── filter-chips.tsx        # Active filter badges
│   │   ├── stat-card.tsx           # KPI card with optional trend
│   │   ├── risk-badge.tsx          # Color-coded risk level badge
│   │   ├── document-links.tsx      # SEMAD document link parser
│   │   ├── under-construction.tsx  # Placeholder card
│   │   └── ui/                     # 21 shadcn/ui primitives (Radix-based)
│   └── lib/
│       ├── api.ts                  # All API calls (~90 endpoints)
│       ├── format.ts               # Number/date formatting (Brazilian locale)
│       └── utils.ts                # cn() class merger
```

## Pages

| Route | Purpose | Key Data |
|-------|---------|----------|
| `/` | Executive dashboard | KPIs, trend charts, data sources |
| `/explorar` | Multi-dataset explorer | SEMAD, ANM, IBAMA, CFEM tables |
| `/empresa` | Company intelligence | CNPJ dossier + viability analysis |
| `/decisoes` | Risk analytics | 8 tabs: overview, trends, regional, heatmap, risk factors, COPAM |
| `/due-diligence` | Compliance evaluation | DN COPAM 217/2017 wizard |
| `/concessoes` | Mining concessions | Filterable table + detail panel |
| `/mapa` | Geospatial view | MapLibre polygons, UCs, TIs |
| `/prospeccao` | Opportunity ranking | Scoring, portfolios, municipalities |
| `/inteligencia-comercial` | Market intelligence | PTAX, COMEX, CFEM, RAL |
| `/mineradora-modelo` | Simulated mine demo | 7 sectors, 23 KPIs |

## Key Patterns

- **Lazy tab loading**: Decisoes page loads data per-tab on selection, not all at once
- **Shared filter QS builder**: `miningFilterQS()` in `lib/api.ts` for concessoes/mapa/export
- **Error boundary**: `error.tsx` catches unhandled errors across all dashboard routes
- **Parecer accordion**: Shared component lazy-loads PDF text from API on expand

## Stack

- Next.js 16.2.2 (App Router, `"use client"` components)
- Tailwind CSS v4 with CSS custom properties design system
- shadcn/ui (21 Radix-based primitives)
- Recharts (charts), MapLibre GL (maps), TanStack React Table (grids)
- Deployed on Vercel

## Known Limitations

- Filters reset on navigation (no URL-based state persistence yet)
- No request deduplication (no SWR/React Query)
- Chat messages lost on page reload
- Decisoes page is 1,398 LOC (large but functional, uses lazy loading)
- `data-table.tsx` has no error state prop
