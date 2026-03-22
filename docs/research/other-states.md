# Other States' Licensing Data Availability

Compiled: 2026-03-21

## Key Finding

No cross-state licensing database exists. Lei 15.190/2025 mandates standardization by ~Feb 2029. Until then, state-by-state collection is needed.

## Expansion Priority Order

| Priority | State | Agency | Effort | Why |
|----------|-------|--------|--------|-----|
| **1** | **SP** | CETESB | LOW | Open data catalog with deferido/indeferido outcomes |
| **2** | **BA** | INEMA/SEIA | MEDIUM | Public consultation portal, significant mining |
| **3** | **GO** | SEMAD/IPE | MEDIUM | Public search (31-day windows), iterative feasible |
| **4** | **SC** | IMA | MEDIUM | Fully digital SINFATWEB, public consultation |
| **5** | **PA** | SEMAS/SIMLAM | HIGH | Largest mining state but data locked per-process |
| **6** | **RS** | FEPAM/SOL | MEDIUM | Digital system, moderate mining |
| **7** | **MA** | SEMA/SIGLA→GUARA | HIGH | System in transition, many mines under IBAMA anyway |
| **8** | **RJ** | INEA | HIGH | No open data, limited mining |
| **9** | **MT** | SEMA/SIGA | VERY HIGH | Requires registration + process number |

## Best Opportunities

### SP (CETESB) — Lowest Hanging Fruit
- **URL**: https://cetesb.sp.gov.br/catalogo-de-dados-abertos/
- Publishes: licenses granted, licenses requested, infractions, appeals, TACs, AND **indeferimentos**
- Formal open data catalog — likely CSV/structured
- Lower mining volume than PA/BA but best data quality

### BA (INEMA) — High Mining + Public Portal
- **URL**: http://www.seia.ba.gov.br/fiscalizacao/consulta-licenciamento
- Public consultation of licensing processes
- Gold, iron ore, chromite mining
- LP+LI can be issued simultaneously for mining

### GO (SEMAD) — Public but Constrained
- **URL**: https://portal.meioambiente.go.gov.br/prodExterno/_pubconprocesso/
- Advanced search with 31-day window limit
- Iterative month-by-month collection feasible
- Nickel, gold, phosphate

### PA (SEMAS) — Biggest Prize, Hardest Access
- SIMLAM: https://monitoramento.semas.pa.gov.br/simlam/
- Process-by-process lookup only, no bulk download
- Largest mining state (Vale, Carajás)
- Many large mines under IBAMA federal jurisdiction (already in our SISLIC data)
- **Strategy**: LAI request + CNPJ/spatial bridge from ANM data

## Cross-State Resources

### PNLA (Portal Nacional de Licenciamento Ambiental)
- https://pnla.mma.gov.br/
- Aggregates basic data from participating states
- 4 states send NO data (AL, AP, RR, SE)
- Not useful for analytics — transparency portal only, no bulk download

### Lei 15.190/2025 Impact
- ALL licensing must be electronic in all phases
- States must integrate with SINIMA within 3 years (~Feb 2029)
- National data standardization mandated
- SP, SC will comply fastest; MT, AM will take longer

## Immediate Next Steps

1. Explore CETESB open data catalog — confirm CSV download of decisions
2. Submit LAI requests to PA (SEMAS) and MT (SEMA) for bulk mining licensing data
3. Test SEIA/BA and IPE/GO portals for scraping feasibility
4. Monitor Lei 15.190/2025 compliance progress

Sources: SEMAS PA, SEMAD GO, INEMA BA, SEMA MT, CETESB SP, INEA RJ, IMA SC, FEPAM RS, PNLA, Lei 15.190/2025
