"""Testes para o coletor ANM SIGMINE."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from licenciaminer.collectors.anm import collect_anm


class TestCollectAnm:
    """Testes para coleta de dados da ANM."""

    def test_collects_features(
        self, tmp_data_dir: Path, sample_anm_response: dict[str, object]
    ) -> None:
        """Deve coletar features do ArcGIS e salvar como parquet."""
        with patch("licenciaminer.collectors.anm._query_arcgis") as mock_query:
            mock_query.return_value = sample_anm_response
            path = collect_anm(tmp_data_dir, ufs=["MG"])

        df = pd.read_parquet(path)
        assert len(df) == 2
        assert "PROCESSO" in df.columns
        assert "UF" in df.columns

    def test_adds_metadata(
        self, tmp_data_dir: Path, sample_anm_response: dict[str, object]
    ) -> None:
        """Deve adicionar colunas de metadados."""
        with patch("licenciaminer.collectors.anm._query_arcgis") as mock_query:
            mock_query.return_value = sample_anm_response
            path = collect_anm(tmp_data_dir, ufs=["MG"])

        df = pd.read_parquet(path)
        assert "_source" in df.columns
        assert df["_source"].iloc[0] == "anm_sigmine"

    def test_output_path(
        self, tmp_data_dir: Path, sample_anm_response: dict[str, object]
    ) -> None:
        """Deve salvar no caminho correto."""
        with patch("licenciaminer.collectors.anm._query_arcgis") as mock_query:
            mock_query.return_value = sample_anm_response
            path = collect_anm(tmp_data_dir, ufs=["MG"])

        assert path == tmp_data_dir / "processed" / "anm_processos.parquet"
        assert path.exists()

    def test_multiple_ufs(
        self, tmp_data_dir: Path, sample_anm_response: dict[str, object]
    ) -> None:
        """Deve coletar de múltiplas UFs."""
        with patch("licenciaminer.collectors.anm._query_arcgis") as mock_query:
            mock_query.return_value = sample_anm_response
            path = collect_anm(tmp_data_dir, ufs=["MG", "PA"])

        df = pd.read_parquet(path)
        # 2 registros por UF x 2 UFs = 4 registros
        assert len(df) == 4
