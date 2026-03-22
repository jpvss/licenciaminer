# Data Map — Minas Gerais Focus

Compiled: 2026-03-21

## Overview

All data sources for MG, how they connect, and how they'll be used.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENHANCED MINING DECISION DATASET                  │
│                                                                     │
│  For each mining process in MG, we want:                           │
│  ├── WHO: Company profile (CNPJ, size, track record)               │
│  ├── WHAT: Activity, substance, production scale                    │
│  ├── WHERE: Location, spatial restrictions (UCs, TIs, caves)        │
│  ├── WHEN: Timeline, commodity prices at decision time              │
│  ├── HOW: Licensing modality, class, regional office                │
│  ├── OUTCOME: Deferido / Indeferido / Arquivamento                 │
│  ├── WHY: Parecer técnico text, conditions, reasoning               │
│  └── GOVERNANCE: COPAM voting record, council composition           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## DATA SOURCES

### LAYER 1: Core Decision Data (DONE)

#### 1A. MG SEMAD Licensing Decisions
- **Status**: ✅ Collected (42,758 records, 8,072 mining)
- **Source**: Web scraper from sistemas.meioambiente.mg.gov.br
- **Fields**: regional, município, empreendimento, cnpj, processo, modalidade, classe, atividade, ano, mês, data_publicação, **decisão**, detail_id
- **Bridge keys**: CNPJ, detail_id, processo_adm
- **Use**: Ground truth for approval/rejection outcomes

#### 1B. MG SEMAD Decision Documents (PDFs)
- **Status**: 🔄 Extracting (8,040 mining records, ~14,735 PDFs)
- **Source**: Detail pages via view-externo?id=N
- **Content**: Parecer técnico (22K+ chars each), Folha de decisão, Despacho, Certificado
- **Bridge keys**: detail_id
- **Use**: Decision reasoning, conditions imposed, technical analysis, specific environmental concerns

#### 1C. IBAMA Federal Licenses
- **Status**: ✅ Collected (1,115 mining records)
- **Source**: dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json
- **Fields**: tipo_licença, número, data_emissão, data_vencimento, empreendimento, nome_pessoa, processo, tipologia
- **Bridge keys**: Company name (fuzzy), CNPJ (not directly available)
- **Use**: Federal licensing complement — projects under IBAMA jurisdiction
- **Limitation**: Only emitted licenses (no rejections)

#### 1D. ANM SIGMINE Mining Processes
- **Status**: ✅ Collected (50,723 MG records)
- **Source**: ArcGIS REST FeatureServer
- **Fields**: PROCESSO, NUMERO, ANO, AREA_HA, FASE, ULT_EVENTO, NOME, SUBS, USO, UF
- **Bridge keys**: CNPJ (via NOME matching), PROCESSO number, spatial overlap
- **Use**: Mining rights context — area size, substance, phase, title holder

---

### LAYER 2: Spatial Restrictions (TO COLLECT)

#### 2A. ICMBio Conservation Units (UCs)
- **Source**: gov.br/icmbio + WFS geoservicos.inde.gov.br
- **Format**: Shapefile, WFS
- **Bridge**: Spatial overlap with ANM polygons
- **Use**: UC overlap = licensing blocker (integral protection) or restriction (sustainable use)
- **Effort**: LOW (clean shapefiles, standard spatial join)
- **Value**: 9/10

#### 2B. FUNAI Indigenous Territories (TIs)
- **Source**: gov.br/funai + GeoServer geoserver.funai.gov.br
- **Format**: Shapefile, KML, XLSX (updated monthly)
- **Bridge**: Spatial overlap with ANM polygons
- **Use**: TI overlap = near-absolute mining blocker (Art. 231 CF/1988)
- **Effort**: LOW
- **Value**: 9/10

#### 2C. CECAV Caves (CANIE)
- **Source**: gov.br/icmbio/cavernas
- **Format**: Shapefile, KMZ (18,000+ caves)
- **Bridge**: Spatial proximity (250m buffer for maximum relevance caves)
- **Use**: Cave proximity = restriction, especially in Quadrilátero Ferrífero (iron ore + canga)
- **Effort**: LOW-MEDIUM (need to compute buffer zones)
- **Value**: 8/10

#### 2D. IBGE Biomes
- **Source**: ibge.gov.br (1:250,000 shapefile)
- **Format**: Shapefile, GeoJSON via API
- **Bridge**: Spatial overlay
- **Use**: Biome classification determines applicable regulations (Mata Atlântica has stricter federal law 11.428/2006)
- **Effort**: LOW
- **Value**: 6/10

---

### LAYER 3: Company & Production Profile (TO COLLECT)

#### 3A. IBAMA Environmental Infractions
- **Source**: dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao
- **Format**: CSV, JSON (68 datasets)
- **Bridge**: CNPJ/CPF
- **Use**: Prior infractions → elevated scrutiny → lower approval odds. Infraction types (flora, fauna, pollution) indicate compliance track record.
- **Effort**: LOW (well-structured CSV with CNPJ)
- **Value**: 9/10

#### 3B. ANM CFEM Royalty Payments
- **Source**: dados.gov.br/dataset/sistema-arrecadacao
- **Format**: CSV
- **Bridge**: CNPJ, processo ANM
- **Use**: Production volumes, revenue per mine. Zero CFEM on active title = irregular operation.
- **Effort**: LOW
- **Value**: 8/10

#### 3C. ANM RAL (Annual Production Reports)
- **Source**: dados.gov.br/dados/conjuntos-dados/relatorio-anual-de-lavra-ral
- **Format**: CSV (3 files: raw production, benefited, mineral water). 2010 onwards.
- **Bridge**: Processo ANM, CNPJ, município
- **Use**: Declared production, reserves, workforce. Large producers with track records face different dynamics.
- **Effort**: LOW
- **Value**: 8/10

#### 3D. Receita Federal CNPJ Data
- **Source**: opencnpj.org API (free) or bulk CSV from Receita Federal
- **Format**: JSON API or 4GB bulk CSV
- **Bridge**: CNPJ (universal key)
- **Use**: Company size (porte), CNAE activity code, founding date, address, partner structure. Company age/size correlate with licensing success.
- **Effort**: LOW (API) to MEDIUM (bulk)
- **Value**: 8/10

---

### LAYER 4: Governance & Voting (TO COLLECT)

#### 4A. COPAM Meeting Data
- **Source**: sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam/index-externo
- **Format**: HTML table (1,761 meetings) + PDF documents per meeting
- **Structure**:
  ```
  Meeting List (1,761 total)
  ├── Metadata: date, title, sede/regional, unidade colegiada
  ├── Filter by: CMI (Atividades Minerárias) for mining-specific
  └── Detail Page (view-externo?id=N)
      ├── Convocação (convocation notice)
      ├── Pauta (agenda)
      ├── Documentos da pauta (per-item PDFs with company names)
      │   ├── Item 06.1 — Empresa X (município Y).pdf
      │   ├── Item 06.2 — Empresa Z (município W).pdf
      │   └── ...
      ├── Relatos de vista (review opinions)
      ├── Pareceres alterados (altered opinions)
      ├── Decisão (decision document — THE GOLD)
      ├── Ata aprovada (approved minutes)
      ├── Apresentações (presentations)
      └── Lista de presença (attendance)
  ```
- **Bridge**: Process number, company name, município → link to SEMAD decisions
- **Use**:
  - Voting patterns by council member
  - Technical opinions vs final decisions (are technical recommendations overridden?)
  - Which companies/substances face more debate
  - Lei.A found 90% of gov-appointed members vote pro-mining
- **Effort**: HIGH (scrape meetings list + detail pages + extract PDFs + NLP)
- **Value**: 10/10

**COPAM Scraping Plan**:
1. Scrape meeting list, filter CMI meetings only (~150-200 of 1,761)
2. For each CMI meeting, fetch detail page and extract all PDF links
3. Download Decision PDFs (Decisão) — contain actual voting outcomes
4. Download Pauta PDFs — contain process details being voted on
5. Extract text from all PDFs
6. Parse structured data: company, processo, município, decision per item
7. Link back to SEMAD decisions via process number or company+município

---

### LAYER 5: Context (TO COLLECT)

#### 5A. ANA Water Rights
- **Source**: dados.ana.gov.br (CSV with coordinates)
- **Bridge**: CNPJ, spatial
- **Use**: Water permit status affects mining licensing. Water conflicts in watershed.
- **Effort**: LOW
- **Value**: 7/10

#### 5B. Commodity Prices
- **Source**: FRED API, Yahoo Finance (free)
- **Bridge**: Substance code → commodity
- **Use**: Time-series analysis — do application volumes track price booms?
- **Effort**: TRIVIAL
- **Value**: 5/10

---

## HOW IT ALL CONNECTS

```
                    CNPJ (primary bridge)
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐      ┌─────────────┐      ┌──────────┐
│ SEMAD   │      │ Receita Fed │      │ IBAMA    │
│ Decisões│      │ CNPJ Data   │      │ Infrações│
│ 42,758  │      │ Size, CNAE  │      │ Fines    │
└────┬────┘      └─────────────┘      └──────────┘
     │
     │ detail_id           PROCESSO ANM
     ▼                         │
┌─────────┐            ┌──────┴──────┐
│ PDFs    │            │ ANM SIGMINE │──── CFEM, RAL
│ Parecer │            │ 50,723 MG   │    (production)
│ Técnico │            │ + polygons  │
└─────────┘            └──────┬──────┘
                              │
                       Spatial Overlap
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         ┌────────┐     ┌─────────┐     ┌─────────┐
         │ UCs    │     │ TIs     │     │ Caves   │
         │ICMBio  │     │ FUNAI   │     │ CECAV   │
         └────────┘     └─────────┘     └─────────┘

     COPAM Meetings ─── processo/empresa ──→ SEMAD Decisões
```

---

## IMPLEMENTATION ORDER

### Sprint 1 (Current): Core MG Pipeline ✅
- [x] SEMAD scraper (42,758 records)
- [x] IBAMA collector (1,115 records)
- [x] ANM collector (50,723 MG records)
- [x] PDF links enrichment (8,045 mining records)
- [🔄] PDF text extraction (running, 8,040 records)

### Sprint 2: Quick-Win Enrichment
1. IBAMA infractions (CSV, CNPJ join)
2. ANM CFEM royalties (CSV, CNPJ/processo join)
3. ANM RAL production (CSV, CNPJ/processo join)
4. Receita Federal CNPJ enrichment (API, CNPJ lookup)

### Sprint 3: Spatial Overlays
5. ICMBio UCs (shapefile, spatial join with ANM)
6. FUNAI TIs (shapefile, spatial join)
7. CECAV caves (shapefile, buffer + spatial join)
8. IBGE biomes (shapefile, spatial overlay)
*Requires: geopandas, shapely — already planned for Phase 2*

### Sprint 4: COPAM Governance
9. Scrape CMI meeting list (~150-200 meetings)
10. Extract detail pages + PDF links
11. Download Decision + Pauta PDFs
12. NLP extraction of voting records and process outcomes
13. Link to SEMAD decisions

### Sprint 5: Predictive Model
- Train on 8,072 mining decisions with enriched features
- Features: spatial restrictions, company profile, activity class, regional, historical patterns
- Target: deferido / indeferido / arquivamento probability
- Validate with cross-validation and temporal splits
