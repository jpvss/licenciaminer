"""Coletor de processos minerários da ANM via SIGMINE (ArcGIS REST)."""

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
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _query_arcgis(
    client: httpx.Client, where: str, offset: int = 0
) -> dict[str, object]:
    """Executa uma consulta ao ArcGIS FeatureServer da ANM."""
    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": "false",
        "f": "json",
        "resultOffset": str(offset),
        "resultRecordCount": str(ANM_MAX_RECORDS),
        "orderByFields": "FID ASC",
    }
    response = client.get(ANM_FEATURESERVER_URL, params=params)
    response.raise_for_status()
    data: dict[str, object] = response.json()
    return data


def _paginated_query(client: httpx.Client, where: str) -> list[dict[str, object]] | None:
    """Consulta com paginação via resultOffset.

    Retorna lista de atributos ou None se paginação não for suportada
    (quando o servidor retorna exatamente MAX_RECORDS sem exceededTransferLimit).
    """
    all_features: list[dict[str, object]] = []
    offset = 0

    while True:
        data = _query_arcgis(client, where=where, offset=offset)
        features = data.get("features", [])

        if isinstance(features, list):
            attrs = [f["attributes"] for f in features if isinstance(f, dict)]
            all_features.extend(attrs)
        else:
            break

        exceeded = data.get("exceededTransferLimit", False)

        if exceeded:
            # Servidor suporta paginação — continuar
            offset += len(attrs)
            time.sleep(1.0)
        elif len(attrs) == ANM_MAX_RECORDS and offset == 0:
            # Primeira página retornou exatamente MAX_RECORDS sem flag.
            # Pode ser que paginação não é suportada — tentar próxima página.
            offset += len(attrs)
            time.sleep(1.0)
            next_data = _query_arcgis(client, where=where, offset=offset)
            next_features = next_data.get("features", [])
            if isinstance(next_features, list) and len(next_features) > 0:
                # Paginação funciona
                next_attrs = [f["attributes"] for f in next_features if isinstance(f, dict)]
                all_features.extend(next_attrs)
                if next_data.get("exceededTransferLimit", False):
                    offset += len(next_attrs)
                    time.sleep(1.0)
                    continue
            else:
                # Paginação não funciona — retornar None para acionar fallback
                return None
            break
        else:
            break

    return all_features


def _query_by_uf(client: httpx.Client, uf: str) -> list[dict[str, object]]:
    """Coleta processos de uma UF, com fallback para subdivisão por FASE."""
    logger.info("ANM: coletando UF=%s", uf)

    result = _paginated_query(client, where=f"UF='{uf}'")
    if result is not None:
        logger.info("ANM: UF=%s — %d registros (paginação)", uf, len(result))
        return result

    # Fallback: subdividir por FASE
    logger.info("ANM: UF=%s — paginação não suportada, subdividindo por FASE", uf)
    all_records: list[dict[str, object]] = []
    for fase in ANM_FASES:
        where = f"UF='{uf}' AND FASE='{fase}'"
        records = _paginated_query(client, where=where)
        if records is not None:
            all_records.extend(records)
            logger.info("ANM: UF=%s FASE=%s — %d registros", uf, fase, len(records))
        else:
            logger.warning(
                "ANM: UF=%s FASE=%s excedeu %d registros — dados podem estar truncados",
                uf,
                fase,
                ANM_MAX_RECORDS,
            )
        time.sleep(1.0)

    return all_records


def collect_anm(data_dir: Path, ufs: list[str] | None = None) -> Path:
    """Coleta processos minerários da ANM via SIGMINE.

    Itera por UF com paginação. Se paginação não for suportada,
    subdivide por FASE para contornar o limite de 5000 registros.
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

    # Converter datas de epoch ms
    date_cols = [c for c in df.columns if "DATA" in c.upper() or "DT_" in c.upper()]
    for col in date_cols:
        df[col] = parse_date_epoch_ms(df[col])

    df = add_metadata(df, source="anm_sigmine")

    output_path = data_dir / "processed" / "anm_processos.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info("ANM: dados salvos em %s (%d registros)", output_path, len(df))
    return output_path
