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


@collect.command("ral")
@click.option("--uf", default="MG", help="Filtrar por UF.")
@click.pass_context
def ral(ctx: click.Context, uf: str) -> None:
    """Coletar dados de produção mineral RAL da ANM."""
    from licenciaminer.collectors.anm_ral import collect_ral

    output_dir: Path = ctx.obj["data_dir"]
    uf_filter = None if uf == "ALL" else uf
    path = collect_ral(output_dir, uf_filter=uf_filter)
    click.echo(f"RAL: dados salvos em {path}")


@collect.command("outorgas")
@click.option("--uf", default="MG", help="Filtrar por UF.")
@click.pass_context
def outorgas(ctx: click.Context, uf: str) -> None:
    """Coletar outorgas de uso de água da ANA."""
    from licenciaminer.collectors.ana_outorgas import collect_ana_outorgas

    output_dir: Path = ctx.obj["data_dir"]
    uf_filter = None if uf == "ALL" else uf
    path = collect_ana_outorgas(output_dir, uf_filter=uf_filter)
    click.echo(f"ANA Outorgas: dados salvos em {path}")


@collect.command("copam")
@click.option(
    "--max-meetings", type=int, default=None,
    help="Limitar número de reuniões (para testes).",
)
@click.pass_context
def copam(ctx: click.Context, max_meetings: int | None) -> None:
    """Coletar reuniões da CMI (mineração) do COPAM."""
    from licenciaminer.collectors.copam import scrape_copam_cmi

    output_dir: Path = ctx.obj["data_dir"]
    path = scrape_copam_cmi(output_dir, max_meetings=max_meetings)
    click.echo(f"COPAM CMI: dados salvos em {path}")


@collect.command("scm")
@click.option("--uf", default="MG", help="Filtrar por UF (padrão: MG, use ALL para todos).")
@click.pass_context
def scm(ctx: click.Context, uf: str) -> None:
    """Coletar concessões minerárias do SCM/ANM (Portaria de Lavra, Licenciamento, PLG)."""
    from licenciaminer.collectors.anm_scm import collect_scm

    output_dir: Path = ctx.obj["data_dir"]
    uf_filter = None if uf == "ALL" else uf
    path = collect_scm(output_dir, uf_filter=uf_filter)
    click.echo(f"SCM: dados salvos em {path}")


@collect.command("spatial")
@click.option(
    "--layer",
    type=click.Choice(["all", "biomas", "ucs", "tis", "caves", "anm-geo", "overlaps"]),
    default="all",
    help="Camada espacial para coletar.",
)
@click.pass_context
def spatial(ctx: click.Context, layer: str) -> None:
    """Coletar dados geoespaciais (UCs, TIs, biomas, geometrias ANM)."""
    from licenciaminer.collectors.spatial import (
        collect_anm_geometries,
        collect_cecav_caves,
        collect_funai_tis,
        collect_ibge_biomas,
        collect_icmbio_ucs,
        compute_spatial_overlaps,
    )

    output_dir: Path = ctx.obj["data_dir"]

    if layer in ("all", "biomas"):
        collect_ibge_biomas(output_dir)
    if layer in ("all", "ucs"):
        collect_icmbio_ucs(output_dir)
    if layer in ("all", "caves"):
        collect_cecav_caves(output_dir)
    if layer in ("all", "tis"):
        collect_funai_tis(output_dir)
    if layer in ("all", "anm-geo"):
        collect_anm_geometries(output_dir)
    if layer in ("all", "overlaps"):
        compute_spatial_overlaps(output_dir)

    click.echo("Spatial: coleta concluída")


@collect.command("all")
@click.pass_context
def collect_all(ctx: click.Context) -> None:
    """Coletar de todas as fontes disponíveis."""
    ctx.invoke(ibama)
    ctx.invoke(anm)
    ctx.invoke(scm)

    from licenciaminer.config import MG_DEFAULT_FILE

    if MG_DEFAULT_FILE.exists():
        ctx.invoke(mg)
    else:
        click.echo(
            f"MG SEMAD: arquivo não encontrado em {MG_DEFAULT_FILE}. "
            "Faça o download manual e coloque o arquivo nesse caminho."
        )


@cli.command("join-concessoes")
@click.pass_context
def join_concessoes(ctx: click.Context) -> None:
    """Consolidar SCM + SIGMINE + CFEM em dataset unificado de concessões."""
    from licenciaminer.processors.join_concessions import join_concessions

    data_dir: Path = ctx.obj["data_dir"]
    path = join_concessions(data_dir)
    click.echo(f"Concessões consolidadas: {path}")


@cli.command()
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Arquivo de saída JSON.")
@click.pass_context
def analyze(ctx: click.Context, output: Path | None) -> None:
    """Executar análises sobre os dados coletados."""
    from licenciaminer.analysis.reports import run_analysis

    data_dir: Path = ctx.obj["data_dir"]
    run_analysis(data_dir, output=output)
