"""Scraper de reuniões da CMI (Câmara de Atividades Minerárias) do COPAM.

Coleta dados do portal de reuniões do COPAM:
https://sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam/index-externo

Cada reunião da CMI tem:
- Metadados: data, título, sede
- Documentos da pauta: PDFs com parecer técnico por item/empresa
- Decisão: PDF com resultado da votação
- Relatos de vista, pareceres alterados, ata aprovada
"""

import logging
import re
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

from licenciaminer.collectors.metadata import save_collection_metadata
from licenciaminer.config import (
    HTTP_TIMEOUT,
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import add_metadata, atomic_parquet_write

logger = logging.getLogger(__name__)

COPAM_BASE_URL = (
    "https://sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam"
)
COPAM_LIST_URL = f"{COPAM_BASE_URL}/index-externo"
COPAM_DETAIL_URL = f"{COPAM_BASE_URL}/view-externo"
COPAM_UPLOADS_BASE = (
    "https://sistemas.meioambiente.mg.gov.br/reunioes/uploads"
)

PER_PAGE = 50


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _fetch_page(client: httpx.Client, url: str, params: dict[str, str]) -> str:
    """Busca uma página HTML."""
    response = client.get(url, params=params)
    response.raise_for_status()
    return response.text


def _extract_total(html: str) -> int:
    """Extrai total de itens da paginação."""
    match = re.search(r"de\s*(?:<[^>]+>)?\s*([\d.,]+)\s*(?:<[^>]+>)?\s*itens", html)
    if match:
        return int(match.group(1).replace(".", "").replace(",", ""))
    return 0


def _parse_meeting_list(html: str) -> list[dict[str, str]]:
    """Extrai reuniões da tabela de listagem."""
    meetings: list[dict[str, str]] = []
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    if not tbody:
        return meetings

    tr_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
    td_pattern = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)

    for tr_match in tr_pattern.finditer(tbody.group(1)):
        tr = tr_match.group(1)
        if "<input" in tr or "<select" in tr:
            continue

        cells = []
        for td_match in td_pattern.finditer(tr):
            text = re.sub(r"<[^>]+>", "", td_match.group(1)).strip()
            text = re.sub(r"\s+", " ", text)
            cells.append(text)

        detail_match = re.search(r"view-externo\?id=(\d+)", tr)
        if len(cells) >= 4 and detail_match:
            meetings.append({
                "meeting_id": detail_match.group(1),
                "municipio": cells[0] if cells[0] != "(não definido)" else "",
                "data": cells[1],
                "titulo": cells[2],
                "sede": cells[3],
                "unidade_colegiada": cells[4] if len(cells) > 4 else "",
            })

    return meetings


def _parse_detail_page(html: str, meeting_id: str) -> dict[str, object]:
    """Extrai documentos e metadados de uma página de detalhe de reunião."""
    documents: list[dict[str, str]] = []

    # Extrair todos os links para PDFs em /reunioes/uploads/
    pdf_links = re.findall(
        r'href="(/reunioes/uploads/[^"]+\.pdf)"[^>]*>\s*([^<]+)', html
    )
    for path, name in pdf_links:
        url = f"https://sistemas.meioambiente.mg.gov.br{path}"
        documents.append({
            "nome": name.strip(),
            "url": url,
        })

    # Tentar extrair seções da página
    sections: dict[str, list[str]] = {}
    section_names = [
        "Convocação", "Pauta", "inerente", "Relato",
        "alterado", "Decisão", "Ata aprovada",
        "Apresentaç", "Lista de presença", "Material complementar",
    ]
    for section_name in section_names:
        section_pdfs = [
            d for d in documents
            if section_name.lower() in d["nome"].lower()
            or section_name.lower() in str(d).lower()
        ]
        if section_pdfs:
            sections[section_name] = [d["url"] for d in section_pdfs]

    return {
        "meeting_id": meeting_id,
        "total_documents": len(documents),
        "documents": documents,
        "documents_str": ";".join(
            f"{d['nome']}|{d['url']}" for d in documents
        ),
    }


def scrape_copam_cmi(
    data_dir: Path,
    max_meetings: int | None = None,
) -> Path:
    """Scrapa reuniões da CMI (Câmara de Atividades Minerárias) do COPAM.

    1. Lista reuniões filtrando por título 'CMI'
    2. Para cada reunião, busca página de detalhe
    3. Extrai links de PDFs (Decisão, Pauta, Pareceres)
    """
    output_path = data_dir / "processed" / "copam_cmi_reunioes.parquet"

    # Carregar existentes para modo incremental
    existing_ids: set[str] = set()
    if output_path.exists():
        df_existing = pd.read_parquet(output_path)
        if "meeting_id" in df_existing.columns:
            existing_ids = set(df_existing["meeting_id"].dropna().astype(str))
            logger.info("COPAM CMI: %d reuniões existentes", len(existing_ids))

    all_meetings: list[dict[str, str]] = []

    with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        # Primeira página para descobrir total
        logger.info("COPAM CMI: buscando lista de reuniões...")
        html = _fetch_page(client, COPAM_LIST_URL, {
            "ReuniaoCopamSearch[titulo]": "CMI",
            "page": "1",
            "per-page": str(PER_PAGE),
        })
        total = _extract_total(html)
        total_pages = (total + PER_PAGE - 1) // PER_PAGE

        if max_meetings is not None:
            total_pages = min(total_pages, (max_meetings + PER_PAGE - 1) // PER_PAGE)

        logger.info("COPAM CMI: %d reuniões, %d páginas", total, total_pages)

        # Parsear primeira página
        meetings = _parse_meeting_list(html)
        all_meetings.extend(meetings)

        # Demais páginas
        for page in range(2, total_pages + 1):
            time.sleep(1.0)
            html = _fetch_page(client, COPAM_LIST_URL, {
                "ReuniaoCopamSearch[titulo]": "CMI",
                "page": str(page),
                "per-page": str(PER_PAGE),
            })
            meetings = _parse_meeting_list(html)
            all_meetings.extend(meetings)

    logger.info("COPAM CMI: %d reuniões encontradas", len(all_meetings))

    if max_meetings is not None:
        all_meetings = all_meetings[:max_meetings]

    # Filtrar apenas novas (incremental)
    new_meetings = [
        m for m in all_meetings
        if m["meeting_id"] not in existing_ids
    ]
    logger.info(
        "COPAM CMI: %d novas, %d já coletadas",
        len(new_meetings),
        len(all_meetings) - len(new_meetings),
    )

    # Buscar detalhes de cada reunião nova
    details: list[dict[str, object]] = []
    with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        for i, meeting in enumerate(new_meetings):
            mid = meeting["meeting_id"]
            try:
                html = _fetch_page(
                    client, COPAM_DETAIL_URL, {"id": mid}
                )
                detail = _parse_detail_page(html, mid)

                row: dict[str, object] = {**meeting, **detail}
                details.append(row)

                logger.info(
                    "COPAM CMI: reunião %s — %d documentos",
                    meeting["titulo"][:40],
                    detail["total_documents"],
                )
            except Exception:
                logger.exception(
                    "COPAM CMI: erro na reunião id=%s", mid
                )

            if (i + 1) % 10 == 0:
                logger.info(
                    "COPAM CMI: %d/%d reuniões processadas",
                    i + 1,
                    len(new_meetings),
                )
            time.sleep(0.5)

    # Construir DataFrame
    df_new = pd.DataFrame(details)

    if not df_new.empty:
        # Remover coluna documents (lista de dicts) — manter documents_str
        if "documents" in df_new.columns:
            df_new = df_new.drop(columns=["documents"])

        df_new["_source_url"] = df_new["meeting_id"].apply(
            lambda x: f"{COPAM_DETAIL_URL}?id={x}"
        )
        df_new = add_metadata(df_new, source="copam_cmi")

    # Juntar com existentes
    if existing_ids and not df_new.empty:
        df_existing = pd.read_parquet(output_path)
        df = pd.concat([df_existing, df_new], ignore_index=True)
        df = df.drop_duplicates(subset="meeting_id", keep="first")
    elif existing_ids:
        df = pd.read_parquet(output_path)
    else:
        df = df_new

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not df.empty:
        atomic_parquet_write(df, output_path)
    else:
        df = pd.DataFrame()
        df = add_metadata(df, source="copam_cmi")
        atomic_parquet_write(df, output_path)

    save_collection_metadata(
        data_dir, "copam_cmi", len(df),
        f"{len(new_meetings)} novas reuniões",
    )
    logger.info(
        "COPAM CMI: salvo em %s (%d reuniões, %d novas)",
        output_path,
        len(df),
        len(new_meetings),
    )
    return output_path
