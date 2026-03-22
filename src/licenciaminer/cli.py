"""Interface de linha de comando do LicenciaMiner."""

import logging
from pathlib import Path

import click


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Ativar logs detalhados.")
@click.option(
    "--data-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Diretório de dados.",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, data_dir: Path | None) -> None:
    """LicenciaMiner — Base analítica de licenciamento ambiental minerário."""
    ctx.ensure_object(dict)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    if data_dir is not None:
        ctx.obj["data_dir"] = data_dir
    else:
        from licenciaminer.config import DATA_DIR

        ctx.obj["data_dir"] = DATA_DIR


@cli.group()
def collect() -> None:
    """Coletar dados das fontes (IBAMA, ANM, MG SEMAD)."""


@collect.command()
@click.pass_context
def ibama(ctx: click.Context) -> None:
    """Coletar licenças do IBAMA SISLIC."""
    from licenciaminer.collectors.ibama import collect_ibama

    output_dir: Path = ctx.obj["data_dir"]
    path = collect_ibama(output_dir)
    click.echo(f"IBAMA: dados salvos em {path}")


@collect.command()
@click.option(
    "--uf",
    multiple=True,
    default=None,
    help="UFs para coletar (padrão: MG, PA, GO, BA, MT, MA).",
)
@click.pass_context
def anm(ctx: click.Context, uf: tuple[str, ...]) -> None:
    """Coletar processos da ANM SIGMINE."""
    from licenciaminer.collectors.anm import collect_anm

    output_dir: Path = ctx.obj["data_dir"]
    ufs = list(uf) if uf else None
    path = collect_anm(output_dir, ufs=ufs)
    click.echo(f"ANM: dados salvos em {path}")


@collect.command()
@click.option(
    "--file",
    "file_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Arquivo Excel da SEMAD/MG.",
)
@click.option(
    "--scrape", is_flag=True, default=False,
    help="Scrapar dados do portal web (ignora Excel).",
)
@click.option(
    "--all-activities", is_flag=True, default=False,
    help="Coletar todas as atividades (não filtrar apenas mineração).",
)
@click.option(
    "--max-pages", type=int, default=None,
    help="Limitar número de páginas (para testes).",
)
@click.option(
    "--full-refresh", is_flag=True, default=False,
    help="Forçar coleta completa (ignorar dados existentes).",
)
@click.pass_context
def mg(
    ctx: click.Context,
    file_path: Path | None,
    scrape: bool,
    all_activities: bool,
    max_pages: int | None,
    full_refresh: bool,
) -> None:
    """Processar dados da SEMAD/MG (Excel ou scraping do portal)."""
    output_dir: Path = ctx.obj["data_dir"]

    if scrape:
        from licenciaminer.collectors.mg_scraper import scrape_mg_semad

        path = scrape_mg_semad(
            output_dir,
            max_pages=max_pages,
            mining_only=not all_activities,
            full_refresh=full_refresh,
        )
    else:
        from licenciaminer.collectors.mg_semad import process_mg_excel

        path = process_mg_excel(output_dir, file_path=file_path)

    click.echo(f"MG SEMAD: dados salvos em {path}")


@collect.command("mg-docs")
@click.option(
    "--max-records", type=int, default=None,
    help="Limitar número de registros (para testes).",
)
@click.option(
    "--mining-only", is_flag=True, default=False,
    help="Enriquecer apenas registros de mineração (A-0x).",
)
@click.pass_context
def mg_docs(ctx: click.Context, max_records: int | None, mining_only: bool) -> None:
    """Buscar links de documentos PDF das páginas de detalhe da SEMAD/MG."""
    from licenciaminer.collectors.mg_scraper import enrich_with_details

    output_dir: Path = ctx.obj["data_dir"]
    path = enrich_with_details(output_dir, max_records=max_records, mining_only=mining_only)
    click.echo(f"MG SEMAD Docs: parquet atualizado em {path}")


@collect.command("mg-textos")
@click.option(
    "--max-records", type=int, default=None,
    help="Limitar número de registros (para testes).",
)
@click.option(
    "--mining-only", is_flag=True, default=False,
    help="Processar apenas registros de mineração (A-0x).",
)
@click.pass_context
def mg_textos(ctx: click.Context, max_records: int | None, mining_only: bool) -> None:
    """Baixar PDFs e extrair texto das decisões da SEMAD/MG."""
    from licenciaminer.processors.pdf_extractor import enrich_parquet_with_texts

    output_dir: Path = ctx.obj["data_dir"]
    path = enrich_parquet_with_texts(
        output_dir, max_records=max_records, mining_only=mining_only
    )
    click.echo(f"MG SEMAD Textos: parquet atualizado em {path}")


@collect.command("infracoes")
@click.option("--uf", default="MG", help="Filtrar por UF (padrão: MG, use ALL para todos).")
@click.pass_context
def infracoes(ctx: click.Context, uf: str) -> None:
    """Coletar autos de infração ambiental do IBAMA."""
    from licenciaminer.collectors.ibama_infracoes import collect_ibama_infracoes

    output_dir: Path = ctx.obj["data_dir"]
    uf_filter = None if uf == "ALL" else uf
    path = collect_ibama_infracoes(output_dir, uf_filter=uf_filter)
    click.echo(f"IBAMA Infrações: dados salvos em {path}")


@collect.command("cfem")
@click.option("--uf", default="MG", help="Filtrar por UF (padrão: MG, use ALL para todos).")
@click.option("--full-history", is_flag=True, default=False, help="Baixar histórico completo.")
@click.pass_context
def cfem(ctx: click.Context, uf: str, full_history: bool) -> None:
    """Coletar dados de arrecadação CFEM (royalties) da ANM."""
    from licenciaminer.collectors.anm_cfem import collect_cfem

    output_dir: Path = ctx.obj["data_dir"]
    uf_filter = None if uf == "ALL" else uf
    path = collect_cfem(output_dir, uf_filter=uf_filter, full_history=full_history)
    click.echo(f"CFEM: dados salvos em {path}")


@collect.command("cnpj")
@click.option("--max-records", type=int, default=None, help="Limitar consultas (para testes).")
@click.pass_context
def cnpj(ctx: click.Context, max_records: int | None) -> None:
    """Enriquecer CNPJs com dados cadastrais da Receita Federal."""
    from licenciaminer.collectors.cnpj_enrichment import collect_cnpj_data

    output_dir: Path = ctx.obj["data_dir"]
    path = collect_cnpj_data(output_dir, max_records=max_records)
    click.echo(f"CNPJ: dados salvos em {path}")


@collect.command("all")
@click.pass_context
def collect_all(ctx: click.Context) -> None:
    """Coletar de todas as fontes disponíveis."""
    ctx.invoke(ibama)
    ctx.invoke(anm)

    from licenciaminer.config import MG_DEFAULT_FILE

    if MG_DEFAULT_FILE.exists():
        ctx.invoke(mg)
    else:
        click.echo(
            f"MG SEMAD: arquivo não encontrado em {MG_DEFAULT_FILE}. "
            "Faça o download manual e coloque o arquivo nesse caminho."
        )


@cli.command()
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Arquivo de saída JSON.")
@click.pass_context
def analyze(ctx: click.Context, output: Path | None) -> None:
    """Executar análises sobre os dados coletados."""
    from licenciaminer.analysis.reports import run_analysis

    data_dir: Path = ctx.obj["data_dir"]
    run_analysis(data_dir, output=output)
