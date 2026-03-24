"""Camada de dados para o app Streamlit.

Wrapper sobre licenciaminer.database com caching Streamlit.
"""

import json
import logging
from pathlib import Path

import duckdb
import streamlit as st

logger = logging.getLogger(__name__)

from licenciaminer.config import DATA_DIR
from licenciaminer.database.loader import create_views
from licenciaminer.database.schema import PARQUET_SOURCES


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    """Retorna conexão DuckDB com views sobre parquets.

    Usa banco em arquivo temporário para reduzir uso de RAM
    (DuckDB faz spill to disk quando necessário).
    """
    import tempfile
    db_dir = tempfile.mkdtemp(prefix="licenciaminer_")
    db_path = str(Path(db_dir) / "app.duckdb")
    con = duckdb.connect(db_path)
    # Limit memory usage for Streamlit Cloud (1GB container)
    con.execute("SET memory_limit = '400MB'")
    con.execute("SET threads = 2")
    create_views(con, DATA_DIR)
    return con


@st.cache_data(ttl=300, max_entries=30)
def run_query(query: str, params: list | None = None) -> list[dict]:
    """Executa query no DuckDB e retorna lista de dicts.

    Usa cursor separado para thread-safety entre sessões Streamlit.
    """
    con = get_connection()
    cursor = con.cursor()
    try:
        result = cursor.execute(query, params) if params else cursor.execute(query)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [dict(zip(columns, row, strict=False)) for row in rows]
    finally:
        cursor.close()


@st.cache_data(ttl=120, max_entries=15)
def run_query_df(query: str, params: list | None = None):
    """Executa query e retorna DataFrame pandas.

    Usa cursor separado para thread-safety entre sessões Streamlit.
    """
    con = get_connection()
    cursor = con.cursor()
    try:
        result = cursor.execute(query, params) if params else cursor.execute(query)
        return result.df()
    finally:
        cursor.close()


# ── Brazilian number formatting ──

def fmt_br(n: float | int, decimals: int = 0) -> str:
    """Formata número no padrão brasileiro: 1.234.567,89."""
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    if decimals > 0:
        formatted = f"{n:,.{decimals}f}"
    else:
        formatted = f"{n:,.0f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_reais(n: float | None) -> str:
    """Formata como R$ 1.234,56."""
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    return f"R$ {fmt_br(n, 2)}"


def fmt_pct(n: float | None) -> str:
    """Formata como 85,3%."""
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    return f"{fmt_br(n, 1)}%"


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
        "anm_scm": "https://app.anm.gov.br/dadosabertos/SCM/",
        "concessoes_mg": "(consolidado: SCM + SIGMINE + CFEM)",
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
        "anm_scm": "ANM SCM Concessões",
        "concessoes_mg": "Concessões MG Consolidadas",
    }

    # Map source keys to parquet filenames for fallback row counting
    # For split files, list all parts to sum rows
    _source_parquets: dict[str, str | list[str]] = {
        "ibama_licencas": "ibama_licencas.parquet",
        "anm_processos": "anm_processos.parquet",
        "ibama_infracoes": [
            "ibama_infracoes_part1.parquet",
            "ibama_infracoes_part2.parquet",
        ],
        "anm_cfem": "anm_cfem.parquet",
        "receita_federal_cnpj": "cnpj_empresas.parquet",
    }

    for source_key, display_name in source_names.items():
        meta = metadata.get(source_key, {})
        records_raw = meta.get("records", "—")
        # Convert string records to int for formatting
        try:
            records = int(records_raw) if records_raw != "—" else "—"
        except (ValueError, TypeError):
            records = records_raw

        # Fallback: count parquet rows if metadata missing
        if records == "—" and source_key in _source_parquets:
            pq_spec = _source_parquets[source_key]
            pq_files = pq_spec if isinstance(pq_spec, list) else [pq_spec]
            try:
                import pyarrow.parquet as pq
                total_rows = 0
                for pq_name in pq_files:
                    pq_path = DATA_DIR / "processed" / pq_name
                    if pq_path.exists():
                        total_rows += pq.read_metadata(pq_path).num_rows
                if total_rows > 0:
                    records = total_rows
            except Exception:
                pass

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


# Shared constants used across multiple pages
REGIME_LABELS = {
    "portaria_lavra": "Portaria de Lavra",
    "licenciamento": "Licenciamento",
    "plg": "Lavra Garimpeira (PLG)",
    "registro_extracao": "Registro de Extração",
}


def safe_query(
    query: str,
    params: list | None = None,
    context: str = "",
    fallback: list | None = None,
) -> list[dict] | None:
    """Executa query com tratamento de erro diferenciado.

    Distingue entre 'dados não coletados' (CatalogException) e erros reais.
    Retorna fallback em caso de erro, mostrando mensagem adequada no Streamlit.
    """
    try:
        result = run_query(query, params)
        return result if result else fallback
    except duckdb.CatalogException:
        view_name = context or "fonte"
        st.warning(f"Dados não disponíveis: {view_name}. Execute `licenciaminer collect`.")
        logger.warning("View não encontrada para: %s", context)
        return fallback
    except Exception as e:
        logger.exception("Erro em query: %s", context)
        st.error(f"Erro ao consultar {context}: {e}")
        return fallback


def get_dataset_options() -> dict[str, str]:
    """Retorna datasets disponíveis para exploração."""
    get_connection()  # Ensure views exist
    processed = DATA_DIR / "processed"
    options = {}
    for view_name, parquet_spec in PARQUET_SOURCES.items():
        # Check existence for single file or list of parts (with fallback)
        if isinstance(parquet_spec, list):
            exists = all((processed / f).exists() for f in parquet_spec)
            if not exists:
                # Fallback: single file (e.g. xxx_part1.parquet → xxx.parquet)
                base_name = parquet_spec[0].replace("_part1", "")
                exists = (processed / base_name).exists()
        else:
            exists = (processed / parquet_spec).exists()

        if exists:
            display = view_name.replace("v_", "").replace("_", " ").title()
            options[display] = view_name
    return options
