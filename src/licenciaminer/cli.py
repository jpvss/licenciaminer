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
@click.pass_context
def mg(
    ctx: click.Context,
    file_path: Path | None,
    scrape: bool,
    all_activities: bool,
    max_pages: int | None,
) -> None:
    """Processar dados da SEMAD/MG (Excel ou scraping do portal)."""
    output_dir: Path = ctx.obj["data_dir"]

    if scrape:
        from licenciaminer.collectors.mg_scraper import scrape_mg_semad

        path = scrape_mg_semad(
            output_dir,
            max_pages=max_pages,
            mining_only=not all_activities,
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
@click.pass_context
def mg_docs(ctx: click.Context, max_records: int | None) -> None:
    """Buscar links de documentos PDF das páginas de detalhe da SEMAD/MG."""
    from licenciaminer.collectors.mg_scraper import enrich_with_details

    output_dir: Path = ctx.obj["data_dir"]
    path = enrich_with_details(output_dir, max_records=max_records)
    click.echo(f"MG SEMAD Docs: parquet atualizado em {path}")


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
