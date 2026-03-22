"""Testes para o coletor IBAMA SISLIC."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from licenciaminer.collectors.ibama import collect_ibama


class TestCollectIbama:
    """Testes para coleta de dados do IBAMA."""

    def test_filters_mining_only(
        self, tmp_data_dir: Path, sample_ibama_response: list[dict[str, str]]
    ) -> None:
        """Deve filtrar apenas registros de mineração."""
        with patch("licenciaminer.collectors.ibama._fetch_sislic") as mock_fetch:
            mock_fetch.return_value = sample_ibama_response
            path = collect_ibama(tmp_data_dir)

        df = pd.read_parquet(path)
        # 2 de mineração, 1 de energia (filtrado)
        assert len(df) == 2
        assert all("miner" in t.lower() for t in df["tipologia"].tolist())

    def test_parses_dates(
        self, tmp_data_dir: Path, sample_ibama_response: list[dict[str, str]]
    ) -> None:
        """Deve parsear datas corretamente."""
        with patch("licenciaminer.collectors.ibama._fetch_sislic") as mock_fetch:
            mock_fetch.return_value = sample_ibama_response
            path = collect_ibama(tmp_data_dir)

        df = pd.read_parquet(path)
        assert pd.api.types.is_datetime64_any_dtype(df["data_emissao"])
        assert pd.api.types.is_datetime64_any_dtype(df["data_vencimento"])

    def test_adds_metadata(
        self, tmp_data_dir: Path, sample_ibama_response: list[dict[str, str]]
    ) -> None:
        """Deve adicionar colunas de metadados."""
        with patch("licenciaminer.collectors.ibama._fetch_sislic") as mock_fetch:
            mock_fetch.return_value = sample_ibama_response
            path = collect_ibama(tmp_data_dir)

        df = pd.read_parquet(path)
        assert "_source" in df.columns
        assert df["_source"].iloc[0] == "ibama_sislic"

    def test_output_path(
        self, tmp_data_dir: Path, sample_ibama_response: list[dict[str, str]]
    ) -> None:
        """Deve salvar no caminho correto."""
        with patch("licenciaminer.collectors.ibama._fetch_sislic") as mock_fetch:
            mock_fetch.return_value = sample_ibama_response
            path = collect_ibama(tmp_data_dir)

        assert path == tmp_data_dir / "processed" / "ibama_licencas.parquet"
        assert path.exists()

    def test_normalizes_columns(
        self, tmp_data_dir: Path, sample_ibama_response: list[dict[str, str]]
    ) -> None:
        """Deve normalizar nomes de colunas para snake_case."""
        with patch("licenciaminer.collectors.ibama._fetch_sislic") as mock_fetch:
            mock_fetch.return_value = sample_ibama_response
            path = collect_ibama(tmp_data_dir)

        df = pd.read_parquet(path)
        # Verificar que não tem CamelCase
        for col in df.columns:
            if not col.startswith("_"):
                assert col == col.lower(), f"Coluna não normalizada: {col}"
