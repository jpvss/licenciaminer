"""Testes para o processador MG SEMAD."""

from pathlib import Path

import pandas as pd
import pytest

from licenciaminer.collectors.mg_semad import process_mg_excel


class TestProcessMgExcel:
    """Testes para processamento de dados da SEMAD/MG."""

    def test_filters_mining_codes(
        self, tmp_data_dir: Path, sample_mg_excel: Path
    ) -> None:
        """Deve filtrar apenas atividades de mineração (A-0x)."""
        path = process_mg_excel(tmp_data_dir, file_path=sample_mg_excel)
        df = pd.read_parquet(path)
        # 3 de mineração (A-02, A-03, A-05), 1 de indústria (B-01, filtrado)
        assert len(df) == 3

    def test_normalizes_decisao(
        self, tmp_data_dir: Path, sample_mg_excel: Path
    ) -> None:
        """Deve normalizar valores da coluna decisão."""
        path = process_mg_excel(tmp_data_dir, file_path=sample_mg_excel)
        df = pd.read_parquet(path)
        valid_values = {"deferido", "indeferido", "outro"}
        assert set(df["decisao"].unique()).issubset(valid_values)

    def test_normalizes_cnpj(
        self, tmp_data_dir: Path, sample_mg_excel: Path
    ) -> None:
        """Deve remover pontuação do CNPJ."""
        path = process_mg_excel(tmp_data_dir, file_path=sample_mg_excel)
        df = pd.read_parquet(path)
        for cnpj in df["cnpj_cpf"].dropna():
            assert "." not in cnpj
            assert "/" not in cnpj
            assert "-" not in cnpj

    def test_normalizes_columns(
        self, tmp_data_dir: Path, sample_mg_excel: Path
    ) -> None:
        """Deve normalizar nomes de colunas."""
        path = process_mg_excel(tmp_data_dir, file_path=sample_mg_excel)
        df = pd.read_parquet(path)
        assert "codigo_de_atividade" in df.columns
        assert "municipio" in df.columns
        assert "decisao" in df.columns

    def test_adds_metadata(
        self, tmp_data_dir: Path, sample_mg_excel: Path
    ) -> None:
        """Deve adicionar colunas de metadados."""
        path = process_mg_excel(tmp_data_dir, file_path=sample_mg_excel)
        df = pd.read_parquet(path)
        assert "_source" in df.columns
        assert df["_source"].iloc[0] == "mg_semad"

    def test_missing_file_raises(self, tmp_data_dir: Path) -> None:
        """Deve levantar erro quando arquivo não existe."""
        with pytest.raises(FileNotFoundError, match="SEMAD"):
            process_mg_excel(tmp_data_dir, file_path=Path("/nonexistent.xlsx"))

    def test_output_path(
        self, tmp_data_dir: Path, sample_mg_excel: Path
    ) -> None:
        """Deve salvar no caminho correto."""
        path = process_mg_excel(tmp_data_dir, file_path=sample_mg_excel)
        assert path == tmp_data_dir / "processed" / "mg_semad_licencas.parquet"
        assert path.exists()
