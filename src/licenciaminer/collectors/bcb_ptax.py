"""Coletor de cotações USD/BRL via BCB PTAX (API OData do Banco Central)."""

import logging
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import pandas as pd
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from licenciaminer.config import (
    HTTP_TIMEOUT,
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import add_metadata, atomic_parquet_write

logger = logging.getLogger(__name__)

BCB_PTAX_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarPeriodo(dataInicial=@di,dataFinalCotacao=@df)"
)


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _fetch_ptax(date_start: str, date_end: str) -> list[dict]:
    """Busca cotações PTAX no período.

    Args:
        date_start: Formato MM-DD-YYYY (exigido pela API BCB).
        date_end: Formato MM-DD-YYYY.
    """
    params = {
        "@di": f"'{date_start}'",
        "@df": f"'{date_end}'",
        "$format": "json",
    }
    logger.info("BCB PTAX: buscando %s a %s", date_start, date_end)
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        resp = client.get(BCB_PTAX_URL, params=params)
        resp.raise_for_status()
        return resp.json().get("value", [])


def collect_bcb_ptax(
    data_dir: Path,
    months: int = 24,
) -> Path:
    """Coleta cotações USD/BRL do BCB e salva como parquet.

    Args:
        data_dir: Diretório base de dados.
        months: Quantos meses de histórico (padrão: 24).

    Returns:
        Caminho do arquivo parquet gerado.
    """
    end = datetime.now()
    start = end - timedelta(days=months * 30)

    date_start = start.strftime("%m-%d-%Y")
    date_end = end.strftime("%m-%d-%Y")

    records = _fetch_ptax(date_start, date_end)

    output = data_dir / "processed" / "bcb_cotacoes.parquet"

    if not records:
        logger.warning("BCB PTAX: nenhum registro retornado")
        df = pd.DataFrame(columns=["data", "cotacao_compra", "cotacao_venda"])
        atomic_parquet_write(df, output)
        return output

    df = pd.DataFrame(records)

    # Normalizar colunas
    df = df.rename(columns={
        "cotacaoCompra": "cotacao_compra",
        "cotacaoVenda": "cotacao_venda",
        "dataHoraCotacao": "data_hora_cotacao",
    })

    # Extrair data (formato: "2024-01-15 13:09:30.123")
    df["data"] = pd.to_datetime(
        df["data_hora_cotacao"]
    ).dt.date.astype(str)

    # Manter apenas cotação de fechamento (última do dia)
    df = df.sort_values("data_hora_cotacao").drop_duplicates(
        subset=["data"], keep="last"
    )

    df = df[["data", "cotacao_compra", "cotacao_venda"]].reset_index(drop=True)
    df["cotacao_compra"] = df["cotacao_compra"].astype(float)
    df["cotacao_venda"] = df["cotacao_venda"].astype(float)

    df = add_metadata(df, "bcb_ptax")
    atomic_parquet_write(df, output)

    logger.info("BCB PTAX: %d cotações salvas em %s", len(df), output)
    return output
