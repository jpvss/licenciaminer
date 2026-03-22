# Data Registry — LicenciaMiner

Last updated: 2026-03-22

## How to Read This Document

Each data source is documented with:
- **What**: description and record count
- **Where**: source URL and local file path
- **Bridge**: how it connects to other sources
- **Refresh**: command and frequency
- **Status**: ✅ done, 🔄 running, ⏳ pending

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
| **Frequency** | Weekly (new decisions published weekly) |
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
| **Status** | 🔄 Re-enriching (1,200/8,072) |

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
| **Status** | ✅ Complete (6,964/8,072 = 86.6% coverage) |

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
| **Limitation** | Only emitted licenses — no rejections |
| **Status** | ✅ Complete |

### 1E. ANM SIGMINE Mining Processes
| Field | Value |
|-------|-------|
| **What** | 50,723 mining processes in MG (titles, phases, substances, areas) |
| **Where (source)** | https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0/query |
| **Where (local)** | `data/processed/anm_processos.parquet` (4 MB) |
| **Key fields** | PROCESSO, NOME, FASE, SUBS, UF, AREA_HA, ANO |
| **Bridge keys** | `NOME` (company name), `PROCESSO` → spatial overlaps |
| **Refresh** | `licenciaminer collect anm --uf MG` (full overwrite, ~17 min) |
| **Frequency** | Weekly |
| **Note** | resultOffset is ignored by server — uses UF→FASE→ANO iteration |
| **Status** | ✅ Complete |

---

## LAYER 2: Company Profile

### 2A. IBAMA Environmental Infractions
| Field | Value |
|-------|-------|
| **What** | 702,280 environmental infraction records (all Brazil, 113K in MG) |
| **Where (source)** | https://dadosabertos.ibama.gov.br/dados/SIFISC/auto_infracao/auto_infracao/auto_infracao_csv.zip |
| **Where (local)** | `data/processed/ibama_infracoes.parquet` (130 MB) |
| **Key fields** | CPF_CNPJ_INFRATOR, UF, valor_multa, tipo_infracao, data_auto |
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
| **Bridge keys** | `CPF_CNPJ` → SEMAD cnpj_cpf |
| **Refresh** | `licenciaminer collect cfem` (full overwrite, ~10 sec) |
| **Frequency** | Monthly |
| **Note** | ValorRecolhido stored as string with comma decimal — use REPLACE in queries |
| **Status** | ✅ Complete |

### 2C. Receita Federal CNPJ Data
| Field | Value |
|-------|-------|
| **What** | Company profiles (razão social, CNAE, porte, data abertura, situação) |
| **Where (source)** | https://brasilapi.com.br/api/cnpj/v1/{CNPJ} |
| **Where (local)** | `data/processed/cnpj_empresas.parquet` |
| **Key fields** | cnpj, razao_social, cnae_fiscal, porte, data_abertura, situacao |
| **Bridge keys** | `cnpj` → SEMAD cnpj_cpf |
| **Refresh** | `licenciaminer collect cnpj` (incremental, skips fetched, ~0.5s/query) |
| **Frequency** | Quarterly (Receita Federal updates quarterly) |
| **Note** | ~30% of source CNPJs are invalid (handled gracefully, returns 400) |
| **Status** | 🔄 Running (3,700/21,840) |

### 2D. ANM RAL Production Reports
| Field | Value |
|-------|-------|
| **What** | Annual production declarations (reserves, workforce, output) |
| **Where (source)** | https://app.anm.gov.br/dadosabertos/ (exact path TBD) |
| **Where (local)** | `data/processed/anm_ral.parquet` |
| **Key fields** | Processo, CNPJ, substância, quantidade_produzida, ano |
| **Bridge keys** | `Processo` → ANM, `CNPJ` → SEMAD |
| **Refresh** | TBD |
| **Status** | ⏳ Pending — need to locate correct CSV URL |

---

## LAYER 3: Spatial Restrictions

### 3A. ICMBio Conservation Units (UCs)
| Field | Value |
|-------|-------|
| **What** | 344 federal conservation units (polygons) |
| **Where (source)** | https://www.gov.br/icmbio/pt-br/assuntos/dados_geoespaciais/ |
| **Where (local)** | `data/reference/icmbio_ucs.parquet` |
| **Key fields** | nome, categoria, grupo (proteção integral vs uso sustentável) |
| **Bridge keys** | Spatial overlap with ANM polygons |
| **Refresh** | `licenciaminer collect spatial --layer ucs` (~10 sec) |
| **Frequency** | Monthly |
| **Status** | ✅ Complete |

### 3B. FUNAI Indigenous Territories (TIs)
| Field | Value |
|-------|-------|
| **What** | 16 indigenous territories in MG (polygons) |
| **Where (source)** | https://geoserver.funai.gov.br/geoserver/Funai/ows (WFS, filtered MG) |
| **Where (local)** | `data/reference/funai_tis.parquet` |
| **Key fields** | nome, fase_ti (regularizada, homologada, etc.) |
| **Bridge keys** | Spatial overlap with ANM polygons |
| **Refresh** | `licenciaminer collect spatial --layer tis` (~2 sec) |
| **Frequency** | Monthly |
| **Status** | ✅ Complete |

### 3C. IBGE Biomes
| Field | Value |
|-------|-------|
| **What** | 6 Brazilian biomes (polygons, 1:250,000) |
| **Where (source)** | http://geoftp.ibge.gov.br/informacoes_ambientais/estudos_ambientais/biomas/ |
| **Where (local)** | `data/reference/ibge_biomas.parquet` |
| **Key fields** | Bioma (Mata Atlântica, Cerrado, Caatinga, etc.) |
| **Bridge keys** | Spatial overlay with ANM polygons |
| **Refresh** | `licenciaminer collect spatial --layer biomas` (~7 sec) |
| **Frequency** | Yearly (biome boundaries rarely change) |
| **Status** | ✅ Complete |

### 3D. ANM Geometries (Mining Polygons)
| Field | Value |
|-------|-------|
| **What** | 50,725 MG mining process polygons (from 265K national) |
| **Where (source)** | https://app.anm.gov.br/dadosabertos/SIGMINE/PROCESSOS_MINERARIOS/BRASIL.zip (122 MB) |
| **Where (local)** | `data/reference/anm_geometrias_mg.parquet` |
| **Key fields** | PROCESSO, geometry (polygon) |
| **Bridge keys** | `PROCESSO` → ANM processos, spatial join with UCs/TIs/biomas |
| **Refresh** | `licenciaminer collect spatial --layer anm-geo` (~15 sec) |
| **Frequency** | Weekly |
| **Status** | ✅ Complete |

### 3E. Spatial Overlaps (Computed)
| Field | Value |
|-------|-------|
| **What** | Pre-computed spatial joins: 50,725 ANM processes × UCs/TIs/biomas |
| **Where (local)** | `data/processed/anm_spatial_overlaps.parquet` |
| **Key fields** | PROCESSO, tem_uc, ucs_sobrepostas, tem_ti, tis_sobrepostas, biomas |
| **Key results** | 949 processes in UCs (1.9%), 113 in TIs (0.2%) |
| **Bridge keys** | `PROCESSO` → ANM |
| **Refresh** | `licenciaminer collect spatial --layer overlaps` (~6 min) |
| **Frequency** | After anm-geo + UCs/TIs refresh |
| **Status** | ✅ Complete |

---

## LAYER 4: Governance (PENDING)

### 4A. COPAM Meeting Data
| Field | Value |
|-------|-------|
| **What** | 1,761 COPAM meetings, ~150-200 CMI (mining chamber) |
| **Where (source)** | https://sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam/index-externo |
| **Where (local)** | TBD |
| **Key fields** | date, title, items/processes discussed, PDFs (Decisão, Pauta, Parecer) |
| **Bridge keys** | Process number, company name → SEMAD decisions |
| **Refresh** | TBD (scraper not built yet) |
| **Status** | ⏳ Pending |

### 4B. CECAV Cave Registry
| Field | Value |
|-------|-------|
| **What** | 18,000+ caves (points/polygons), relevance classification |
| **Where (source)** | https://www.gov.br/icmbio/pt-br/assuntos/centros-de-pesquisa/cavernas/ |
| **Where (local)** | TBD |
| **Key fields** | location, relevance (máxima, alta, média, baixa) |
| **Bridge keys** | Spatial proximity (250m buffer for máxima relevance) |
| **Refresh** | TBD |
| **Status** | ⏳ Pending |

### 4C. ANA Water Rights
| Field | Value |
|-------|-------|
| **What** | Federal water use permits (outorgas) |
| **Where (source)** | https://dados.ana.gov.br/dataset/outorgas-de-direito-de-uso-de-recursos-hidricos |
| **Where (local)** | TBD |
| **Key fields** | CNPJ, coordinates, finalidade, vazão |
| **Bridge keys** | `CNPJ` → SEMAD, spatial |
| **Refresh** | TBD |
| **Status** | ⏳ Pending |

---

## CROSS-SOURCE JOINS

All joins happen at query time via DuckDB views. No data is duplicated.

```
SEMAD (cnpj_cpf) ←→ IBAMA infrações (CPF_CNPJ_INFRATOR, needs REGEXP_REPLACE)
SEMAD (cnpj_cpf) ←→ CFEM (CPF_CNPJ)
SEMAD (cnpj_cpf) ←→ CNPJ empresas (cnpj)
ANM (PROCESSO)   ←→ Spatial overlaps (PROCESSO)
ANM (PROCESSO)   ←→ CFEM (Processo)
SEMAD (detail_id) → PDF docs → PDF text
```

**Known CNPJ join rates:**
- SEMAD mining → IBAMA infrações: **309/4,206** unique CNPJs (7.3%)
- SEMAD mining → CFEM: **1,584/4,206** (37.6%)

---

## REFRESH COMMANDS (Daily/Weekly)

```bash
# 1. New SEMAD decisions (incremental, ~1 sec if no new)
licenciaminer collect mg --scrape --all-activities

# 2. PDF links for new records (incremental)
licenciaminer collect mg-docs --mining-only

# 3. PDF text for new records (incremental)
licenciaminer collect mg-textos --mining-only

# 4. Fast full-overwrite sources (~30 sec total)
licenciaminer collect ibama
licenciaminer collect infracoes
licenciaminer collect cfem

# 5. Spatial layers (weekly)
licenciaminer collect spatial --layer all

# 6. CNPJ for new companies (incremental)
licenciaminer collect cnpj

# 7. ANM processes (weekly, 17 min)
licenciaminer collect anm --uf MG
```

---

## PENDING DATA COLLECTION

| # | Source | Effort | Value | Depends On |
|---|--------|--------|-------|------------|
| 1 | **ANM RAL production** | 20 min | 8/10 | Find CSV URL |
| 2 | **COPAM CMI meetings** | 2 hours | 10/10 | Nothing |
| 3 | **CECAV caves** | 30 min | 8/10 | Nothing |
| 4 | **ANA water rights** | 30 min | 7/10 | Nothing |
| 5 | **Commodity prices** | 15 min | 5/10 | Nothing |

After these 5, the MG data foundation is complete for product development.
