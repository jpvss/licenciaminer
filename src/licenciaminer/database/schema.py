"""Definições de schema para o DuckDB."""

# Mapeamento de views para arquivos parquet.
# Valor pode ser string (arquivo único) ou lista (partes para UNION).
PARQUET_SOURCES: dict[str, str | list[str]] = {
    "v_ibama": "ibama_licencas.parquet",
    "v_anm": "anm_processos.parquet",
    "v_mg_semad": [
        "mg_semad_licencas_part1.parquet",
        "mg_semad_licencas_part2.parquet",
    ],
    "v_ibama_infracoes": [
        "ibama_infracoes_part1.parquet",
        "ibama_infracoes_part2.parquet",
    ],
    "v_cfem": "anm_cfem.parquet",
    "v_cnpj": "cnpj_empresas.parquet",
    "v_spatial": "anm_spatial_overlaps.parquet",
    "v_copam": "copam_cmi_reunioes.parquet",
    "v_ral": "anm_ral.parquet",
    "v_scm": "scm_concessoes.parquet",
    "v_concessoes": "concessoes_mg.parquet",
    "v_bcb_cotacoes": "bcb_cotacoes.parquet",
    "v_comex_mineracao": "comex_mineracao.parquet",
}
