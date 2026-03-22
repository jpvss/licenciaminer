"""Coletor de processos minerários da ANM via SIGMINE (ArcGIS REST).

IMPORTANTE: O servidor ArcGIS da ANM IGNORA o parâmetro resultOffset.
Paginação não funciona — a mesma página é retornada independente do offset.
Estratégia: iterar por UF → FASE → ANO para manter cada query abaixo de 5000.
"""

import logging
import time
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
    ANM_FASES,
    ANM_FEATURESERVER_URL,
    ANM_MAX_RECORDS,
    ANM_PRIORITY_UFS,
    HTTP_TIMEOUT,
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import (
    add_metadata,
    atomic_parquet_write,
    parse_date_epoch_ms,
)

logger = logging.getLogger(__name__)



@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _query_arcgis(client: httpx.Client, where: str) -> dict[str, object]:
    """Executa uma consulta ao ArcGIS FeatureServer da ANM."""
    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": "false",
        "f": "json",
        "resultRecordCount": str(ANM_MAX_RECORDS),
    }
    response = client.get(ANM_FEATURESERVER_URL, params=params)
    response.raise_for_status()
    data: dict[str, object] = response.json()
    return data


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _query_count(client: httpx.Client, where: str) -> int:
    """Consulta contagem de registros para um filtro."""
    params = {
        "where": where,
        "returnCountOnly": "true",
        "f": "json",
    }
    response = client.get(ANM_FEATURESERVER_URL, params=params)
    response.raise_for_status()
    data = response.json()
    count: int = data.get("count", 0)
    return count


def _extract_features(data: dict[str, object]) -> list[dict[str, object]]:
    """Extrai atributos das features do response ArcGIS."""
    features = data.get("features", [])
    if isinstance(features, list):
        return [f["attributes"] for f in features if isinstance(f, dict)]
    return []



def _query_simple(
    client: httpx.Client, where: str, label: str
) -> list[dict[str, object]]:
    """Consulta simples (sem paginação). Loga warning se atingir limite."""
    data = _query_arcgis(client, where=where)
    records = _extract_features(data)
    if len(records) == ANM_MAX_RECORDS:
        logger.warning(
            "ANM: %s retornou exatamente %d registros — possível truncamento",
            label,
            ANM_MAX_RECORDS,
        )
    else:
        logger.info("ANM: %s — %d registros", label, len(records))
    return records


def _query_by_fase(
    client: httpx.Client, uf: str, fase: str
) -> list[dict[str, object]]:
    """Coleta por UF+FASE. Se exceder 5000, subdivide por ANO."""
    where = f"UF='{uf}' AND FASE='{fase}'"
    label = f"UF={uf} FASE={fase}"

    # Primeiro, verificar contagem
    count = _query_count(client, where)
    time.sleep(0.5)

    if count <= ANM_MAX_RECORDS:
        records = _query_simple(client, where, label)
        time.sleep(0.5)
        return records

    # Contagem excede limite — subdividir por ANO
    logger.info(
        "ANM: %s tem %d registros (> %d), subdividindo por ANO",
        label,
        count,
        ANM_MAX_RECORDS,
    )
    all_records: list[dict[str, object]] = []
    collected = 0

    for ano in range(1930, 2027):
        where_ano = f"UF='{uf}' AND FASE='{fase}' AND ANO={ano}"
        label_ano = f"UF={uf} FASE={fase} ANO={ano}"

        # Verificar contagem antes de baixar dados
        ano_count = _query_count(client, where_ano)
        time.sleep(0.3)

        if ano_count == 0:
            continue

        records = _query_simple(client, where_ano, label_ano)
        all_records.extend(records)
        collected += len(records)
        time.sleep(0.3)

        # Se já coletamos tudo, parar
        if collected >= count:
            break

    return all_records


def _query_by_uf(client: httpx.Client, uf: str) -> list[dict[str, object]]:
    """Coleta todos os processos de uma UF, iterando por FASE."""
    logger.info("ANM: coletando UF=%s", uf)

    # Verificar contagem total
    total = _query_count(client, f"UF='{uf}'")
    logger.info("ANM: UF=%s — %d registros totais", uf, total)
    time.sleep(0.5)

    if total <= ANM_MAX_RECORDS:
        # UF inteira cabe em uma query
        return _query_simple(client, f"UF='{uf}'", f"UF={uf}")

    # Iterar por FASE
    all_records: list[dict[str, object]] = []
    for fase in ANM_FASES:
        records = _query_by_fase(client, uf, fase)
        all_records.extend(records)

    # Verificar se capturamos tudo
    if len(all_records) < total:
        logger.warning(
            "ANM: UF=%s — coletamos %d de %d registros. "
            "Podem existir FASE values não mapeadas.",
            uf,
            len(all_records),
            total,
        )

    return all_records


def collect_anm(data_dir: Path, ufs: list[str] | None = None) -> Path:
    """Coleta processos minerários da ANM via SIGMINE.

    O servidor ArcGIS da ANM NÃO suporta paginação (resultOffset é ignorado).
    Estratégia: iterar por UF → FASE → ANO para manter queries abaixo de 5000.
    """
    ufs = ufs or ANM_PRIORITY_UFS
    all_records: list[dict[str, object]] = []

    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        for uf in ufs:
            records = _query_by_uf(client, uf)
            all_records.extend(records)
            time.sleep(1.0)

    logger.info("ANM: %d registros totais coletados", len(all_records))
    df = pd.DataFrame(all_records)

    if df.empty:
        logger.warning("ANM: nenhum registro coletado")
        df = pd.DataFrame()
    else:
        # Converter datas de epoch ms
        date_cols = [
            c for c in df.columns if "DATA" in c.upper() or "DT_" in c.upper()
        ]
        for col in date_cols:
            df[col] = parse_date_epoch_ms(df[col])

    df = add_metadata(df, source="anm_sigmine")

    output_path = data_dir / "processed" / "anm_processos.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info("ANM: dados salvos em %s (%d registros)", output_path, len(df))
    return output_path
