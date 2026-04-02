"""Módulo de download e extração de texto de PDFs de decisões da SEMAD/MG.

Cada registro de licenciamento pode ter múltiplos PDFs:
- Folha de decisão: documento formal da decisão
- Parecer técnico: opinião técnica do analista (fonte mais rica)
- Despacho: expediente administrativo
- Outros documentos de suporte

O formato do campo documentos_pdf é:
    "nome1.pdf|url1;nome2.pdf|url2;nome3.pdf|url3"
"""

import logging
import time
from pathlib import Path

import httpx
import pymupdf
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
def _download_pdf(client: httpx.Client, url: str) -> bytes:
    """Baixa um PDF e retorna os bytes."""
    response = client.get(url)
    response.raise_for_status()
    return response.content


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extrai texto de um PDF em memória usando PyMuPDF."""
    text_parts: list[str] = []
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")  # type: ignore[no-untyped-call]
    try:
        for page in doc:  # type: ignore[attr-defined]
            text_parts.append(page.get_text())
    finally:
        doc.close()  # type: ignore[no-untyped-call]
    return "\n".join(text_parts).strip()


def parse_documentos_field(documentos_pdf: str) -> list[dict[str, str]]:
    """Parseia o campo documentos_pdf em lista de {nome, url}.

    Formato: "nome1.pdf|url1;nome2.pdf|url2"
    """
    docs: list[dict[str, str]] = []
    if not documentos_pdf or documentos_pdf.strip() == "":
        return docs

    for entry in documentos_pdf.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("|", 1)
        if len(parts) == 2:
            docs.append({"nome": parts[0].strip(), "url": parts[1].strip()})
        elif entry.startswith("http"):
            docs.append({"nome": "documento.pdf", "url": entry.strip()})

    return docs


def download_and_extract_texts(
    documentos_pdf: str,
    client: httpx.Client | None = None,
) -> list[dict[str, str]]:
    """Baixa todos os PDFs de um registro e extrai o texto de cada um.

    Retorna lista de dicts com {nome, url, texto}.
    """
    docs = parse_documentos_field(documentos_pdf)
    if not docs:
        return []

    own_client = client is None
    active_client = client or httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True)

    results: list[dict[str, str]] = []
    try:
        for doc in docs:
            try:
                pdf_bytes = _download_pdf(active_client, doc["url"])
                texto = extract_text_from_bytes(pdf_bytes)
                results.append({
                    "nome": doc["nome"],
                    "url": doc["url"],
                    "texto": texto,
                })
                logger.debug("PDF extraído: %s (%d chars)", doc["nome"], len(texto))
            except Exception:
                logger.warning("Erro ao processar PDF: %s", doc["url"], exc_info=True)
                results.append({
                    "nome": doc["nome"],
                    "url": doc["url"],
                    "texto": "",
                })
            time.sleep(0.3)
    finally:
        if own_client:
            active_client.close()

    return results


def get_full_context(
    documentos_pdf: str,
    client: httpx.Client | None = None,
) -> str:
    """Concatena texto de todos os PDFs de um registro em um único contexto.

    Retorna string formatada com separadores entre documentos.
    """
    docs = download_and_extract_texts(documentos_pdf, client=client)
    if not docs:
        return ""

    parts: list[str] = []
    for doc in docs:
        if doc["texto"]:
            parts.append(f"=== {doc['nome']} ===\n{doc['texto']}")

    return "\n\n".join(parts)


def enrich_parquet_with_texts(
    data_dir: Path,
    max_records: int | None = None,
    mining_only: bool = True,
) -> Path:
    """Enriquece o parquet MG SEMAD com texto extraído dos PDFs.

    Adiciona coluna 'texto_documentos' com o texto concatenado de todos
    os PDFs de cada registro. Por padrão filtra apenas mineração (A-0x).
    """
    import pandas as pd

    from licenciaminer.config import MG_MINING_CODE_PREFIX
    from licenciaminer.processors.normalize import atomic_parquet_write

    parquet_path = data_dir / "processed" / "mg_semad_licencas.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Parquet não encontrado: {parquet_path}")

    df = pd.read_parquet(parquet_path)

    if "documentos_pdf" not in df.columns:
        raise ValueError(
            "Coluna 'documentos_pdf' não encontrada. "
            "Execute 'licenciaminer collect mg-docs' primeiro."
        )

    from licenciaminer.processors.normalize import has_content

    # Selecionar registros para processar
    has_docs = has_content(df["documentos_pdf"])

    if mining_only and "atividade" in df.columns:
        is_mining = df["atividade"].astype(str).str.startswith(MG_MINING_CODE_PREFIX)
        mask = has_docs & is_mining
    else:
        mask = has_docs

    # Pular registros já processados
    if "texto_documentos" in df.columns:
        already_done = has_content(df["texto_documentos"])
        mask = mask & ~already_done

    indices = df[mask].index.tolist()
    if max_records is not None:
        indices = indices[:max_records]

    logger.info("PDF Extractor: %d registros para processar", len(indices))

    if not indices:
        logger.info("PDF Extractor: nenhum registro para processar")
        return parquet_path

    # Inicializar coluna se não existir
    if "texto_documentos" not in df.columns:
        df["texto_documentos"] = ""

    with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        for i, idx in enumerate(indices):
            docs_field = str(df.at[idx, "documentos_pdf"])
            texto = get_full_context(docs_field, client=client)
            df.at[idx, "texto_documentos"] = texto

            if (i + 1) % 50 == 0:
                logger.info(
                    "PDF Extractor: %d/%d processados",
                    i + 1,
                    len(indices),
                )
                # Salvar progresso parcial a cada 50
                atomic_parquet_write(df, parquet_path)

            time.sleep(0.3)

    atomic_parquet_write(df, parquet_path)
    processed = has_content(df["texto_documentos"]).sum()
    logger.info(
        "PDF Extractor: parquet atualizado — %d registros com texto (%s)",
        processed,
        parquet_path,
    )
    return parquet_path
