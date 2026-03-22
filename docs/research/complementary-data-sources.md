# Complementary Data Sources — Prioritized Roadmap

Compiled: 2026-03-21

## Phase 1 — Quick Wins (1-2 weeks each, massive value)

All clean, well-structured, connect directly to existing data via spatial join or CNPJ.

| # | Source | Bridge | Value | Effort | URL |
|---|--------|--------|-------|--------|-----|
| 1 | **ICMBio UCs** (Conservation Units) | Spatial | 9/10 | 2/10 | gov.br/icmbio + WFS service |
| 2 | **FUNAI TIs** (Indigenous Territories) | Spatial | 9/10 | 2/10 | gov.br/funai + GeoServer |
| 3 | **IBAMA Infractions/Fines** | CNPJ | 9/10 | 3/10 | dadosabertos.ibama.gov.br (CSV/JSON) |
| 4 | **ANM CFEM** (royalty payments) | CNPJ/processo | 8/10 | 2/10 | dados.gov.br (CSV) |
| 5 | **ANM RAL** (annual production reports) | CNPJ/processo | 8/10 | 2/10 | dados.gov.br (CSV) |
| 6 | **Receita Federal CNPJ** | CNPJ | 8/10 | 3/10 | opencnpj.org API or bulk CSV |
| 7 | **CECAV Caves** | Spatial | 8/10 | 3/10 | gov.br/icmbio (Shapefile) |
| 8 | **IBGE Biomes** | Spatial | 6/10 | 2/10 | ibge.gov.br (Shapefile) |

**Combined outcome**: Pre-screening risk score for any mining area:
- Does it overlap with UC, TI, or cave? → licensing blocker/restriction
- Does the company have prior infractions? → elevated scrutiny
- What's their production scale (CFEM/RAL)? → operational maturity
- What kind of company (size, age, CNAE)? → profile

## Phase 2 — Moderate Effort (2-4 weeks each)

| # | Source | Bridge | Value | Effort | Notes |
|---|--------|--------|-------|--------|-------|
| 9 | **ANA Water Rights** | CNPJ/spatial | 7/10 | 3/10 | CSV with coordinates, federal waters only |
| 10 | **MapBiomas Mining Footprint** | Spatial | 7/10 | 5/10 | Raster via GEE, vector alerts easier |
| 11 | **Commodity Prices** | Substance | 5/10 | 1/10 | Free APIs (FRED, Yahoo Finance) |

## Phase 3 — High Effort, Highest Reward

| # | Source | Bridge | Value | Effort | Notes |
|---|--------|--------|-------|--------|-------|
| 12 | **COPAM Meeting Minutes** | Processo | **10/10** | 9/10 | Voting records, technical opinions. Lei.A found 90% gov members vote pro-mining. NLP/LLM extraction needed. |
| 13 | **CAR/SICAR** | Spatial | 7/10 | 7/10 | APPs, legal reserves. Must scrape per municipality (5,570). |

## Phase 4 — State Expansion

| # | Source | Bridge | Value | Effort |
|---|--------|--------|-------|--------|
| 14 | SP CETESB | CNPJ | 4/10 | 5/10 |
| 15 | PA SEMAS | CNPJ/spatial | 7/10 | 8/10 |
| 16 | BA INEMA | CNPJ | 5/10 | 7/10 |

## The Compound Value

Phase 1 sources + our existing 42,758 MG decisions → **predictive licensing risk score**:

```
risk_score = f(
    spatial_restrictions,    # UCs, TIs, caves, biome
    company_track_record,    # infractions, CFEM regularity, company age
    operational_scale,       # RAL production, CFEM revenue
    activity_class,          # DN 217 classification
    regional_patterns,       # historical approval rates
    decision_reasoning,      # PDF text from Pareceres Técnicos
)
```

Validated against 8,072 mining decisions with known outcomes (deferido/indeferido/arquivamento).

Sources: ICMBio, FUNAI, IBAMA, ANM, Receita Federal, CECAV, IBGE, ANA, MapBiomas, COPAM, CAR/SICAR, Lei.A
