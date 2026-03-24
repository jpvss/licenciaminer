"""Camada de dados para o app Streamlit.

Wrapper sobre licenciaminer.database com caching Streamlit.
"""

import json

import duckdb
import streamlit as st

from licenciaminer.config import DATA_DIR
from licenciaminer.database.loader import create_views
from licenciaminer.database.schema import PARQUET_SOURCES


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    """Retorna conexão DuckDB em memória com views sobre parquets."""
    con = duckdb.connect(":memory:")
    create_views(con, DATA_DIR)
    return con


@st.cache_data(ttl=300)
def run_query(query: str, params: list | None = None) -> list[dict]:
    """Executa query no DuckDB e retorna lista de dicts."""
    con = get_connection()
    result = con.execute(query, params) if params else con.execute(query)
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return [dict(zip(columns, row, strict=False)) for row in rows]


@st.cache_data(ttl=300)
def run_query_df(query: str, params: list | None = None):
    """Executa query e retorna DataFrame pandas."""
    con = get_connection()
    result = con.execute(query, params) if params else con.execute(query)
    return result.df()


def load_metadata() -> dict:
    """Carrega metadados de coleta."""
    meta_path = DATA_DIR / "processed" / "collection_metadata.json"
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_source_info() -> list[dict]:
    """Retorna informações de cada fonte de dados."""
    metadata = load_metadata()
    sources = []

    source_urls = {
        "mg_semad": "https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca",
        "ibama_licencas": "https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json",
        "anm_processos": "https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0",
        "ibama_infracoes": "https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao",
        "anm_cfem": "https://app.anm.gov.br/dadosabertos/ARRECADACAO/",
        "anm_ral": "https://app.anm.gov.br/dadosabertos/AMB/",
        "receita_federal_cnpj": "https://brasilapi.com.br/api/cnpj/v1/",
        "copam_cmi": "https://sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam/index-externo",
        "icmbio_ucs": "https://www.gov.br/icmbio/pt-br/assuntos/dados_geoespaciais/",
        "funai_tis": "https://geoserver.funai.gov.br/geoserver/Funai/ows",
        "ibge_biomas": "http://geoftp.ibge.gov.br/informacoes_ambientais/",
        "spatial_overlaps": "(computado a partir de ANM + UCs + TIs + biomas)",
    }

    source_names = {
        "mg_semad": "MG SEMAD Decisões",
        "ibama_licencas": "IBAMA Licenças Federais",
        "anm_processos": "ANM SIGMINE Processos",
        "ibama_infracoes": "IBAMA Infrações Ambientais",
        "anm_cfem": "ANM CFEM Royalties",
        "anm_ral": "ANM RAL Produção",
        "receita_federal_cnpj": "Receita Federal CNPJ",
        "copam_cmi": "COPAM CMI Reuniões",
        "icmbio_ucs": "ICMBio Unidades Conservação",
        "funai_tis": "FUNAI Terras Indígenas",
        "ibge_biomas": "IBGE Biomas",
        "spatial_overlaps": "Sobreposições Espaciais",
    }

    for source_key, display_name in source_names.items():
        meta = metadata.get(source_key, {})
        records_raw = meta.get("records", "—")
        # Convert string records to int for formatting
        try:
            records = int(records_raw) if records_raw != "—" else "—"
        except (ValueError, TypeError):
            records = records_raw

        last_collected = meta.get("last_collected", "—")
        last_collected = (
            str(last_collected)[:10]
            if last_collected not in ("—", "")
            else "—"
        )

        sources.append({
            "Fonte": display_name,
            "Registros": records,
            "Atualização": last_collected,
            "URL": source_urls.get(source_key, ""),
        })

    return sources


def get_dataset_options() -> dict[str, str]:
    """Retorna datasets disponíveis para exploração."""
    con = get_connection()
    processed = DATA_DIR / "processed"
    options = {}
    for view_name, parquet_spec in PARQUET_SOURCES.items():
        # Check existence for single file or list of parts
        if isinstance(parquet_spec, list):
            exists = all((processed / f).exists() for f in parquet_spec)
        else:
            exists = (processed / parquet_spec).exists()

        if exists:
            try:
                count = con.execute(
                    f"SELECT COUNT(*) FROM {view_name}"
                ).fetchone()
                n = count[0] if count else 0
                display = view_name.replace("v_", "").replace("_", " ").title()
                options[f"{display} ({n:,})"] = view_name
            except Exception:
                pass
    return options
