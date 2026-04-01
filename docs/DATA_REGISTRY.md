# Data Registry — Sistema Integrado Summo Quartile

Last updated: 2026-03-31

## How to Read This Document

Each data source is documented with:
- **What**: description and record count
- **Where**: source URL and local file path
- **Bridge**: how it connects to other sources
- **Refresh**: command and frequency
- **Status**: ✅ done, 🔄 running, ⏸ blocked (external), ⏳ pending

---

## LAYER 1: Core Decision Data

### 1A. MG SEMAD Licensing Decisions
| Field | Value |
|-------|-------|
| **What** | 42,758 environmental licensing decisions in MG (8,072 mining) |
| **Where (source)** | https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca |
| **Where (local)** | `data/processed/mg_semad_licencas.parquet` (120 MB) |
| **Key fields** | regional, município, empreendimento, cnpj_cpf, modalidade, classe, atividade, decisão, detail_id |
| **Bridge keys** | `cnpj_cpf` → infrações, CFEM, CNPJ; `detail_id` → PDF docs |
| **Refresh** | `licenciaminer collect mg --scrape --all-activities` (incremental, ~1 sec if no new) |
| **Frequency** | Weekly |
| **Status** | ✅ Complete |

### 1B. MG SEMAD Decision Documents (PDF Links)
| Field | Value |
|-------|-------|
| **What** | PDF document URLs from detail pages (Parecer, Folha de decisão, Despacho) |
| **Where (source)** | Detail pages: view-externo?id={detail_id} |
| **Where (local)** | Column `documentos_pdf` in mg_semad_licencas.parquet |
| **Key fields** | documentos_pdf (format: "filename\|url;filename\|url") |
| **Bridge keys** | `detail_id` |
| **Refresh** | `licenciaminer collect mg-docs --mining-only` (incremental, skips enriched) |
| **Frequency** | After each mg scrape |
| **Status** | 🔄 Re-enriching (5,500/8,072 — ~30 min remaining) |

### 1C. MG SEMAD Decision Text (PDF Extraction)
| Field | Value |
|-------|-------|
| **What** | Full text extracted from 6,964 mining decision PDFs (253 MB text) |
| **Where (source)** | PDFs at sistemas.meioambiente.mg.gov.br/licenciamento/uploads/*.pdf |
| **Where (local)** | Column `texto_documentos` in mg_semad_licencas.parquet |
| **Key fields** | texto_documentos (concatenated text from all PDFs per record) |
| **Bridge keys** | `detail_id` |
| **Refresh** | `licenciaminer collect mg-textos --mining-only` (incremental, skips extracted) |
| **Frequency** | After each mg-docs enrichment |
| **Note** | 86.6% coverage — 13.4% are scanned PDFs without extractable text |
| **Status** | ✅ Complete |

### 1D. IBAMA Federal Mining Licenses
| Field | Value |
|-------|-------|
| **What** | 1,115 federal environmental licenses for mining (1994–2026) |
| **Where (source)** | https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json |
| **Where (local)** | `data/processed/ibama_licencas.parquet` (0.04 MB) |
| **Key fields** | tipo_licenca, numero_licenca, data_emissão, empreendimento, nome_empreendedor |
| **Bridge keys** | Company name (fuzzy match to SEMAD/ANM) |
| **Refresh** | `licenciaminer collect ibama` (full overwrite, ~5 sec) |
| **Frequency** | Weekly |
| **Limitation** | Only emitted licenses — no rejections in open data |
| **Status** | ✅ Complete |

### 1E. ANM SIGMINE Mining Processes
| Field | Value |
|-------|-------|
| **What** | 50,723 mining processes in MG (titles, phases, substances, areas) |
| **Where (source)** | https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0/query |
| **Where (local)** | `data/processed/anm_processos.parquet` (4 MB) |
| **Key fields** | PROCESSO, NOME, FASE, SUBS, UF, AREA_HA, ANO |
| **Bridge keys** | `NOME` (company name), `PROCESSO` → spatial overlaps, CFEM |
| **Refresh** | `licenciaminer collect anm --uf MG` (full overwrite, ~17 min) |
| **Frequency** | Weekly |
| **Note** | resultOffset ignored by server — uses UF→FASE→ANO iteration |
| **Status** | ✅ Complete |

---

## LAYER 2: Company Profile

### 2A. IBAMA Environmental Infractions
| Field | Value |
|-------|-------|
| **What** | 702,280 environmental infraction records (all Brazil, 113K in MG) |
| **Where (source)** | https://dadosabertos.ibama.gov.br/dados/SIFISC/auto_infracao/auto_infracao/auto_infracao_csv.zip |
| **Where (local)** | `data/processed/ibama_infracoes.parquet` (130 MB) |
| **Key fields** | CPF_CNPJ_INFRATOR, UF, tipo_infracao, data_auto |
| **Bridge keys** | `CPF_CNPJ_INFRATOR` → SEMAD cnpj_cpf (needs REGEXP_REPLACE to strip punctuation) |
| **Refresh** | `licenciaminer collect infracoes` (full overwrite, ~20 sec) |
| **Frequency** | Monthly |
| **Status** | ✅ Complete |

### 2B. ANM CFEM Royalty Payments
| Field | Value |
|-------|-------|
| **What** | 91,026 monthly royalty payment records for MG (2022–2026) |
| **Where (source)** | https://app.anm.gov.br/dadosabertos/ARRECADACAO/CFEM_Arrecadacao_2022_2026.csv |
| **Where (local)** | `data/processed/anm_cfem.parquet` (2.4 MB) |
| **Key fields** | CPF_CNPJ, Processo, Substância, ValorRecolhido, Ano, Mês |
| **Bridge keys** | `CPF_CNPJ` → SEMAD cnpj_cpf; `Processo` → ANM |
| **Refresh** | `licenciaminer collect cfem` (full overwrite, ~10 sec) |
| **Frequency** | Monthly |
| **Note** | ValorRecolhido stored as string with comma decimal — use REPLACE in queries |
| **Status** | ✅ Complete |

### 2C. ANM RAL Production Reports
| Field | Value |
|-------|-------|
| **What** | 1,013 MG mineral production records (raw + benefited, by substance/year) |
| **Where (source)** | https://app.anm.gov.br/dadosabertos/AMB/Producao_Bruta.csv + Producao_Beneficiada.csv |
| **Where (local)** | `data/processed/anm_ral.parquet` |
| **Key fields** | Ano base, UF, Substância Mineral, Quantidade, Valor Venda |
| **Bridge keys** | Substance name → ANM SUBS; aggregated by UF (no per-company CNPJ) |
| **Refresh** | `licenciaminer collect ral` (full overwrite, ~2 sec) |
| **Frequency** | Yearly |
| **Note** | Aggregated by UF/substance — no CNPJ. Useful for market context only. |
| **Status** | ✅ Complete |

### 2D. Receita Federal CNPJ Data
| Field | Value |
|-------|-------|
| **What** | Company profiles (razão social, CNAE, porte, data abertura, situação) |
| **Where (source)** | https://brasilapi.com.br/api/cnpj/v1/{CNPJ} |
| **Where (local)** | `data/processed/cnpj_empresas.parquet` |
| **Key fields** | cnpj, razao_social, cnae_fiscal, porte, data_abertura, situacao |
| **Bridge keys** | `cnpj` → SEMAD cnpj_cpf |
| **Refresh** | `licenciaminer collect cnpj` (incremental, skips fetched, ~0.5s/query) |
| **Frequency** | Quarterly |
| **Note** | ~30% of source CNPJs are invalid (handled gracefully). ~70% hit rate. |
| **Status** | 🔄 Running (6,300/21,840 — ~2.5 hrs remaining, resumable) |

---

## LAYER 3: Spatial Restrictions

### 3A. ICMBio Conservation Units (UCs)
| Field | Value |
|-------|-------|
| **What** | 344 federal conservation units (polygons) |
| **Where (source)** | https://www.gov.br/icmbio/pt-br/assuntos/dados_geoespaciais/ |
| **Where (local)** | `data/reference/icmbio_ucs.parquet` |
| **Bridge keys** | Spatial overlap with ANM polygons |
| **Refresh** | `licenciaminer collect spatial --layer ucs` (~10 sec) |
| **Status** | ✅ Complete |

### 3B. FUNAI Indigenous Territories (TIs)
| Field | Value |
|-------|-------|
| **What** | 16 indigenous territories in MG (polygons) |
| **Where (source)** | https://geoserver.funai.gov.br/geoserver/Funai/ows (WFS, filtered MG) |
| **Where (local)** | `data/reference/funai_tis.parquet` |
| **Bridge keys** | Spatial overlap with ANM polygons |
| **Refresh** | `licenciaminer collect spatial --layer tis` (~2 sec) |
| **Status** | ✅ Complete |

### 3C. IBGE Biomes
| Field | Value |
|-------|-------|
| **What** | 6 Brazilian biomes (polygons, 1:250,000) |
| **Where (source)** | http://geoftp.ibge.gov.br/informacoes_ambientais/estudos_ambientais/biomas/ |
| **Where (local)** | `data/reference/ibge_biomas.parquet` |
| **Bridge keys** | Spatial overlay with ANM polygons |
| **Refresh** | `licenciaminer collect spatial --layer biomas` (~7 sec) |
| **Status** | ✅ Complete |

### 3D. ANM Geometries (Mining Polygons)
| Field | Value |
|-------|-------|
| **What** | 50,725 MG mining process polygons |
| **Where (source)** | https://app.anm.gov.br/dadosabertos/SIGMINE/PROCESSOS_MINERARIOS/BRASIL.zip (122 MB) |
| **Where (local)** | `data/reference/anm_geometrias_mg.parquet` |
| **Bridge keys** | `PROCESSO` → ANM processos |
| **Refresh** | `licenciaminer collect spatial --layer anm-geo` (~15 sec) |
| **Status** | ✅ Complete |

### 3E. Spatial Overlaps (Computed)
| Field | Value |
|-------|-------|
| **What** | Pre-computed spatial joins: ANM processes × UCs/TIs/biomas |
| **Where (local)** | `data/processed/anm_spatial_overlaps.parquet` |
| **Key results** | 949 processes in UCs (1.9%), 113 in TIs (0.2%), biomas for all |
| **Refresh** | `licenciaminer collect spatial --layer overlaps` (~6 min) |
| **Status** | ✅ Complete |

### 3F. CECAV Cave Occurrence Areas
| Field | Value |
|-------|-------|
| **What** | Cave occurrence areas in Brazil (geological potential) |
| **Where (source)** | gov.br/icmbio — shapefile URL returned 404 |
| **Where (local)** | `data/reference/cecav_cavernas.parquet` (not yet collected) |
| **Refresh** | `licenciaminer collect spatial --layer caves` |
| **Note** | Shapefile URL moved. Collector built, needs updated URL or CANIE login. |
| **Status** | ⏸ Blocked — URL 404 |

---

## LAYER 4: Governance

### 4A. COPAM CMI Meeting Data
| Field | Value |
|-------|-------|
| **What** | 135 CMI (mining chamber) meetings with 2,234 PDF documents |
| **Where (source)** | https://sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam/index-externo |
| **Where (local)** | `data/processed/copam_cmi_reunioes.parquet` |
| **Key fields** | meeting_id, data, titulo, sede, documents_str (PDFs) |
| **Documents include** | Pauta, Decisão, Pareceres alterados, Relatos de vista, Atas |
| **Bridge keys** | Company name, process number → SEMAD decisions |
| **Refresh** | `licenciaminer collect copam` (incremental, ~1 min) |
| **Frequency** | Monthly (CMI meets monthly) |
| **Status** | ✅ Complete |

---

## LAYER 5: Context

### 5A. ANA Water Rights
| Field | Value |
|-------|-------|
| **What** | Federal water use permits (outorgas) |
| **Where (source)** | https://dados.ana.gov.br/dataset/outorgas |
| **Where (local)** | `data/processed/ana_outorgas.parquet` (not yet collected) |
| **Bridge keys** | `CNPJ` → SEMAD, spatial coordinates |
| **Refresh** | `licenciaminer collect outorgas` |
| **Note** | Collector built. ANA portal returning 504 consistently. Retry later. |
| **Status** | ⏸ Blocked — ANA portal 504 |

---

## CROSS-SOURCE JOINS

All joins happen at query time via DuckDB views. No data is duplicated.

```
SEMAD (cnpj_cpf)  ←→ IBAMA infrações (CPF_CNPJ_INFRATOR, REGEXP_REPLACE)
SEMAD (cnpj_cpf)  ←→ CFEM (CPF_CNPJ)
SEMAD (cnpj_cpf)  ←→ CNPJ empresas (cnpj)
SEMAD (detail_id) →  PDF docs → PDF text
ANM (PROCESSO)    ←→ Spatial overlaps (PROCESSO)
ANM (PROCESSO)    ←→ CFEM (Processo)
COPAM (company/process) → SEMAD decisions (fuzzy match)
```

**Validated CNPJ join rates:**
- SEMAD mining → IBAMA infrações: **309/4,206** unique CNPJs (7.3%)
- SEMAD mining → CFEM: **1,584/4,206** (37.6%)

**Key cross-source insights:**
- Companies with 6+ infractions: **73.7% approval** (vs 62.3% with 0)
- CFEM payers: **65.6% approval** (vs 60.5% non-payers)
- Small CFEM (<R$10K): **70.3%** best rate; large (>R$1M): **56.7%** worst

---

## REFRESH COMMANDS

### Daily/Weekly (fast, ~1 min total if no new data)
```bash
licenciaminer collect mg --scrape --all-activities   # Incremental
licenciaminer collect mg-docs --mining-only            # Incremental
licenciaminer collect mg-textos --mining-only           # Incremental
licenciaminer collect ibama                             # Full, 5 sec
licenciaminer collect infracoes                         # Full, 20 sec
licenciaminer collect cfem                              # Full, 10 sec
licenciaminer collect copam                             # Incremental, ~1 min
```

### Weekly (slower)
```bash
licenciaminer collect anm --uf MG                      # Full, 17 min
licenciaminer collect spatial --layer all               # Full, ~7 min
```

### Quarterly / As needed
```bash
licenciaminer collect cnpj                             # Incremental, ~3 hrs first time
licenciaminer collect ral                              # Full, 2 sec
licenciaminer collect outorgas                         # When ANA portal is back
```

---

## BLOCKED SOURCES (retry when available)

| Source | Issue | Collector | Command |
|--------|-------|-----------|---------|
| CECAV caves | Shapefile URL returned 404 | `spatial.py:collect_cecav_caves` | `collect spatial --layer caves` |
| ANA water rights | Portal returning 504 timeout | `ana_outorgas.py:collect_ana_outorgas` | `collect outorgas` |

Both collectors are fully built and tested. Just need external portals to come back.

---

## FILE INVENTORY

```
data/processed/
  mg_semad_licencas.parquet      120 MB   42,758 decisions + PDF text
  ibama_infracoes.parquet        130 MB   702,280 infractions
  anm_processos.parquet            4 MB   50,723 mining processes
  anm_spatial_overlaps.parquet     ? MB   50,725 with UC/TI/bioma flags
  anm_cfem.parquet               2.4 MB   91,026 royalty payments
  anm_ral.parquet                  ? MB   1,013 production records
  copam_cmi_reunioes.parquet       ? MB   135 meetings, 2,234 docs
  ibama_licencas.parquet         0.04 MB  1,115 federal licenses
  cnpj_empresas.parquet            ? MB   ~6,300+ (growing)
  collection_metadata.json                Timestamps per source

data/reference/
  icmbio_ucs.parquet                     344 conservation units
  funai_tis.parquet                      16 indigenous territories
  ibge_biomas.parquet                    6 biomes
  anm_geometrias_mg.parquet              50,725 mining polygons
```

---

## LAYER 6: Market Intelligence

### 6A. BCB PTAX Exchange Rates
| Field | Value |
|-------|-------|
| **What** | Daily USD/BRL exchange rates (buy/sell) from Banco Central |
| **Where (source)** | https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/ |
| **Where (local)** | `data/processed/bcb_cotacoes.parquet` |
| **Key fields** | data, cotacao_compra, cotacao_venda |
| **Refresh** | `licenciaminer collect bcb` (full overwrite, ~2 sec) |
| **Frequency** | Weekly |
| **Status** | ✅ Complete |

### 6B. Comex Stat Mining Trade
| Field | Value |
|-------|-------|
| **What** | Export/import data for mineral products (NCM chapter 26) |
| **Where (source)** | https://api-comexstat.mdic.gov.br/ |
| **Where (local)** | `data/processed/comex_mineracao.parquet` |
| **Key fields** | ano, mes, capitulo_ncm, posicao_ncm, uf, pais, valor_fob_usd, peso_kg, fluxo |
| **Refresh** | `licenciaminer collect comex` (full overwrite, ~5 sec) |
| **Frequency** | Monthly |
| **Status** | ✅ Complete |

### 6C. Commodity Prices (Manual)
| Field | Value |
|-------|-------|
| **What** | Iron ore, gold, niobium spot prices |
| **Where (source)** | Investing.com, IndexMundi, TradingEconomics (manual) |
| **Where (local)** | `data/reference/commodity_prices.csv` |
| **Key fields** | data, mineral, preco_usd, unidade, fonte |
| **Refresh** | Upload via Inteligência Comercial page UI |
| **Frequency** | Monthly (manual) |
| **Status** | ✅ Template with sample data |

---

## LAYER 7: Reference Data (Due Diligence)

### 7A. DD Document Inventory
| Field | Value |
|-------|-------|
| **What** | 119 documents mapped for environmental licensing compliance |
| **Where (source)** | Extracted from Excel model (DN COPAM 217/2017 + MG legislation) |
| **Where (local)** | `data/reference/dd_inventario_documentos.csv` |
| **Key fields** | num, licenca, documento, doc_id, modalidade, fase |
| **Status** | ✅ Complete |

### 7B. DD Compliance Tests
| Field | Value |
|-------|-------|
| **What** | 1,934 adherence tests mapped across all document types |
| **Where (source)** | Extracted from Excel model |
| **Where (local)** | `data/reference/dd_requisitos_testes.csv` |
| **Key fields** | requisito_id, documento, topico, teste_aderencia, evidencia_esperada, peso |
| **Status** | ✅ Complete |

### 7C. DD Weighting Table
| Field | Value |
|-------|-------|
| **What** | 8 risk weighting levels (4 Operational + 4 Legal) |
| **Where (source)** | Extracted from Excel model |
| **Where (local)** | `data/reference/dd_ponderacao.csv` |
| **Status** | ✅ Complete |

---

## REFRESH COMMANDS (Updated)

### Daily/Weekly (fast)
```bash
licenciaminer collect mg --scrape --all-activities
licenciaminer collect mg-docs --mining-only
licenciaminer collect ibama
licenciaminer collect infracoes
licenciaminer collect cfem
licenciaminer collect copam
licenciaminer collect bcb                              # New: exchange rates
```

### Weekly (slower)
```bash
licenciaminer collect anm --uf MG
licenciaminer collect spatial --layer all
licenciaminer collect comex                            # New: trade data
```

### Quarterly / As needed
```bash
licenciaminer collect cnpj
licenciaminer collect ral
```

### All automated sources
```bash
licenciaminer collect all    # Includes bcb and comex
```

---

## FILE INVENTORY (Updated)

```
data/processed/
  mg_semad_licencas.parquet      120 MB   42,758 decisions + PDF text
  ibama_infracoes.parquet        130 MB   702,280 infractions
  anm_processos.parquet            4 MB   50,723 mining processes
  anm_spatial_overlaps.parquet     ? MB   50,725 with UC/TI/bioma flags
  anm_cfem.parquet               2.4 MB   91,026 royalty payments
  anm_ral.parquet                  ? MB   1,013 production records
  copam_cmi_reunioes.parquet       ? MB   135 meetings, 2,234 docs
  ibama_licencas.parquet         0.04 MB  1,115 federal licenses
  cnpj_empresas.parquet            ? MB   ~6,300+ (growing)
  bcb_cotacoes.parquet             ? MB   ~500 daily rates (24 months)
  comex_mineracao.parquet          ? MB   Mining trade data (5 years)
  collection_metadata.json                Timestamps per source

data/reference/
  icmbio_ucs.parquet                     344 conservation units
  funai_tis.parquet                      16 indigenous territories
  ibge_biomas.parquet                    6 biomes
  anm_geometrias_mg.parquet              50,725 mining polygons
  dd_inventario_documentos.csv           119 DD documents
  dd_requisitos_testes.csv               1,934 DD compliance tests
  dd_ponderacao.csv                      8 weighting levels
  comex_ncm_mineracao.csv                17 mineral NCM codes
  commodity_prices.csv                   Commodity price template
```
