# Changelog — Web Frontend Quality Review

## 2026-04-01 — Systematic Quality Review (Phase 2)

Net LOC change: +143 / −143 = **0**
Files modified: 11 | Files created: 2

### Simplifications

- **Extract `ParecerAccordion` shared component** — Removed ~36 lines of duplicate code from `record-detail.tsx` and `inline-record-detail.tsx`. New `parecer-accordion.tsx` (57 LOC) lazy-loads parecer text on accordion open.
- **Extract `miningFilterQS()` shared helper** — Collapsed duplicate `concessoesQS()` and `geoQS()` query-string builders in `lib/api.ts` into a single function. Also simplified `concessoesExportUrl()` from 10 lines to 1.
- **Remove dead `hoverFeatureId` state** — Unused state variable in `mining-map.tsx`.

### Bug Fixes

- **Global error boundary** — Added `error.tsx` for the `(dashboard)` route group. Catches unhandled errors and shows retry + home link instead of crashing the app.
- **Sidebar memory leak** — `fetchFreshness()` in `sidebar-nav.tsx` had no cleanup. Added `cancelled` flag pattern to prevent setState on unmounted component.
- **Chat sidebar accessibility** — Added `aria-label="Mensagem para o assistente"` to chat textarea.

### Performance

- **Lazy tab loading on Decisoes** — Reduced initial API calls from 13 to 5. Remaining 8 calls fire on-demand when user selects a tab. Uses `lazyFetch` helper with controlled `activeTab` state.

### Quick Wins

- **Error retry button** (`page.tsx` home) — Error state now shows "Tentar novamente" button instead of static text.
- **Relative timestamps** (`page.tsx` home) — Data sources table shows "3h atrás", "ontem", "5d atrás" with tooltip for original date.
- **Hover lift on platform cards** (`page.tsx` home) — `transition-shadow hover:shadow-md` on platform map cards.
- **CNPJ auto-formatting** (`empresa/page.tsx`) — Input auto-formats as XX.XXX.XXX/XXXX-XX while typing. CPF (11 digits) remains unmasked.
- **"Ver no Mapa" cross-link** (`concessoes/page.tsx`) — Detail panel now has button linking to `/mapa?search={processo}`.
- **KPI progress bar** (`mineradora-modelo/page.tsx`) — Each KPI card shows a progress bar with % of target achieved.

### Not Implemented (Deferred)

High-priority items for next sprint:
- URL-based filter persistence across explorar, concessoes, mapa, prospeccao
- Due Diligence stepper + sessionStorage persistence
- Decisoes file splitting into per-tab sub-components
- Abort controllers on all useEffect fetches
- Data enrichment opportunities (RAL in Prospeccao, spatial overlaps in Concessoes)
