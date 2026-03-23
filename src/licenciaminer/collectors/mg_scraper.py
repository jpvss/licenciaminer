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

        # Mapear células para colunas (ignorando extras no final)
        if len(cells) >= len(TABLE_COLUMNS):
            row = {
                col: cells[i] for i, col in enumerate(TABLE_COLUMNS)
            }

            # Extrair ID do link "Visualizar" (view-externo?id=NNNNN)
            id_match = re.search(
                r'view-externo\?id=(\d+)', tr_content
            )
            if id_match:
                row["detail_id"] = id_match.group(1)

            rows.append(row)

    return rows


MG_DETAIL_URL = (
    "https://sistemas.meioambiente.mg.gov.br/licenciamento/site/view-externo"
)
MG_UPLOADS_BASE = (
    "https://sistemas.meioambiente.mg.gov.br/licenciamento/uploads"
)


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(
        (httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _fetch_detail(client: httpx.Client, detail_id: str) -> dict[str, str]:
    """Busca página de detalhe e extrai links de documentos PDF."""
    response = client.get(MG_DETAIL_URL, params={"id": detail_id})
    response.raise_for_status()
    html = response.text

    # Extrair links para PDFs em /licenciamento/uploads/
    pdf_links = re.findall(
        r'href="(/licenciamento/uploads/[^"]+\.pdf)"', html
    )

    # Extrair nomes dos documentos (texto antes do link)
    doc_names = re.findall(
        r'<a[^>]*href="/licenciamento/uploads/[^"]+\.pdf"[^>]*>\s*([^<]+)',
        html,
    )

    # Construir URLs completas e juntar com nomes
    docs: list[str] = []
    for i, pdf_path in enumerate(pdf_links):
        url = f"https://sistemas.meioambiente.mg.gov.br{pdf_path}"
        name = doc_names[i].strip() if i < len(doc_names) else "documento.pdf"
        docs.append(f"{name}|{url}")

    # Extrair modalidade (presente no detalhe mas não na lista)
    modalidade_match = re.search(
        r"Modalidade.*?<td[^>]*>(.*?)</td>", html, re.DOTALL
    )
    modalidade = ""
    if modalidade_match:
        modalidade = re.sub(r"<[^>]+>", "", modalidade_match.group(1)).strip()

    return {
        "documentos_pdf": ";".join(docs),
        "modalidade_detalhe": modalidade,
    }


def enrich_with_details(
    data_dir: Path,
    max_records: int | None = None,
    mining_only: bool = False,
) -> Path:
    """Enriquece parquet existente com links de documentos das páginas de detalhe.

    Lê o parquet salvo pelo scraper, busca a página de detalhe para cada
    registro que tem detail_id, e adiciona colunas com links de PDFs.
    """
    parquet_path = data_dir / "processed" / "mg_semad_licencas.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Parquet não encontrado: {parquet_path}. "
            "Execute 'licenciaminer collect mg --scrape' primeiro."
        )

    df = pd.read_parquet(parquet_path)

    if "detail_id" not in df.columns:
        logger.warning("Coluna detail_id não encontrada — re-execute o scraper")
        return parquet_path

    # Filtrar apenas mineração se solicitado
    if mining_only and "atividade" in df.columns:
        mask = df["atividade"].astype(str).str.startswith(MG_MINING_CODE_PREFIX)
        candidate_ids = df.loc[mask, "detail_id"].dropna().unique()
        logger.info("MG SEMAD Detalhe: filtro mineração — %d registros", len(candidate_ids))
    else:
        candidate_ids = df["detail_id"].dropna().unique()

    # Pular registros que já têm documentos_pdf
    already_enriched: set[str] = set()
    if "documentos_pdf" in df.columns:
        from licenciaminer.processors.normalize import has_content

        has_docs = has_content(df["documentos_pdf"])
        already_enriched = set(
            df.loc[has_docs, "detail_id"].dropna().astype(str)
        )

    ids_to_fetch = [
        did for did in candidate_ids
        if str(did) not in already_enriched
    ]
    logger.info(
        "MG SEMAD Detalhe: %d já enriquecidos, %d novos para buscar",
        len(already_enriched),
        len(ids_to_fetch),
    )

    if max_records is not None:
        ids_to_fetch = ids_to_fetch[:max_records]

    logger.info(
        "MG SEMAD Detalhe: buscando documentos de %d registros",
        len(ids_to_fetch),
    )

    if "documentos_pdf" not in df.columns:
        df["documentos_pdf"] = ""

    with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        for i, detail_id in enumerate(ids_to_fetch):
            try:
                detail = _fetch_detail(client, str(detail_id))
                # Atualizar imediatamente no DataFrame
                mask = df["detail_id"].astype(str) == str(detail_id)
                df.loc[mask, "documentos_pdf"] = detail.get(
                    "documentos_pdf", ""
                )
            except Exception:
                logger.warning(
                    "MG SEMAD Detalhe: erro no id=%s — continuando",
                    detail_id,
                )

            if (i + 1) % 200 == 0:
                # Salvar progresso a cada 200
                atomic_parquet_write(df, parquet_path)
                logger.info(
                    "MG SEMAD Detalhe: %d/%d processados (salvo)",
                    i + 1,
                    len(ids_to_fetch),
                )
            time.sleep(0.3)

    atomic_parquet_write(df, parquet_path)
    logger.info(
        "MG SEMAD Detalhe: parquet atualizado com documentos (%d registros)",
        len(df),
    )
    return parquet_path


def _normalize_new_rows(df: pd.DataFrame, mining_only: bool) -> pd.DataFrame:
    """Normaliza um DataFrame de linhas recém-scrapadas."""

    if df.empty:
        return df

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
    return df


def scrape_mg_semad(
    data_dir: Path,
    max_pages: int | None = None,
    mining_only: bool = True,
    full_refresh: bool = False,
) -> Path:
    """Scrapa dados de licenciamento da SEMAD/MG via tabela HTML paginada.

    Modo incremental (padrão): scrapa páginas mais recentes até encontrar
    um detail_id já existente no parquet. Novos registros são concatenados.

    Modo full (--full-refresh): scrapa tudo do zero, substituindo o parquet.
    """
    from licenciaminer.collectors.metadata import save_collection_metadata

    output_path = data_dir / "processed" / "mg_semad_licencas.parquet"

    # Carregar IDs existentes para modo incremental
    existing_ids: set[str] = set()
    df_existing: pd.DataFrame | None = None
    if not full_refresh and output_path.exists():
        df_existing = pd.read_parquet(output_path)
        if "detail_id" in df_existing.columns:
            existing_ids = set(df_existing["detail_id"].dropna().astype(str))
            logger.info(
                "MG SEMAD Scraper: modo incremental — %d registros existentes",
                len(existing_ids),
            )

    all_rows: list[dict[str, str]] = []
    hit_existing = False

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

        # Em modo incremental, verificar se já temos estes registros
        if existing_ids:
            new_rows = [
                r for r in rows
                if r.get("detail_id", "") not in existing_ids
            ]
            if len(new_rows) < len(rows):
                hit_existing = True
            all_rows.extend(new_rows)
            logger.info(
                "MG SEMAD Scraper: página 1 — %d novos de %d",
                len(new_rows),
                len(rows),
            )
        else:
            all_rows.extend(rows)
            logger.info("MG SEMAD Scraper: página 1 — %d registros", len(rows))

        # Coletar demais páginas (parar se modo incremental e todos conhecidos)
        for page in range(2, total_pages + 1):
            if hit_existing and existing_ids and not full_refresh:
                # Página anterior já tinha IDs conhecidos — parar
                logger.info(
                    "MG SEMAD Scraper: encontrou registros existentes na "
                    "página %d — parando coleta incremental (%d novos)",
                    page - 1,
                    len(all_rows),
                )
                break

            time.sleep(1.0)
            try:
                html = _fetch_page(client, page=page)
                rows = _parse_table_rows(html)

                if existing_ids:
                    new_rows = [
                        r for r in rows
                        if r.get("detail_id", "") not in existing_ids
                    ]
                    if len(new_rows) < len(rows):
                        hit_existing = True
                    all_rows.extend(new_rows)
                else:
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

    logger.info("MG SEMAD Scraper: %d registros novos coletados", len(all_rows))

    if not all_rows:
        logger.info("MG SEMAD Scraper: nenhum registro novo — dados atualizados")
        if df_existing is not None:
            save_collection_metadata(
                data_dir, "mg_semad", len(df_existing), "incremental — sem novos"
            )
            return output_path
        # Parquet vazio
        df = pd.DataFrame()
        df = add_metadata(df, source="mg_semad_scraper")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_parquet_write(df, output_path)
        return output_path

    df_new = pd.DataFrame(all_rows)
    df_new = _normalize_new_rows(df_new, mining_only=mining_only)

    # Concatenar com existentes em modo incremental
    if df_existing is not None and not full_refresh and not df_new.empty:
        # Existing rows go FIRST — keep="first" preserves enrichment columns
        df = pd.concat([df_existing, df_new], ignore_index=True)
        if "detail_id" in df.columns:
            df = df.drop_duplicates(subset="detail_id", keep="first")

        # Garantir que novos registros sem detail_id duplicado sejam incluídos
        logger.info(
            "MG SEMAD Scraper: %d novos + %d existentes = %d total",
            len(df_new),
            len(df_existing),
            len(df),
        )
    else:
        df = df_new

    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    save_collection_metadata(
        data_dir,
        "mg_semad",
        len(df),
        f"{'full' if full_refresh else 'incremental'} — {len(all_rows)} novos",
    )
    logger.info(
        "MG SEMAD Scraper: dados salvos em %s (%d registros)",
        output_path,
        len(df),
    )
    return output_path
