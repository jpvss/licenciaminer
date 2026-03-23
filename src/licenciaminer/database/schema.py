"""Definições de schema para o DuckDB."""

# Mapeamento de views para arquivos parquet
PARQUET_SOURCES: dict[str, str] = {
    "v_ibama": "ibama_licencas.parquet",
    "v_anm": "anm_processos.parquet",
    "v_mg_semad": "mg_semad_licencas.parquet",
    "v_ibama_infracoes": "ibama_infracoes.parquet",
    "v_cfem": "anm_cfem.parquet",
    "v_cnpj": "cnpj_empresas.parquet",
    "v_spatial": "anm_spatial_overlaps.parquet",
    "v_copam": "copam_cmi_reunioes.parquet",
    "v_ral": "anm_ral.parquet",
}
