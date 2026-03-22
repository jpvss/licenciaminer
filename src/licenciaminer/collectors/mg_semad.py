"""Processador de dados da SEMAD/MG (Excel de licenciamento ambiental)."""

import logging
from pathlib import Path

import pandas as pd

from licenciaminer.config import MG_DEFAULT_FILE, MG_MINING_CODE_PREFIX
from licenciaminer.processors.normalize import (
    add_metadata,
    atomic_parquet_write,
    normalize_cnpj,
    normalize_columns,
    parse_date_br,
)

logger = logging.getLogger(__name__)

# Colunas críticas que devem existir no Excel
REQUIRED_COLUMNS = {"Decisão", "Código de Atividade"}

# Todas as colunas esperadas
EXPECTED_COLUMNS = {
    "Regional",
    "Município",
    "Empreendimento",
    "CNPJ/CPF",
    "Modalidade",
    "Processo Administrativo",
    "Protocolo",
    "Código de Atividade",
    "Atividade",
    "Classe",
    "Ano",
    "Mês",
    "Data Publicação DOEMG",
    "Decisão",
}


def _validate_columns(df: pd.DataFrame) -> None:
    """Valida que as colunas críticas existem no DataFrame."""
    missing_critical = REQUIRED_COLUMNS - set(df.columns)
    if missing_critical:
        raise ValueError(
            f"Colunas obrigatórias ausentes no Excel da SEMAD: {missing_critical}. "
            "Verifique se o arquivo está no formato esperado."
        )

    missing_optional = EXPECTED_COLUMNS - set(df.columns)
    if missing_optional:
        logger.warning("MG SEMAD: colunas esperadas ausentes (não críticas): %s", missing_optional)


def _normalize_decisao(series: "pd.Series[str]") -> "pd.Series[str]":
    """Normaliza valores da coluna Decisão para padrão consistente."""
    mapping = series.str.strip().str.lower()
    result = mapping.map(
        lambda x: (
            "deferido"
            if isinstance(x, str) and "deferido" in x and "indeferido" not in x
            else (
                "indeferido"
                if isinstance(x, str) and "indeferido" in x
                else "outro"
            )
        )
    )
    return result


def process_mg_excel(data_dir: Path, file_path: Path | None = None) -> Path:
    """Processa o Excel de decisões da SEMAD/MG.

    Lê o arquivo Excel, filtra atividades minerárias (códigos A-0x),
    normaliza colunas e salva como parquet.
    """
    file_path = file_path or MG_DEFAULT_FILE
    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo da SEMAD/MG não encontrado: {file_path}. "
            "Faça o download manual em: "
            "https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca"
        )

    logger.info("MG SEMAD: lendo arquivo %s", file_path)
    df = pd.read_excel(file_path, engine="openpyxl", dtype={"CNPJ/CPF": str})
    logger.info("MG SEMAD: %d registros brutos lidos", len(df))

    # Validar colunas
    _validate_columns(df)

    # Filtrar atividades de mineração
    mask = df["Código de Atividade"].astype(str).str.startswith(MG_MINING_CODE_PREFIX)
    df = df[mask].copy()
    logger.info("MG SEMAD: %d registros de mineração após filtro", len(df))

    if df.empty:
        logger.warning("MG SEMAD: nenhum registro de mineração encontrado após filtro")

    # Normalizar decisão ANTES de normalizar colunas
    df["Decisão"] = _normalize_decisao(df["Decisão"])

    # Normalizar CNPJ/CPF
    if "CNPJ/CPF" in df.columns:
        df["CNPJ/CPF"] = df["CNPJ/CPF"].apply(
            lambda x: normalize_cnpj(str(x)) if pd.notna(x) else None
        )

    # Normalizar colunas para snake_case
    df = normalize_columns(df)

    # Parsear datas
    if "data_publicacao_doemg" in df.columns:
        df["data_publicacao_doemg"] = parse_date_br(df["data_publicacao_doemg"])

    # Garantir tipo da classe
    if "classe" in df.columns:
        df["classe"] = pd.to_numeric(df["classe"], errors="coerce")

    df = add_metadata(df, source="mg_semad")

    output_path = data_dir / "processed" / "mg_semad_licencas.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info("MG SEMAD: dados salvos em %s (%d registros)", output_path, len(df))
    return output_path
