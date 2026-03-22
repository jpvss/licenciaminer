"""Módulo de análise e geração de relatórios."""

import json
import logging
from pathlib import Path

import click
import duckdb

from licenciaminer.database.loader import create_views, get_connection
from licenciaminer.database.queries import (
    QUERY_ANM_BY_FASE_UF,
    QUERY_ANM_SUMMARY,
    QUERY_IBAMA_BY_TYPE_YEAR,
    QUERY_IBAMA_SUMMARY,
    QUERY_MG_APPROVAL_RATES,
    QUERY_MG_SUMMARY,
)

logger = logging.getLogger(__name__)


def _format_table(headers: list[str], rows: list[tuple[object, ...]]) -> str:
    """Formata dados como tabela de texto alinhada."""
    if not rows:
        return "  (sem dados)\n"

    # Converter valores para string
    str_rows = [[str(v) if v is not None else "" for v in row] for row in rows]

    # Calcular largura de cada coluna
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, val in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(val))

    # Formatar linhas
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    lines = [fmt.format(*headers)]
    lines.append("  ".join("-" * w for w in widths))
    for row in str_rows:
        # Pad row if shorter than headers
        padded = row + [""] * (len(headers) - len(row))
        lines.append(fmt.format(*padded[:len(headers)]))

    return "\n".join(lines) + "\n"


def _run_query(
    con: duckdb.DuckDBPyConnection, query: str, title: str
) -> dict[str, object] | None:
    """Executa query e exibe resultado formatado. Retorna dados para export."""
    try:
        result = con.execute(query)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()

        click.echo(f"\n{'=' * 60}")
        click.echo(f"  {title}")
        click.echo(f"{'=' * 60}\n")
        click.echo(_format_table(columns, rows))

        return {
            "title": title,
            "columns": columns,
            "rows": [[str(v) for v in row] for row in rows],
            "count": len(rows),
        }
    except duckdb.CatalogException:
        logger.debug("View não disponível para query: %s", title)
        return None


def run_analysis(data_dir: Path, output: Path | None = None) -> None:
    """Executa todas as análises sobre os dados coletados.

    Cada análise roda independentemente — se uma fonte não foi
    coletada, a análise correspondente é ignorada com um aviso.
    """
    con = get_connection()
    loaded = create_views(con, data_dir)

    results: list[dict[str, object]] = []

    click.echo("\n" + "=" * 60)
    click.echo("  LicenciaMiner — Relatório de Análise")
    click.echo("=" * 60)

    # Resumo de fontes
    click.echo("\nFontes carregadas:")
    for view, ok in loaded.items():
        status = "OK" if ok else "NÃO ENCONTRADA"
        click.echo(f"  {view}: {status}")

    # Análises MG
    if loaded.get("v_mg_semad"):
        r = _run_query(con, QUERY_MG_SUMMARY, "MG SEMAD — Resumo Geral de Aprovação")
        if r:
            results.append(r)
        r = _run_query(
            con, QUERY_MG_APPROVAL_RATES, "MG SEMAD — Aprovação por Classe/Atividade/Regional/Ano"
        )
        if r:
            results.append(r)
    else:
        click.echo("\n⚠ MG SEMAD: dados não disponíveis. Execute 'licenciaminer collect mg'.")

    # Análises IBAMA
    if loaded.get("v_ibama"):
        r = _run_query(con, QUERY_IBAMA_SUMMARY, "IBAMA — Resumo Geral")
        if r:
            results.append(r)
        r = _run_query(con, QUERY_IBAMA_BY_TYPE_YEAR, "IBAMA — Licenças por Tipo/Ano")
        if r:
            results.append(r)
    else:
        click.echo("\n⚠ IBAMA: dados não disponíveis. Execute 'licenciaminer collect ibama'.")

    # Análises ANM
    if loaded.get("v_anm"):
        r = _run_query(con, QUERY_ANM_SUMMARY, "ANM — Resumo Geral")
        if r:
            results.append(r)
        r = _run_query(con, QUERY_ANM_BY_FASE_UF, "ANM — Distribuição por Fase/UF")
        if r:
            results.append(r)
    else:
        click.echo("\n⚠ ANM: dados não disponíveis. Execute 'licenciaminer collect anm'.")

    # Exportar JSON se solicitado
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        click.echo(f"\nResultados exportados para: {output}")

    con.close()
