# feat: Mineradora Modelo — AI Mining Value Chain Showcase

> **Type:** Enhancement | **Priority:** P0 | **Complexity:** High
> **Page:** `/mineradora-modelo` | **Deploy:** Vercel (Next.js)

---

## Overview

Revamp the Mineradora Modelo page from a simple KPI dashboard into a comprehensive **AI Mining Value Chain Showcase** — a commercial product that demonstrates how AI can improve every stage of a mining operation. This becomes the primary sales tool for Summo Quartile's consulting practice, mapping activities, bottlenecks, AI use cases, and implementation roadmaps across 7 mining modules.

The page transforms from "simulated KPI viewer" into "interactive AI maturity diagnostic and consulting entry point."

## Problem Statement / Motivation

**Current state:** The page shows 24 KPIs across 7 tabs with trend charts. It demonstrates data visualization capability but does NOT:
- Explain *what* AI can do for each mining stage
- Map activities and bottlenecks that AI can address
- Show expected ROI or business impact
- Provide a maturity assessment framework
- Offer a consulting engagement pathway
- Generate leads for the consulting business

**Why this matters:** This page is Summo Quartile's commercial hook. Mining executives and plant managers need to see:
1. That SQ understands their operation (activity maps + KPIs)
2. That AI has concrete, measurable impact (use cases + ROI)
3. Where they stand vs. industry best practice (maturity assessment)
4. How to get started (roadmap + CTA)

**Market context:** AI in mining is a US$30B+ market (2024) growing at 41.9% CAGR. Only 5% of companies generate substantial value from AI at scale. The consulting opportunity is massive — most companies need external help for change management, tool selection, and implementation.

---

## Proposed Solution

### Architecture: Per-Module Content System

Each of the 7 mining modules becomes a rich, multi-section page with 5 content areas:

```
┌─────────────────────────────────────────────────────┐
│ OVERVIEW (above tabs)                                │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────────┐  │
│ │ Maturity    │ │ Total ROI   │ │ Recommended    │  │
│ │ Radar Chart │ │ Opportunity │ │ Starting Point │  │
│ └─────────────┘ └─────────────┘ └────────────────┘  │
├─────────────────────────────────────────────────────┤
│ [Tab1] [Tab2] [Tab3] [Tab4] [Tab5] [Tab6] [Tab7]   │
├─────────────────────────────────────────────────────┤
│ MODULE CONTENT (per tab)                             │
│                                                      │
│ ┌─ Section Nav ──────────────────────────────────┐  │
│ │ KPIs | Atividades | IA | Maturidade | Roadmap  │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ § KPI Dashboard (existing, enhanced)                 │
│   - KPI cards with target gauge + sparkline          │
│   - "Projeção com IA" dashed overlay on charts       │
│                                                      │
│ § Atividades & Gargalos (NEW)                        │
│   - Horizontal process flow with 4-6 steps           │
│   - Bottleneck indicators (red badges)               │
│   - Click to expand activity details                 │
│                                                      │
│ § Casos de Uso de IA (NEW)                           │
│   - Card grid with AI use cases                      │
│   - ROI badge, complexity indicator, time to value   │
│   - Links to affected KPIs                           │
│                                                      │
│ § Avaliação de Maturidade (NEW)                      │
│   - 5-level scale visualization                      │
│   - Current level highlighted for model company      │
│   - Per-level criteria checklist                     │
│                                                      │
│ § Roadmap de Implementação (NEW)                     │
│   - Phased timeline (3 phases)                       │
│   - Deliverables, duration, dependencies             │
│   - "Solicitar Diagnóstico" CTA                      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Data Model (TypeScript)

```typescript
// web/src/app/(dashboard)/mineradora-modelo/lib/types.ts

/** Process step in the activity map */
interface ActivityStep {
  id: string;
  nome: string;
  descricao: string;
  status: "ok" | "gargalo" | "oportunidade";
  detalhes: string;          // expanded view text
  kpisAfetados: string[];    // links to KPI names
}

/** AI use case card */
interface AIUseCase {
  id: string;
  titulo: string;
  descricao: string;
  categoria: "computer-vision" | "predictive" | "optimization" | "nlp" | "automation" | "digital-twin";
  roiEstimativa: string;     // e.g. "5-15% redução de custo"
  complexidade: "baixa" | "media" | "alta";
  tempoValor: string;        // e.g. "3-6 meses"
  prerequisitos: string[];
  kpisAfetados: string[];
  exemplosReais: string[];   // e.g. "Rio Tinto — 130+ caminhões autônomos"
}

/** Maturity level definition */
interface MaturityLevel {
  nivel: 1 | 2 | 3 | 4 | 5;
  nome: string;              // e.g. "Reativo", "Descritivo", "Preditivo", "Prescritivo", "Autônomo"
  descricao: string;
  criterios: string[];       // checklist items for this level
}

/** Implementation roadmap phase */
interface RoadmapPhase {
  fase: number;
  titulo: string;            // e.g. "Diagnóstico", "Piloto", "Escala"
  duracao: string;           // e.g. "4-6 semanas"
  entregas: string[];
  dependencias: string[];
}

/** Complete module content */
interface MiningModule {
  key: string;               // e.g. "planejamento"
  nome: string;              // e.g. "Planejamento de Mina"
  icon: string;              // lucide icon name
  cor: string;               // accent color CSS variable
  descricao: string;         // module overview paragraph
  atividades: ActivityStep[];
  casosIA: AIUseCase[];
  maturidade: {
    nivelAtual: 1 | 2 | 3 | 4 | 5;  // model company's current level
    niveis: MaturityLevel[];
  };
  roadmap: RoadmapPhase[];
}
```

---

## Technical Approach

### Phase 1: Foundation — Data Model + Content Pilot (1 module)

Build the complete content system and validate with one module before scaling.

**Tasks:**
- [ ] Create type definitions in `mineradora-modelo/lib/types.ts`
- [ ] Create content data file for **Operação de Mina** module (most relatable to executives) in `mineradora-modelo/lib/data/operacao.ts`
- [ ] Implement URL-based tab state with `useSearchParams` (copy `inteligencia-comercial` pattern)
- [ ] Add `Suspense` boundary for search params
- [ ] Implement cross-module Overview section above tabs:
  - Maturity radar chart (Recharts `RadarChart`)
  - Total ROI opportunity card
  - Recommended starting module card

**New files:**
```
web/src/app/(dashboard)/mineradora-modelo/
  lib/
    types.ts                    # TypeScript interfaces
    data/
      operacao.ts               # Pilot module content
      modules-index.ts          # Module registry + overview data
  components/
    overview-section.tsx        # Cross-module summary with radar chart
    module-section-nav.tsx      # Sticky in-tab section navigation
```

**Success criteria:**
- Types compile with no errors
- Overview radar chart renders with placeholder data for all 7 modules
- URL state works: `/mineradora-modelo?modulo=operacao` loads correct tab

---

### Phase 2: New Section Components (4 components)

Build the 4 new section components using the pilot module's data.

**Tasks:**

#### 2a. Activity Map Component
- [ ] Create `activity-map.tsx` — horizontal process flow
- [ ] Each step: rounded card with icon, name, status badge
- [ ] Status colors: `ok` = muted, `gargalo` = destructive, `oportunidade` = brand-teal
- [ ] Click to expand: shows `detalhes` + affected KPIs as links
- [ ] Responsive: horizontal scroll on mobile, wrap on desktop

```tsx
// Conceptual structure
<div className="flex gap-3 overflow-x-auto pb-2">
  {atividades.map((step, i) => (
    <Fragment key={step.id}>
      {i > 0 && <ArrowRight className="shrink-0 text-muted-foreground" />}
      <ActivityCard step={step} onExpand={...} />
    </Fragment>
  ))}
</div>
```

#### 2b. AI Use Cases Component
- [ ] Create `ai-use-cases.tsx` — card grid of AI applications
- [ ] Each card: title, description, category icon/badge, ROI badge, complexity indicator (dots or bars), time to value, affected KPIs tags
- [ ] Category filter chips at top (Computer Vision, Predictive, Optimization, NLP, etc.)
- [ ] Expandable detail with prerequisites + real-world examples
- [ ] Grid: `sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3`

```tsx
// Conceptual card structure
<Card className="relative overflow-hidden">
  <div className="absolute top-0 right-0 px-2 py-1 text-[10px] bg-brand-teal/10 text-brand-teal rounded-bl-lg">
    {categoria}
  </div>
  <CardContent className="pt-6 space-y-3">
    <h4 className="font-heading font-semibold text-sm">{titulo}</h4>
    <p className="text-xs text-muted-foreground">{descricao}</p>
    <div className="flex gap-2">
      <Badge variant="outline">{roiEstimativa}</Badge>
      <ComplexityDots level={complexidade} />
      <span className="text-[10px] text-muted-foreground">{tempoValor}</span>
    </div>
    <div className="flex flex-wrap gap-1">
      {kpisAfetados.map(kpi => <Badge key={kpi} variant="secondary" className="text-[10px]">{kpi}</Badge>)}
    </div>
  </CardContent>
</Card>
```

#### 2c. Maturity Assessment Component
- [ ] Create `maturity-assessment.tsx` — 5-level horizontal scale
- [ ] Visual: 5 connected nodes on a horizontal line, current level highlighted
- [ ] Each level: name, description, criteria checklist
- [ ] Active level expands to show criteria with checkmarks
- [ ] Below: "Quer avaliar sua operação? Solicite um diagnóstico." micro-CTA

```
  ●────────●────────●────────●────────○
  Reativo  Descritivo  Preditivo  Prescritivo  Autônomo
              ▲ Nível atual
```

**Maturity Scale (5 levels, consistent across all modules):**

| Level | Nome | Description |
|-------|------|-------------|
| 1 | Reativo | Data in silos, manual KPIs, reactive decisions |
| 2 | Descritivo | Centralized data, real-time dashboards, automated KPIs |
| 3 | Preditivo | ML models for prediction, condition-based monitoring |
| 4 | Prescritivo | Closed-loop AI optimization, autonomous systems |
| 5 | Autônomo | Fully autonomous operation, continuous self-optimization |

#### 2d. Implementation Roadmap Component
- [ ] Create `implementation-roadmap.tsx` — phased timeline
- [ ] 3 phases: Diagnóstico (4-6 weeks), Piloto (8-12 weeks), Implementação (6-18 months)
- [ ] Each phase: card with deliverables list, duration badge, dependency links
- [ ] Visual: connected timeline (vertical on mobile, horizontal on desktop)
- [ ] Final CTA: "Solicitar Diagnóstico" button → modal/form

**New files:**
```
web/src/app/(dashboard)/mineradora-modelo/
  components/
    activity-map.tsx            # Horizontal process flow
    ai-use-cases.tsx            # AI use case card grid
    maturity-assessment.tsx     # 5-level maturity scale
    implementation-roadmap.tsx  # Phased timeline + CTA
    cta-modal.tsx               # Lead generation form modal
```

**Success criteria:**
- All 4 components render with pilot module data
- Activity map shows bottlenecks visually distinct from normal steps
- AI use cases can be filtered by category
- Maturity scale correctly highlights current level
- Roadmap CTA opens modal form

---

### Phase 3: Enhanced KPI Section

Upgrade the existing KPI section with AI projection overlays.

**Tasks:**
- [ ] Add "Projeção com IA" dashed line to trend charts showing estimated post-AI performance
- [ ] Add "Potencial de melhoria" badge to KPI cards (e.g., "+12% com IA")
- [ ] Enhance KPI cards with left accent bar + sparkline (borrow from `kpi-strip.tsx` pattern)
- [ ] Add in-tab section navigation (sticky bar): `KPIs | Atividades | IA | Maturidade | Roadmap`
- [ ] Implement scroll-to-section behavior on nav click

**Modified files:**
```
web/src/app/(dashboard)/mineradora-modelo/
  page.tsx                      # Main page restructured with sections
  components/
    kpi-card-enhanced.tsx       # Upgraded KPI card with AI projection badge
    kpi-chart-enhanced.tsx      # Trend chart with AI projection overlay
    module-section-nav.tsx      # Sticky section navigation
```

**Success criteria:**
- KPI charts show both "Realizado" solid line and "Projeção com IA" dashed line
- KPI cards show improvement potential badge
- Section nav is sticky and scrolls to correct section
- Smooth scroll behavior between sections

---

### Phase 4: Content for All 7 Modules

Scale the content system to all remaining modules.

**Tasks:**
- [ ] Create `mineradora-modelo/lib/data/planejamento.ts`
- [ ] Create `mineradora-modelo/lib/data/processamento.ts`
- [ ] Create `mineradora-modelo/lib/data/rejeitos.ts`
- [ ] Create `mineradora-modelo/lib/data/manutencao.ts`
- [ ] Create `mineradora-modelo/lib/data/logistica.ts`
- [ ] Create `mineradora-modelo/lib/data/ssma.ts`
- [ ] Update `modules-index.ts` to register all modules
- [ ] Verify radar chart updates with real module maturity levels

**Content per module (based on research):**

| Module | Activities | AI Use Cases | Maturity Level | Key Bottlenecks |
|--------|-----------|-------------|----------------|-----------------|
| Planejamento de Mina | 5 steps (modelo geologico → sequenciamento → reconciliação) | 4 cases (ML grade prediction, RL pit optimization, CV fragmentation, digital twin) | Nível 2 | Reconciliação modelo vs. realizado, variabilidade de teor |
| Operação de Mina | 6 steps (perfuração → desmonte → carregamento → transporte → descarga → serviços) | 5 cases (AHS, dispatch optimization, fatigue detection, road monitoring, drill optimization) | Nível 2 | Tempo de fila, consumo de diesel, disponibilidade de frota |
| Processamento Mineral | 5 steps (britagem → moagem → flotação/concentração → espessamento → filtragem) | 4 cases (closed-loop optimization, froth analysis, virtual analyzers, energy optimization) | Nível 2 | Recuperação metalúrgica, consumo energético, variabilidade de alimentação |
| Rejeitos e Meio Ambiente | 4 steps (disposição → monitoramento → recirculação água → recuperação ambiental) | 4 cases (dam stability prediction, InSAR deformation, water optimization, digital twin) | Nível 2 | Fator de segurança, detecção precoce de anomalias, conformidade |
| Manutenção | 5 steps (planejamento → preventiva → preditiva → corretiva → análise de falhas) | 5 cases (predictive maintenance, RUL estimation, NLP work orders, spare parts optimization, tire management) | Nível 1 | Manutenção reativa (>50%), MTBF baixo, custo por tonelada |
| Logística e Supply Chain | 5 steps (planejamento demanda → estoque → transporte mina-porto → embarque → blending) | 4 cases (mine-rail-port scheduling, demurrage prediction, demand forecasting, stockpile blending) | Nível 2 | Demurrage, lead time, aderência ao plano de embarque |
| SSMA-ESG | 5 steps (identificação riscos → monitoramento → resposta → reporte → melhoria contínua) | 4 cases (fatigue detection, PPE compliance CV, automated ESG reporting, predictive accident analysis) | Nível 1 | Subnotificação de quase-acidentes, reporte ESG manual, fadiga |

**New files:**
```
web/src/app/(dashboard)/mineradora-modelo/lib/data/
  planejamento.ts
  processamento.ts
  rejeitos.ts
  manutencao.ts
  logistica.ts
  ssma.ts
```

**Success criteria:**
- All 7 modules load with complete content
- Radar chart shows differentiated maturity levels
- No empty sections in any module
- Content is technically credible (would pass a mining engineer's review)

---

### Phase 5: Polish, CTA & Lead Generation

**Tasks:**
- [ ] Implement CTA modal (`cta-modal.tsx`):
  - Fields: nome, empresa, email, cargo, módulo de interesse (pre-filled from current tab)
  - Submit → sends email notification (or stores in simple API endpoint)
  - Success state: "Entraremos em contato em até 24h"
- [ ] Add floating CTA button on scroll (appears after user scrolls past first section)
- [ ] Clean up simulated data disclaimers: ONE persistent banner + footer note only
- [ ] Implement lazy loading: `dynamic(() => import(...))` for each module component
- [ ] Add ScrollArea around TabsList for mobile
- [ ] Test all 7 modules on mobile viewport
- [ ] Add micro-interactions: smooth scroll between sections, hover effects on cards

**Modified/New files:**
```
web/src/app/(dashboard)/mineradora-modelo/
  components/
    cta-modal.tsx               # Lead gen form
    cta-floating.tsx            # Floating CTA button
  modules/                      # Lazy-loaded module panels
    planejamento.tsx
    operacao.tsx
    processamento.tsx
    rejeitos.tsx
    manutencao.tsx
    logistica.tsx
    ssma.tsx
```

**Success criteria:**
- CTA modal opens from multiple touch points (roadmap section, floating button, overview)
- Mobile experience is smooth with 7 tabs
- Page loads fast (lazy loading keeps initial bundle small)
- Disclaimers are present but not visually overwhelming

---

## Module Content Detail: Operação de Mina (Pilot)

This is the first module to implement end-to-end. Full content specification:

### KPIs (existing, enhanced)

| KPI | Target | Unit | AI Projection |
|-----|--------|------|---------------|
| Produtividade da Frota | 280 | t/h | +15% com dispatch IA |
| Ciclo de Transporte | 25 | min | -12% com otimização de rotas |
| Consumo de Diesel | 1.8 | L/t | -10% com driving assist IA |
| Disponibilidade Física | 88 | % | +5pp com manutenção preditiva |
| Utilização Física | 78 | % | +8pp com AHS |

### Activity Map

```
[Perfuração] → [Desmonte] → [Carregamento] → [Transporte] → [Descarga] → [Serviços Auxiliares]
   ok           ok         gargalo          gargalo       ok           oportunidade
```

- **Carregamento (gargalo):** Tempo de fila de caminhões na escavadeira. Causa: dispatch ineficiente, desequilíbrio frota/equipamento. KPIs afetados: Produtividade, Ciclo.
- **Transporte (gargalo):** Maior custo operacional (~50% do custo de mina). Consumo de diesel, condição de estradas, velocidade. KPIs afetados: Diesel, Ciclo, Produtividade.
- **Serviços Auxiliares (oportunidade):** Manutenção de estradas, drenagem. Subutilizado para monitoramento com IA. KPIs afetados: Ciclo, Disponibilidade.

### AI Use Cases

1. **Despacho Inteligente com IA** — Otimização em tempo real da alocação caminhão-escavadeira usando ML + heurísticas. ROI: 5-15% produtividade. Complexidade: média. Tempo: 3-6 meses. Ex: Wenco, Hexagon Jigsaw, Modular DISPATCH.

2. **Caminhões Autônomos (AHS)** — Autonomous Haulage System com percepção LIDAR + GPS RTK. ROI: 15-20% redução de custo operacional. Complexidade: alta. Tempo: 18-36 meses. Ex: Rio Tinto (130+ caminhões), Caterpillar MineStar.

3. **Detecção de Fadiga** — Wearables (EEG smart caps) + câmeras in-cab para monitorar estado de alerta do operador. ROI: 70% redução acidentes por fadiga. Complexidade: baixa. Tempo: 1-3 meses. Ex: BHP smart caps, Fatigue Science Readi.

4. **Monitoramento de Estradas com CV** — Computer vision em drones/câmeras para avaliar condição de pista (buracos, ondulações, poeira). ROI: -8% consumo diesel. Complexidade: média. Tempo: 3-6 meses.

5. **Otimização de Perfuração** — ML para ajustar parâmetros de perfuração baseado em dureza da rocha e geologia do bloco. ROI: 5-10% redução custo de explosivos. Complexidade: média. Tempo: 6-12 meses.

### Maturity Assessment

**Nível atual da Mineradora Modelo: 2 — Descritivo**

| Nível | Status | Critérios |
|-------|--------|-----------|
| 1 - Reativo | ✅ Completo | Dados básicos de produção coletados, KPIs calculados manualmente, decisões reativas |
| 2 - Descritivo | ✅ Atual | FMS implantado, dashboards de produção em tempo real, KPIs automatizados, GPS em toda frota |
| 3 - Preditivo | ⬜ Próximo | Modelos ML para previsão de falhas, otimização de despacho com IA, análise preditiva de ciclo |
| 4 - Prescritivo | ⬜ Futuro | Despacho autônomo, closed-loop de otimização de diesel, digital twin da operação |
| 5 - Autônomo | ⬜ Visão | AHS full, operação remota, auto-otimização contínua sem intervenção humana |

### Implementation Roadmap

**Fase 1 — Diagnóstico (4-6 semanas)**
- Levantamento de sistemas existentes (FMS, SCADA, GPS)
- Mapeamento de dados disponíveis e qualidade
- Assessment de maturidade digital atual
- Identificação de quick wins (ROI em <3 meses)
- Entrega: Relatório diagnóstico + plano de ação priorizado

**Fase 2 — Piloto (8-12 semanas)**
- Implementação de 1-2 casos de uso priorizados (e.g., despacho IA + detecção fadiga)
- Integração com dados existentes do FMS
- Treinamento de equipe operacional
- Medição de baseline vs. resultados do piloto
- Entrega: Piloto validado + business case para escala

**Fase 3 — Implementação em Escala (6-18 meses)**
- Rollout dos casos de uso validados para toda operação
- Integração com sistemas corporativos (ERP, BI)
- Centro de Excelência de IA (governança, MLOps)
- Programa de change management
- Entrega: Operação digital madura (nível 3-4)

---

## Alternative Approaches Considered

### A. Interactive Self-Assessment (Deferred to V2)

Instead of showing a static model company, let prospects self-assess their maturity per module. Creates a powerful lead-gen moment ("enter email to save your assessment"). Deferred because:
- Requires user account/session management
- Needs careful questionnaire design per module
- Current priority is the sales demo, not self-service

### B. Presentation Mode (Deferred to V2)

A fullscreen, one-section-at-a-time mode for consultant-led demos. Deferred because:
- The standard page with section nav serves most needs
- Can be added later without architectural changes

### C. PDF Export (Deferred to V2)

Generate a per-module PDF report. Deferred because:
- Consultants can screenshot for now
- PDF generation adds complexity (headless browser or PDF library)
- Not critical for initial launch

---

## Acceptance Criteria

### Functional Requirements
- [ ] Page loads at `/mineradora-modelo` with cross-module overview (radar chart + ROI summary)
- [ ] 7 module tabs with URL state sync (`?modulo=operacao`)
- [ ] Each module has 5 sections: KPIs, Atividades, IA, Maturidade, Roadmap
- [ ] Sticky in-tab section navigation with smooth scroll
- [ ] Activity maps show 4-6 steps with status badges (ok/gargalo/oportunidade)
- [ ] AI use cases display as filterable card grid with ROI, complexity, time to value
- [ ] Maturity scale shows 5 levels with current level highlighted
- [ ] Implementation roadmap shows 3 phases with deliverables
- [ ] KPI charts include AI projection overlay (dashed line)
- [ ] CTA modal accessible from roadmap section, floating button, and overview
- [ ] Deep linking works: sharing a URL with `?modulo=manutencao` loads correct tab

### Non-Functional Requirements
- [ ] Initial page load < 2s (lazy-load module content)
- [ ] Mobile-responsive: tabs scroll horizontally, sections stack vertically
- [ ] All content in Portuguese (technical terms in English where standard in industry)
- [ ] Simulated data disclaimer: 1 persistent banner + 1 footer note (not per-chart)
- [ ] Dark mode compatible (uses CSS variables throughout)

### Quality Gates
- [ ] All TypeScript types compile with strict mode
- [ ] Content reviewed by domain expert for technical accuracy
- [ ] Tested on desktop (1440px), tablet (768px), and mobile (375px)
- [ ] Lighthouse performance score > 90

---

## Dependencies & Prerequisites

| Dependency | Status | Notes |
|-----------|--------|-------|
| Next.js web app deployed | ✅ Ready | Vercel at summo-quartile.vercel.app |
| shadcn/ui components | ✅ Ready | Tabs, Card, Badge, Dialog all available |
| Recharts | ✅ Ready | v3.8.1 installed, RadarChart available |
| Domain content (7 modules) | ⬜ Needed | Mining industry KPIs, activities, AI use cases |
| CTA backend (email/form) | ⬜ Needed | Simple endpoint to receive lead form submissions |

---

## Risk Analysis & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Content authoring bottleneck (28 content blocks) | High | Start with 1 pilot module; use AI-assisted content generation with human review |
| Technical credibility with mining engineers | High | Source all KPIs and benchmarks from industry standards (Opsima, McKinsey, BCG) |
| Page becomes too long/overwhelming | Medium | Sticky section nav + lazy rendering of inactive tabs |
| CTA backend complexity | Low | Start with simple mailto: or Formspree, upgrade to API later |
| Mobile UX with 7 tabs + 5 sections | Medium | ScrollArea for tabs, collapsible sections on mobile |

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Time on page | > 3 minutes | Vercel Analytics |
| Module tabs visited per session | > 3 of 7 | Custom events |
| CTA conversion rate | > 5% of visitors | Form submissions / page views |
| Consultant feedback | "I can use this in a real pitch" | Qualitative |
| Technical credibility | No factual errors flagged by mining engineers | Expert review |

---

## File Structure (Complete)

```
web/src/app/(dashboard)/mineradora-modelo/
├── page.tsx                          # Main page: overview + tabs + URL state
├── lib/
│   ├── types.ts                      # TypeScript interfaces
│   └── data/
│       ├── modules-index.ts          # Module registry, overview aggregation
│       ├── maturity-scale.ts         # Shared 5-level maturity definitions
│       ├── planejamento.ts           # Mine Planning content
│       ├── operacao.ts               # Mine Operations content (PILOT)
│       ├── processamento.ts          # Mineral Processing content
│       ├── rejeitos.ts               # Tailings & Environment content
│       ├── manutencao.ts             # Maintenance content
│       ├── logistica.ts              # Logistics & Supply Chain content
│       └── ssma.ts                   # Safety-ESG content
├── components/
│   ├── overview-section.tsx          # Cross-module radar + ROI summary
│   ├── module-section-nav.tsx        # Sticky in-tab section navigation
│   ├── activity-map.tsx              # Horizontal process flow
│   ├── ai-use-cases.tsx              # AI use case card grid
│   ├── maturity-assessment.tsx       # 5-level scale visualization
│   ├── implementation-roadmap.tsx    # Phased timeline
│   ├── kpi-card-enhanced.tsx         # KPI card with AI projection badge
│   ├── kpi-chart-enhanced.tsx        # Trend chart with AI overlay
│   ├── cta-modal.tsx                 # Lead generation form
│   └── cta-floating.tsx              # Floating CTA button
└── modules/                          # Lazy-loaded per-module panels
    ├── planejamento.tsx
    ├── operacao.tsx
    ├── processamento.tsx
    ├── rejeitos.tsx
    ├── manutencao.tsx
    ├── logistica.tsx
    └── ssma.tsx
```

---

## References & Research

### Internal References
- Current Next.js page: [mineradora-modelo/page.tsx](web/src/app/(dashboard)/mineradora-modelo/page.tsx)
- Simulation engine: [mining_simulator.py](app/components/mining_simulator.py)
- Tab pattern reference: [inteligencia-comercial/page.tsx](web/src/app/(dashboard)/inteligencia-comercial/page.tsx)
- KPI card pattern: [kpi-strip.tsx](web/src/app/(dashboard)/inteligencia-comercial/kpi-strip.tsx)
- Migration plan: [feat-full-streamlit-to-nextjs-migration.md](plans/feat-full-streamlit-to-nextjs-migration.md)
- Parity audit: [feat-streamlit-parity-next.md](plans/feat-streamlit-parity-next.md)

### External References — AI in Mining
- [BCG: The AI-Powered Mining and Metals Company](https://www.bcg.com/publications/2026/the-ai-powered-mining-and-metals-company)
- [BCG: Scheduling Rio Tinto's Iron Ore Supply Chain with AI](https://www.bcg.com/x/mark-your-moment/how-an-iron-ore-producer-modernized-mining-operations-with-ai)
- [McKinsey: OptimusAI for Metals & Mining](https://www.mckinsey.com/industries/metals-and-mining/how-we-help-clients/optimusai)
- [Imubit: AI Methods to Boost Mineral Recovery](https://imubit.com/article/ai-critical-mineral-recovery-plant/)
- [Hatch: AI Breakthrough in Mineral Processing](https://www.hatch.com/en/About-Us/Publications/Performance-Innovations/2025/0202-AI-breakthrough-in-mineral-processing-unlocking-millions-in-value)
- [Omdena: 22 AI Use Cases in Mining](https://www.omdena.com/blog/ai-use-cases-in-mining)
- [Mining Technology: AI in Tailings Management](https://www.mining-technology.com/features/ais-rising-role-in-tailings-management/)
- [Nanoprecise: Predictive Maintenance in Mining](https://nanoprecise.io/predictive-maintenance-in-mining-sector/)
- [Fatigue Science: AI for Mining Safety](https://fatiguescience.com/blog/ai-mining-safety)
- [Opsima: Mining Industry KPIs — 30 Metrics](https://opsima.com/blog/kpis/mining-industry-kpis/)

### Market Data
- AI in mining market: US$29.94B (2024) → US$685.61B (2033), CAGR 41.9%
- Only 5% of mining companies generate substantial value from AI at scale (BCG 2025)
- 70% of implementation challenges are people/process, not technical
- 52% of mining workers concerned about AI's impact on jobs

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
