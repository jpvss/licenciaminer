"""Pipeline de consolidação de concessões minerárias.

Junta dados do SCM (tabular), SIGMINE (geometria/área) e CFEM (atividade)
em um dataset unificado para análise e prospecção.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from licenciaminer.processors.normalize import (
    atomic_parquet_write,
    normalize_processo,
)

logger = logging.getLogger(__name__)


def _load_if_exists(path: Path) -> pd.DataFrame | None:
    """Carrega parquet se existir, senão retorna None."""
    if path.exists():
        return pd.read_parquet(path)
    logger.warning("Arquivo não encontrado: %s", path)
    return None


def _build_cfem_key(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói chave de processo normalizada para CFEM.

    CFEM tem Processo (número) e AnoDoProcesso (ano como float).
    """
    df = df.copy()
    df["_ano_str"] = df["AnoDoProcesso"].apply(
        lambda x: str(int(x)) if pd.notna(x) else ""
    )
    df["processo_norm"] = df.apply(
        lambda row: normalize_processo(f"{row['Processo']}/{row['_ano_str']}")
        if row["_ano_str"]
        else "",
        axis=1,
    )
    return df.drop(columns=["_ano_str"])


def join_concessions(data_dir: Path) -> Path:
    """Consolida SCM + SIGMINE + CFEM em dataset unificado.

    Estratégia de join:
    1. SCM ←LEFT JOIN→ SIGMINE on processo_norm (adiciona área_ha)
    2. Resultado ←LEFT JOIN→ CFEM agregado (adiciona cfem_total, ativo_cfem)
    3. Enriquece com classificação de substâncias
    """
    processed = data_dir / "processed"
    reference = data_dir / "reference"

    # --- Carregar SCM ---
    scm = _load_if_exists(processed / "scm_concessoes.parquet")
    if scm is None or scm.empty:
        raise FileNotFoundError(
            "scm_concessoes.parquet não encontrado. "
            "Execute 'licenciaminer collect scm' primeiro."
        )
    logger.info("SCM: %d registros carregados", len(scm))

    # --- Carregar e preparar SIGMINE ---
    sigmine = _load_if_exists(processed / "anm_processos.parquet")
    if sigmine is not None and not sigmine.empty:
        sigmine["processo_norm"] = sigmine["PROCESSO"].apply(normalize_processo)
        # Manter apenas colunas úteis para o join
        sigmine_cols = ["processo_norm", "AREA_HA", "SUBS", "FASE", "ULT_EVENTO"]
        sigmine_cols = [c for c in sigmine_cols if c in sigmine.columns]
        sigmine_dedup = sigmine[sigmine_cols].drop_duplicates(subset=["processo_norm"])
        logger.info("SIGMINE: %d processos únicos para join", len(sigmine_dedup))
    else:
        sigmine_dedup = pd.DataFrame(columns=["processo_norm"])
        logger.warning("SIGMINE: sem dados, join será parcial")

    # --- Carregar e agregar CFEM ---
    cfem = _load_if_exists(processed / "anm_cfem.parquet")
    if cfem is not None and not cfem.empty:
        cfem = _build_cfem_key(cfem)

        # Converter ValorRecolhido para numérico
        valor_col = next(
            (c for c in cfem.columns if "valor" in c.lower()),
            None,
        )
        if valor_col:
            cfem[valor_col] = pd.to_numeric(
                cfem[valor_col].astype(str).str.replace(",", "."),
                errors="coerce",
            )

        ano_col = "Ano"
        cfem_agg = (
            cfem[cfem["processo_norm"] != ""]
            .groupby("processo_norm")
            .agg(
                cfem_total=(valor_col, "sum") if valor_col else ("processo_norm", "count"),
                cfem_ultimo_ano=(ano_col, "max"),
                cfem_qtd_anos=(ano_col, "nunique"),
            )
            .reset_index()
        )
        logger.info("CFEM: %d processos com arrecadação", len(cfem_agg))
    else:
        cfem_agg = pd.DataFrame(
            columns=["processo_norm", "cfem_total", "cfem_ultimo_ano", "cfem_qtd_anos"]
        )
        logger.warning("CFEM: sem dados, flags de atividade não disponíveis")

    # --- Join 1: SCM ← SIGMINE ---
    result = scm.merge(
        sigmine_dedup,
        on="processo_norm",
        how="left",
        suffixes=("", "_sigmine"),
    )
    match_sigmine = result["AREA_HA"].notna().sum() if "AREA_HA" in result.columns else 0
    logger.info(
        "Join SCM↔SIGMINE: %d/%d matched (%.1f%%)",
        match_sigmine,
        len(result),
        100 * match_sigmine / max(len(result), 1),
    )

    # --- Join 2: Resultado ← CFEM ---
    result = result.merge(
        cfem_agg,
        on="processo_norm",
        how="left",
    )
    match_cfem = result["cfem_total"].notna().sum()
    logger.info(
        "Join SCM↔CFEM: %d/%d matched (%.1f%%)",
        match_cfem,
        len(result),
        100 * match_cfem / max(len(result), 1),
    )

    # --- Flag de atividade ---
    current_year = datetime.now().year
    result["ativo_cfem"] = result["cfem_ultimo_ano"].apply(
        lambda x: bool(pd.notna(x) and int(x) >= current_year - 2)
    )

    # --- Classificação de substâncias ---
    subs_path = reference / "substancias_classificacao.csv"
    if subs_path.exists() and "substancia_principal" in result.columns:
        subs_map = pd.read_csv(subs_path, dtype=str)
        result = result.merge(
            subs_map,
            left_on="substancia_principal",
            right_on="substancia",
            how="left",
            suffixes=("", "_class"),
        )
        # Remover coluna duplicada do merge
        if "substancia_class" in result.columns:
            result = result.drop(columns=["substancia_class"])
        elif "substancia" in result.columns and "substancia_principal" in result.columns:
            # Se ambas existem, a do merge pode ser redundante
            pass

        classified = result["categoria"].notna().sum() if "categoria" in result.columns else 0
        logger.info(
            "Classificação: %d/%d substâncias classificadas (%.1f%%)",
            classified,
            len(result),
            100 * classified / max(len(result), 1),
        )
    else:
        if not subs_path.exists():
            logger.warning(
                "Tabela de classificação não encontrada em %s", subs_path
            )

    # --- Salvar ---
    output = processed / "concessoes_mg.parquet"
    atomic_parquet_write(result, output)

    from licenciaminer.collectors.metadata import save_collection_metadata
    save_collection_metadata(
        data_dir,
        "concessoes_mg",
        len(result),
        notes=f"sigmine_match={match_sigmine}, cfem_match={match_cfem}",
    )

    logger.info(
        "Concessões consolidadas: %d registros salvos em %s", len(result), output
    )
    return output
