"""Testes para o módulo de análise."""

from pathlib import Path
from unittest.mock import patch

import duckdb
import pandas as pd

from licenciaminer.analysis.reports import run_analysis
from licenciaminer.database.loader import create_views, get_connection


class TestDuckDBLoader:
    """Testes para o carregador DuckDB."""

    def test_creates_views_from_parquet(self, tmp_data_dir: Path) -> None:
        """Deve criar views quando parquet existe."""
        # Criar um parquet de teste
        df = pd.DataFrame({"x": [1, 2, 3]})
        df.to_parquet(tmp_data_dir / "processed" / "ibama_licencas.parquet")

        con = get_connection()
        loaded = create_views(con, tmp_data_dir)

        assert loaded["v_ibama"] is True
        assert loaded["v_anm"] is False  # não existe
        assert loaded["v_mg_semad"] is False  # não existe

        result = con.execute("SELECT COUNT(*) FROM v_ibama").fetchone()
        assert result is not None
        assert result[0] == 3
        con.close()

    def test_handles_missing_parquets(self, tmp_data_dir: Path) -> None:
        """Deve lidar com parquets ausentes sem erro."""
        con = get_connection()
        loaded = create_views(con, tmp_data_dir)
        assert all(v is False for v in loaded.values())
        con.close()


class TestRunAnalysis:
    """Testes para execução de análises."""

    def test_runs_with_mg_data(self, tmp_data_dir: Path) -> None:
        """Deve executar análise MG com dados disponíveis."""
        df = pd.DataFrame(
            {
                "ano": [2023, 2023, 2023],
                "classe": [5, 4, 5],
                "codigo_de_atividade": ["A-02-01-1", "A-03-01-1", "A-02-01-1"],
                "regional": ["SUPRAM CM", "SUPRAM CM", "SUPRAM NM"],
                "decisao": ["deferido", "indeferido", "deferido"],
                "_source": ["mg_semad"] * 3,
                "_collected_at": ["2024-01-01"] * 3,
            }
        )
        df.to_parquet(tmp_data_dir / "processed" / "mg_semad_licencas.parquet")

        # Deve rodar sem erro
        run_analysis(tmp_data_dir)

    def test_runs_with_no_data(self, tmp_data_dir: Path) -> None:
        """Deve rodar sem erro quando não há dados."""
        run_analysis(tmp_data_dir)

    def test_json_export(self, tmp_data_dir: Path) -> None:
        """Deve exportar resultados como JSON."""
        df = pd.DataFrame(
            {
                "ano": [2023],
                "classe": [5],
                "codigo_de_atividade": ["A-02"],
                "regional": ["CM"],
                "decisao": ["deferido"],
                "_source": ["mg_semad"],
                "_collected_at": ["2024-01-01"],
            }
        )
        df.to_parquet(tmp_data_dir / "processed" / "mg_semad_licencas.parquet")

        output_path = tmp_data_dir / "output.json"
        run_analysis(tmp_data_dir, output=output_path)
        assert output_path.exists()
