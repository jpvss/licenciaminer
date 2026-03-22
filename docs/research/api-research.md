# API & Framework Research — LicenciaMiner

Compiled: 2026-03-21

---

## 1. IBAMA SISLIC Open Data

- **URL**: `https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json`
- **Also available**: CSV, XML, HTML at same path with different extension
- **Type**: Static JSON dump (NOT a REST API — no query params, no pagination)
- **Update**: Listed as daily; last confirmed live March 2026
- **Size**: ~450+ records (relatively small)
- **Fields**: `desTipoLicenca`, `numLicenca`, `dataEmissao`, `dataVencimento`, `empreendimento`, `nomePessoa`, `numeroProcesso`, `tipologia`, `pac`, `Atualizacao`
- **Mining filter**: `tipologia` contains "Mineração"
- **Date format**: DD/MM/YYYY strings
- **LIMITATION**: Only emitted licenses (deferimentos). No rejections.
- **No CNPJ field** — must bridge via company name matching or spatial overlap
- **No rate limiting** documented

## 2. ANM SIGMINE (ArcGIS REST)

- **URL**: `https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0/query`
- **Type**: ArcGIS FeatureServer REST API
- **MaxRecordCount**: 5,000 per query (32,000 without geometry)
- **Geometry**: esriGeometryPolygon, EPSG 4674 (SIRGAS 2000)
- **Fields**: `PROCESSO`, `NUMERO`, `ANO`, `AREA_HA`, `FASE`, `ULT_EVENTO`, `NOME`, `SUBS`, `USO`, `UF`, `ID`, `FID`, `DSProcesso`
- **Date format**: Epoch milliseconds
- **Key params**: `where`, `outFields`, `returnGeometry`, `f=json`, `resultOffset`, `resultRecordCount`, `orderByFields`
- **Pagination**: `resultOffset` may work — check `exceededTransferLimit` in response
- **Fallback**: Iterate by UF, then by FASE if any UF exceeds 5000
- **FASE values** (known): REQUERIMENTO DE PESQUISA, AUTORIZAÇÃO DE PESQUISA, REQUERIMENTO DE LAVRA, CONCESSÃO DE LAVRA, LICENCIAMENTO, REGISTRO DE EXTRAÇÃO, DISPONIBILIDADE, others
- **CRITICAL**: "LICENCIAMENTO" at ANM = mining regime, NOT environmental licensing
- **Bulk download**: Shapefiles at `https://app.anm.gov.br/dadosabertos/SIGMINE/PROCESSOS_MINERARIOS/BRASIL.zip`
- **CSVs**: `https://app.anm.gov.br/dadosabertos/scm/`

## 3. MG SEMAD (Manual Excel)

- **Portal**: `https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca`
- **Type**: JavaScript form — manual download only
- **Format**: Excel 2007+ (.xlsx)
- **~42,758 decisions** available
- **Fields**: Regional, Município, Empreendimento, CNPJ/CPF, Modalidade, Processo Administrativo, Protocolo, Código de Atividade, Atividade, Classe (1-6), Ano, Mês, Data Publicação DOEMG, **Decisão** (deferido/indeferido)
- **Mining codes**: A-01 to A-07 (filter codes starting with "A-0")
- **Date format**: DD/MM/YYYY
- **UNIQUE VALUE**: Only source with deferimento/indeferimento outcomes

## 4. DN COPAM 217/2017 Classification

| | Pot. Poluidor P | Pot. Poluidor M | Pot. Poluidor G |
|---|---|---|---|
| **Porte P** | Classe 1 | Classe 2 | Classe 4 |
| **Porte M** | Classe 2 | Classe 3 | Classe 5 |
| **Porte G** | Classe 3 | Classe 5 | Classe 6 |

Mining activity codes:
- A-01: Pesquisa mineral
- A-02: Lavra a céu aberto
- A-03: Lavra subterrânea (or materials de uso imediato per kickoff)
- A-04: Lavra por dragagem / água mineral
- A-05: Beneficiamento mineral / unidades operacionais
- A-06: Pilhas de estéril / barragens de rejeito / óleo e gás
- A-07: Transporte e infraestrutura minerária / pesquisa mineral

Licensing modalities:
- Classes 1-2: LAS (simplificado) — generally NOT allowed for mining
- Classes 3-4: LAC (concomitante)
- Classes 5-6: LAT (trifásico: LP → LI → LO)

## 5. Brazilian Environmental Licensing Framework

| License | Phase | Validity |
|---------|-------|----------|
| LP (Licença Prévia) | Planning | Up to 5 years |
| LI (Licença de Instalação) | Construction | Up to 6 years |
| LO (Licença de Operação) | Operation | 4-10 years |

- **Deferimento** = approval/granting
- **Indeferimento** = denial/rejection
- **Jurisdiction**: IBAMA (federal/cross-state), SEMAD (state MG), Municipal (local impact)
- **CNPJ** = primary bridge key between ANM mining rights and environmental licenses
- **Lei 15.190/2025** = new general licensing law, mandates 100% digital within 3 years

## 6. Tech Stack Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package manager | **uv** | 10-100x faster than pip, single tool for venv+deps+lockfile |
| Project layout | **src/ layout** | Prevents accidental imports, catches packaging errors |
| HTTP client | **httpx** | Async support, HTTP/2, nearly identical to requests API |
| Retry logic | **tenacity** | Mature, decorator-based, exponential backoff |
| CLI framework | **Click** | Best composability for multi-command pipelines |
| Database | **DuckDB** views over Parquet | No data duplication, automatic filter pushdown |
| Data processing | **pandas** (Excel) + **pyarrow** (Parquet) | Polars optional for performance |
| Build backend | **hatchling** | Simple, fast, modern |
