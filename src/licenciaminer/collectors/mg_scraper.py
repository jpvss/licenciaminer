"""Scraper para dados de licenciamento ambiental da SEMAD/MG.

Coleta dados da tabela paginada em:
https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca

O portal usa Yii Framework GridView com paginação simples via ?page=N&per-page=50.
O download de Excel está fora do ar, mas a tabela HTML está acessível.
"""

import logging
import re
import time
from pathlib import Path

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from licenciaminer.config import (
    HTTP_TIMEOUT,
    MG_MINING_CODE_PREFIX,
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import (
    add_metadata,
    atomic_parquet_write,
    normalize_cnpj,
    normalize_columns,
    parse_date_br,
)

logger = logging.getLogger(__name__)

MG_BASE_URL = (
    "https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca"
)
PER_PAGE = 50

# Colunas na ordem em que aparecem na tabela HTML
TABLE_COLUMNS = [
    "Regional",
    "Município",
    "Empreendimento",
    "CNPJ/CPF",
    "Processo Adm",
    "Nº de Protocolo",
    "Modalidade",
    "Classe",
    "Atividade",
    "Ano",
    "Mês",
    "Data de Publicação",
    "Decisão",
]


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _fetch_page(client: httpx.Client, page: int) -> str:
    """Baixa uma página da tabela de licenciamento."""
    response = client.get(
        MG_BASE_URL,
        params={"page": str(page), "per-page": str(PER_PAGE)},
    )
    response.raise_for_status()
    return response.text


def _extract_total_items(html: str) -> int:
    """Extrai o número total de itens da paginação."""
    # Padrão: "de <b>42,758</b> itens" (com tags HTML e separador de milhar)
    match = re.search(r"de\s*(?:<[^>]+>)?\s*([\d.,]+)\s*(?:<[^>]+>)?\s*itens", html)
    if match:
        total_str = match.group(1).replace(".", "").replace(",", "")
        return int(total_str)
    return 0


def _parse_table_rows(html: str) -> list[dict[str, str]]:
    """Extrai linhas de dados da tabela HTML.

    Usa regex para extrair conteúdo de <td> dentro de <tbody>.
    """
    rows: list[dict[str, str]] = []

    # Encontrar o tbody
    tbody_match = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    if not tbody_match:
        return rows

    tbody = tbody_match.group(1)

    # Encontrar cada <tr>
    tr_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
    td_pattern = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)

    for tr_match in tr_pattern.finditer(tbody):
        tr_content = tr_match.group(1)

        # Pular linhas de filtro (contêm <input> ou <select>)
        if "<input" in tr_content or "<select" in tr_content:
            continue

        # Extrair cada <td>
        cells = []
        for td_match in td_pattern.finditer(tr_content):
            cell_html = td_match.group(1).strip()
            # Remover tags HTML e limpar
            cell_text = re.sub(r"<[^>]+>", "", cell_html).strip()
            # Normalizar espaços
            cell_text = re.sub(r"\s+", " ", cell_text)
            cells.append(cell_text)

        # A última coluna pode ter botão "Visualizar" — ignorar
        # Mapear células para colunas (ignorando extras no final)
        if len(cells) >= len(TABLE_COLUMNS):
            row = {
                col: cells[i] for i, col in enumerate(TABLE_COLUMNS)
            }
            rows.append(row)

    return rows


def scrape_mg_semad(
    data_dir: Path,
    max_pages: int | None = None,
    mining_only: bool = True,
) -> Path:
    """Scrapa dados de licenciamento da SEMAD/MG via tabela HTML paginada.

    Coleta todas as páginas da tabela, opcionalmente filtrando apenas
    atividades de mineração (códigos A-0x).
    """
    import pandas as pd

    all_rows: list[dict[str, str]] = []

    with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        # Primeira página para descobrir total
        logger.info("MG SEMAD Scraper: baixando página 1...")
        html = _fetch_page(client, page=1)
        total_items = _extract_total_items(html)
        total_pages = (total_items + PER_PAGE - 1) // PER_PAGE

        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        logger.info(
            "MG SEMAD Scraper: %d itens, %d páginas para coletar",
            total_items,
            total_pages,
        )

        # Parsear primeira página
        rows = _parse_table_rows(html)
        all_rows.extend(rows)
        logger.info("MG SEMAD Scraper: página 1 — %d registros", len(rows))

        # Coletar demais páginas
        for page in range(2, total_pages + 1):
            time.sleep(1.0)  # Rate limiting
            try:
                html = _fetch_page(client, page=page)
                rows = _parse_table_rows(html)
                all_rows.extend(rows)

                if page % 50 == 0 or page == total_pages:
                    logger.info(
                        "MG SEMAD Scraper: página %d/%d — %d registros acumulados",
                        page,
                        total_pages,
                        len(all_rows),
                    )
            except Exception:
                logger.exception(
                    "MG SEMAD Scraper: erro na página %d — continuando",
                    page,
                )
                continue

    logger.info("MG SEMAD Scraper: %d registros brutos coletados", len(all_rows))

    df = pd.DataFrame(all_rows)

    if df.empty:
        logger.warning("MG SEMAD Scraper: nenhum registro coletado")
        df = add_metadata(df, source="mg_semad_scraper")
        output_path = data_dir / "processed" / "mg_semad_licencas.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_parquet_write(df, output_path)
        return output_path

    # Normalizar decisão
    if "Decisão" in df.columns:
        df["Decisão"] = df["Decisão"].str.strip().str.lower().map(
            lambda x: (
                "deferido"
                if isinstance(x, str) and "deferid" in x and "indeferid" not in x
                else (
                    "indeferido"
                    if isinstance(x, str) and "indeferid" in x
                    else (
                        "arquivamento"
                        if isinstance(x, str) and "arquiv" in x
                        else "outro"
                    )
                )
            )
        )

    # Normalizar CNPJ/CPF
    if "CNPJ/CPF" in df.columns:
        df["CNPJ/CPF"] = df["CNPJ/CPF"].apply(
            lambda x: normalize_cnpj(str(x)) if pd.notna(x) and x else None
        )

    # Normalizar colunas
    df = normalize_columns(df)

    # Parsear datas
    if "data_de_publicacao" in df.columns:
        df["data_de_publicacao"] = parse_date_br(df["data_de_publicacao"])

    # Extrair número da classe ("classe 2" → 2)
    if "classe" in df.columns:
        df["classe"] = (
            df["classe"]
            .astype(str)
            .str.extract(r"(\d+)", expand=False)
        )
        df["classe"] = pd.to_numeric(df["classe"], errors="coerce")

    # Filtrar mineração se solicitado
    if mining_only and "atividade" in df.columns:
        total_before = len(df)
        mask = df["atividade"].astype(str).str.startswith(MG_MINING_CODE_PREFIX)
        df = df[mask].copy()
        logger.info(
            "MG SEMAD Scraper: filtro mineração — %d → %d registros",
            total_before,
            len(df),
        )

    df = add_metadata(df, source="mg_semad_scraper")

    output_path = data_dir / "processed" / "mg_semad_licencas.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info(
        "MG SEMAD Scraper: dados salvos em %s (%d registros)",
        output_path,
        len(df),
    )
    return output_path
