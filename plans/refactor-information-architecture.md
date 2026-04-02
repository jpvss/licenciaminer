# Refactor: Information Architecture & Navigation

**Type:** refactor  
**Priority:** P0  
**Scope:** Navigation sidebar, home page, page naming  
**Estimated effort:** 1 focused session  

---

## Problem Statement

The current navigation groups pages by **internal business units** (Summo Ambiental, Direitos e Concessões, SQ Solutions, etc.). This mirrors the company org chart, not how users think about their work. A first-time user must learn the company's internal structure before they can navigate.

Additionally, "Painel Principal" (the home page) tries to be both a welcome mat and an executive dashboard simultaneously. It buries the most trust-building content (Fontes de Dados) inside an accordion, and mixes onboarding concerns with analytical content (trend charts, insights).

### Specific Issues

1. **Org-chart grouping** — "Summo Ambiental" means nothing to a customer
2. **Home page buried** under the first section header, not visually distinct
3. **Related pages split** — Consulta Empresa (Ambiental) and Concessões (Direitos) both answer "tell me about this entity"
4. **Prospecção + Inteligência Comercial** both serve market/opportunity personas but live in different sections
5. **No onboarding** — no walkthrough, no "start here", no app map
6. **Fontes de Dados hidden** in accordion — the #1 trust signal requires a click to see
7. **Internal branding visible** — "SQ Solutions", "Gestão Interna" are meaningless to customers
8. **Naming inconsistencies** — "Explorar Dados" (too generic), "Mapa Geoespacial" (jargon)

---

## Proposed Navigation Structure

### Before (current)

```
Summo Ambiental (orange)
  ├ Painel Principal        /
  ├ Explorar Dados          /explorar
  ├ Consulta Empresa        /empresa
  ├ Análise Decisões        /decisoes
  └ Due Diligence           /due-diligence

Direitos e Concessões (teal)
  ├ Base de Concessões      /concessoes
  ├ Mapa Geoespacial        /mapa
  └ Prospecção              /prospeccao

Mineral Intelligence (gold)
  ├ Inteligência Comercial  /inteligencia-comercial
  └ Monitoramento           /monitoramento (disabled)

SQ Solutions (teal)
  └ Mineradora Modelo       /mineradora-modelo

Gestão Interna (muted)
  └ Gestão Interna          /gestao-interna (disabled)
```

### After (proposed)

```
(no section header — standalone)
  └ Início                  /                    (Home icon)

Análise & Pesquisa (orange)
  ├ Consulta Empresa        /empresa             (Building2)
  ├ Explorador              /explorar            (Database)
  └ Análise de Decisões     /decisoes            (BarChart3)

Direitos Minerários (teal)
  ├ Mapa Interativo         /mapa                (Map)
  ├ Concessões              /concessoes          (FileSearch)
  └ Prospecção Mineral      /prospeccao          (TrendingUp)

Mercado & Inteligência (gold)
  ├ Inteligência Comercial  /inteligencia-comercial (Globe)
  └ Monitoramento           /monitoramento       (Search, disabled)

Conformidade (orange)
  └ Due Diligence           /due-diligence       (ShieldCheck)

Simulação (muted teal)
  └ Mineradora Modelo       /mineradora-modelo   (Factory)
```

### Changes Summary

| What | Before | After | Why |
|------|--------|-------|-----|
| Home position | Nested under "Summo Ambiental" | Standalone at top, no section header | Clear entry point, not buried |
| Home name | "Painel Principal" | "Início" | Universal Brazilian convention |
| Section names | Business unit names | User-intent names | Users don't know your org chart |
| Consulta Empresa position | 3rd in Ambiental | 1st in Análise & Pesquisa | Most-used page first |
| Explorar name | "Explorar Dados" | "Explorador" | Shorter, still clear |
| Mapa position | 2nd in Direitos | 1st in Direitos Minerários | Visual entry points draw clicks |
| Mapa name | "Mapa Geoespacial" | "Mapa Interativo" | "Geoespacial" is jargon |
| Concessões name | "Base de Concessões" | "Concessões" | Drop implied "Base de" |
| Prospecção name | "Prospecção" | "Prospecção Mineral" | Disambiguate |
| Due Diligence | Grouped with analysis | Own "Conformidade" section | Distinct wizard workflow |
| Mineradora Modelo | Under "SQ Solutions" | Under "Simulação" | Drop internal branding |
| Gestão Interna | Visible but disabled | **Removed entirely** | Internal tool, not customer-facing |
| Decisões name | "Análise Decisões" | "Análise de Decisões" | Proper Portuguese grammar |

---

## Home Page ("Início") Redesign

### Current Structure (page.tsx)

```
1. Hero (title + subtitle)
2. 4 KPI StatCards
3. TrendChart (2/3) + Insights panel (1/3)
4. Accordion: Fontes de Dados (collapsed)
5. Accordion: Metodologia (collapsed)
```

### Proposed Structure

```
1. Hero
   - Title: "Summo Quartile"
   - Subtitle: "Inteligência ambiental e mineral para mineração no Brasil"
   - 2 CTA buttons: [Consultar Empresa] [Explorar Mapa]

2. Números-Chave (4 KPI StatCards — same as current)
   - Total Decisões | Aprovação Mineração | Licenças IBAMA | Processos ANM

3. Mapa da Plataforma (new — the "walkthrough")
   - 3-column card grid with section headers matching nav groups
   - Each card: icon + page name + 1-line description + clickable link
   - Grouped:
     Column 1: Análise & Pesquisa
       • Consulta Empresa — Dossier completo por CNPJ ou CPF
       • Explorador — Acesso direto a 16+ bases de dados públicas
       • Análise de Decisões — Tendências, fatores de risco, padrões regionais
     Column 2: Direitos Minerários
       • Mapa Interativo — Concessões, UCs e Terras Indígenas em camadas
       • Concessões — Base pesquisável de títulos minerários
       • Prospecção Mineral — Scoring de oportunidades por potencial
     Column 3: Mercado & Conformidade
       • Inteligência Comercial — Câmbio, comércio exterior, CFEM, cotações
       • Due Diligence — Avaliação estruturada de conformidade ambiental

4. Fontes de Dados (ALWAYS VISIBLE — not accordion)
   - Same table as current: 16 sources, record counts, dates, status dots, links
   - This is the trust section — never hide it behind a click

5. Metodologia (accordion — expandable, same as current)
   - Detailed text about collection, processing, auditability
```

### What Moves OUT of Início

The **TrendChart** and **Insights panel** move to **Análise de Decisões** (`/decisoes`). Rationale:

- They're analytical content about licensing decisions — that's what `/decisoes` is for
- The Início page should be stable, informational, and fast — not a dashboard that competes with actual analysis pages
- `/decisoes` already has 7+ tabs of analysis; adding a summary "Visão Geral" tab at the front gives it a proper landing view
- Users who want the executive overview will navigate to Análise de Decisões, which is where that content naturally lives

### Implementation for Trend/Insights Move

In `/decisoes/page.tsx`:
- Add a new first tab: **"Visão Geral"** before the existing "Tendência" tab
- This tab shows: 4 KPI stat cards (same data) + TrendChart + Insights panel
- The `trend-chart.tsx` component stays in the same location, just imported from decisoes instead of home
- API calls `fetchOverviewStats`, `fetchOverviewTrend`, `fetchOverviewInsights` are reused

---

## File Changes

### Files to Edit

| File | Change |
|------|--------|
| `web/src/components/sidebar-nav.tsx` | Restructure NAV_SECTIONS array, rename labels, reorder items, remove Gestão Interna |
| `web/src/app/(dashboard)/page.tsx` | Redesign as Início hub — remove TrendChart/Insights, add platform map cards, make Fontes always visible |
| `web/src/app/(dashboard)/decisoes/page.tsx` | Add "Visão Geral" summary tab with trend chart + insights from old home page |

### Files to Move/Rename

None — all routes stay the same (`/`, `/explorar`, `/empresa`, etc.). Only the sidebar labels and page titles change.

### Files Unchanged

All other page files (`explorar/page.tsx`, `empresa/page.tsx`, `concessoes/page.tsx`, `mapa/page.tsx`, `prospeccao/page.tsx`, `inteligencia-comercial/page.tsx`, `due-diligence/page.tsx`, `mineradora-modelo/page.tsx`) — content stays identical, only nav labels that reference them change.

### Components Reused

| Component | Current Location | Reused In |
|-----------|-----------------|-----------|
| `TrendChart` | `web/src/app/(dashboard)/trend-chart.tsx` | Move import to `/decisoes`, keep file in place |
| `StatCard` | `web/src/components/stat-card.tsx` | Used in both Início (summary) and Decisões (Visão Geral tab) |
| `InsightCard` | Inline in `page.tsx` | Extract to shared component or duplicate in decisoes |

---

## Implementation Steps

### Step 1: Restructure Sidebar Navigation
**File:** `web/src/components/sidebar-nav.tsx`

Replace `NAV_SECTIONS` array (lines 30-73) with new structure:

```typescript
const NAV_SECTIONS: { label: string; color?: string; standalone?: boolean; items: NavItem[] }[] = [
  {
    label: "",
    standalone: true,
    items: [
      { href: "/", label: "Início", icon: Home },
    ],
  },
  {
    label: "Análise & Pesquisa",
    color: "text-brand-orange",
    items: [
      { href: "/empresa", label: "Consulta Empresa", icon: Building2 },
      { href: "/explorar", label: "Explorador", icon: Database },
      { href: "/decisoes", label: "Análise de Decisões", icon: BarChart3 },
    ],
  },
  {
    label: "Direitos Minerários",
    color: "text-brand-teal",
    items: [
      { href: "/mapa", label: "Mapa Interativo", icon: Map },
      { href: "/concessoes", label: "Concessões", icon: FileSearch },
      { href: "/prospeccao", label: "Prospecção Mineral", icon: TrendingUp },
    ],
  },
  {
    label: "Mercado & Inteligência",
    color: "text-brand-gold",
    items: [
      { href: "/inteligencia-comercial", label: "Inteligência Comercial", icon: Globe },
      { href: "/monitoramento", label: "Monitoramento", icon: Search, disabled: true },
    ],
  },
  {
    label: "Conformidade",
    color: "text-brand-orange",
    items: [
      { href: "/due-diligence", label: "Due Diligence", icon: ShieldCheck },
    ],
  },
  {
    label: "Simulação",
    color: "text-sidebar-foreground/40",
    items: [
      { href: "/mineradora-modelo", label: "Mineradora Modelo", icon: Factory },
    ],
  },
];
```

- Add `Home` to lucide imports
- Remove `Construction` icon import (Gestão Interna removed)
- Handle `standalone` sections: skip the section label `<p>` when `standalone: true`

### Step 2: Redesign Home Page as "Início"

**File:** `web/src/app/(dashboard)/page.tsx`

Major rewrite:

1. Update hero section:
   - Title: "Summo Quartile"
   - Subtitle: "Inteligência ambiental e mineral para mineração no Brasil"
   - Two `Link` buttons: "Consultar Empresa" → `/empresa`, "Explorar Mapa" → `/mapa`

2. Keep KPI cards section (lines 75-107) — same 4 StatCards

3. Replace TrendChart + Insights grid (lines 109-168) with **Platform Map**:
   - 3-column responsive grid (`sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3`)
   - Each column is a Card with section header matching nav group
   - Each item inside: `<Link>` with icon + name + description

   ```
   Análise & Pesquisa:
     Consulta Empresa — Dossier completo por CNPJ ou CPF
     Explorador — Acesso direto a 16+ bases de dados públicas
     Análise de Decisões — Tendências, fatores de risco, padrões regionais

   Direitos Minerários:
     Mapa Interativo — Concessões, UCs e Terras Indígenas em camadas
     Concessões — Base pesquisável com filtros e exportação CSV
     Prospecção Mineral — Scoring de oportunidades por potencial

   Mercado & Conformidade:
     Inteligência Comercial — Câmbio, comércio exterior, CFEM, cotações
     Due Diligence — Avaliação estruturada de conformidade ambiental
   ```

4. Make Fontes de Dados **always visible** (remove Accordion wrapper, keep table content):
   - Section header with Database icon
   - Full source table always rendered (no click to expand)

5. Keep Metodologia as accordion (less essential, OK to collapse)

6. Remove: `TrendChart` import, `fetchOverviewTrend`, `fetchOverviewInsights` calls, `InsightCard` component, trend/insights state

### Step 3: Add "Visão Geral" Tab to Análise de Decisões

**File:** `web/src/app/(dashboard)/decisoes/page.tsx`

1. Add new imports:
   ```typescript
   import { TrendChart } from "../trend-chart";  // relative import from sibling
   import { StatCard } from "@/components/stat-card";
   import { fetchOverviewStats, fetchOverviewTrend, fetchOverviewInsights, ... } from "@/lib/api";
   ```

2. Add state for overview data:
   ```typescript
   const [overviewStats, setOverviewStats] = useState<OverviewStats | null>(null);
   const [trend, setTrend] = useState<TrendPoint[] | null>(null);
   const [insights, setInsights] = useState<Insight[] | null>(null);
   ```

3. Add useEffect to fetch overview data (alongside existing fetches)

4. Add "Visão Geral" as first `TabsTrigger` + `TabsContent`:
   - 4 KPI StatCards (same as home)
   - TrendChart (2/3 width)
   - Insights panel (1/3 width) with InsightCard components
   - This becomes the default active tab

5. Move `InsightCard` component here (or extract to `@/components/insight-card.tsx`)

---

## What This Does NOT Change

- **No route changes** — all URLs stay the same
- **No API changes** — all endpoints stay the same
- **No page content changes** — only nav labels, home page layout, and decisoes gets an extra tab
- **No component library changes** — same shadcn/ui components
- **No data flow changes** — same fetch patterns

---

## Acceptance Criteria

- [ ] Sidebar shows new section structure with "Início" standalone at top
- [ ] "Gestão Interna" is removed from navigation
- [ ] All page labels match the renaming table above
- [ ] Home page shows: Hero with CTAs → KPIs → Platform Map → Fontes de Dados (visible) → Metodologia (accordion)
- [ ] Home page does NOT show TrendChart or Insights panel
- [ ] `/decisoes` has "Visão Geral" as first tab with trend chart + insights + KPI cards
- [ ] All existing pages still accessible at their current URLs
- [ ] No broken links in platform map cards
- [ ] Standalone "Início" item has no section header above it
- [ ] `next build` succeeds with zero errors
- [ ] Visual: Fontes de Dados table renders without requiring any click
