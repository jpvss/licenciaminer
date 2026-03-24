"""Testes para o coletor SCM da ANM."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from licenciaminer.collectors.anm_scm import collect_scm
from licenciaminer.processors.normalize import normalize_processo


# Fixture CSV simulando o formato do SCM
SAMPLE_SCM_CSV = """\
Superintendencia;Processo;Tipo de requerimento;Fase Atual;CPF/CNPJ do titular;Titular;Municipio(s);Substancia(s);Tipo(s) de Uso;Situacao
DNPM/MG;830.001/2020;Portaria de Lavra;Concessao de Lavra;12.345.678/0001-90;MINERADORA ALPHA LTDA;OURO PRETO - MG;MINERIO DE FERRO;Industrial;Sim
DNPM/MG;005.370/1964;Portaria de Lavra;Concessao de Lavra;98.765.432/0001-10;EMPRESA BETA SA;BELO HORIZONTE - MG, SABARA - MG;OURO, PRATA;Industrial;Sim
DNPM/PA;900.100/2019;Portaria de Lavra;Concessao de Lavra;11.222.333/0001-44;MINA GAMA LTDA;MARABA - PA;COBRE;Industrial;Sim
""".encode("utf-8")

SAMPLE_LIC_CSV = """\
Superintendencia;Processo;Tipo de requerimento;Fase Atual;CPF/CNPJ do titular;Titular;Municipio(s);Substancia(s);Tipo(s) de Uso;Situacao
DNPM/MG;810.500/2018;Licenciamento;Licenciamento;44.555.666/0001-77;AREIAL DO SUL LTDA;BETIM - MG;AREIA;Construcao Civil;Sim
""".encode("utf-8")

SAMPLE_PLG_CSV = """\
Superintendencia;Processo;Tipo de requerimento;Fase Atual;CPF/CNPJ do titular;Titular;Municipio(s);Substancia(s);Tipo(s) de Uso;Situacao
DNPM/MG;820.300/2015;PLG;Lavra Garimpeira;123.456.789-01;JOAO GARIMPEIRO;DIAMANTINA - MG;OURO;Nao Informado;Sim
""".encode("utf-8")

SAMPLE_REG_CSV = """\
Superintendencia;Processo;Tipo de requerimento;Fase Atual;CPF/CNPJ do titular;Titular;Municipio(s);Substancia(s);Tipo(s) de Uso;Situacao
DNPM/MG;840.200/2022;Registro de Extracao;Registro de Extracao;Governo do Estado;DEOP MG;BELO HORIZONTE - MG;BRITA;Construcao Civil;Sim
""".encode("utf-8")


def _mock_download(url: str) -> bytes:
    """Retorna CSV de fixture baseado na URL."""
    if "Portaria_de_Lavra" in url:
        return SAMPLE_SCM_CSV
    elif "Licenciamento" in url:
        return SAMPLE_LIC_CSV
    elif "PLG" in url:
        return SAMPLE_PLG_CSV
    elif "Registro_de_Extracao" in url:
        return SAMPLE_REG_CSV
    return b""


class TestCollectScm:
    """Testes para coleta de dados do SCM."""

    def test_collects_and_unifies(self, tmp_data_dir: Path) -> None:
        """Deve baixar os 4 CSVs, filtrar MG e unificar."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter="MG")

        df = pd.read_parquet(path)
        # 2 de portaria_lavra (MG), 1 licenciamento, 1 PLG, 1 registro = 5
        assert len(df) == 5
        assert set(df["regime"].unique()) == {
            "portaria_lavra", "licenciamento", "plg", "registro_extracao"
        }

    def test_filters_by_uf(self, tmp_data_dir: Path) -> None:
        """Deve filtrar registros pelo campo Município."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter="PA")

        df = pd.read_parquet(path)
        # Apenas 1 registro do PA na portaria_lavra
        assert len(df) == 1

    def test_no_uf_filter(self, tmp_data_dir: Path) -> None:
        """Sem filtro de UF, deve retornar todos os registros."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter=None)

        df = pd.read_parquet(path)
        # 3 portaria + 1 lic + 1 plg + 1 reg = 6
        assert len(df) == 6

    def test_processo_norm(self, tmp_data_dir: Path) -> None:
        """Deve normalizar número de processo para NNNNNN/YYYY."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter="MG")

        df = pd.read_parquet(path)
        assert "processo_norm" in df.columns
        norms = df["processo_norm"].tolist()
        assert "830001/2020" in norms
        assert "005370/1964" in norms

    def test_adds_metadata(self, tmp_data_dir: Path) -> None:
        """Deve adicionar colunas de metadados."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter="MG")

        df = pd.read_parquet(path)
        assert "_source" in df.columns
        assert df["_source"].iloc[0] == "anm_scm"
        assert "_collected_at" in df.columns
        assert "_source_url" in df.columns

    def test_output_path(self, tmp_data_dir: Path) -> None:
        """Deve salvar no caminho correto."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir)

        assert path == tmp_data_dir / "processed" / "scm_concessoes.parquet"
        assert path.exists()

    def test_substancia_principal(self, tmp_data_dir: Path) -> None:
        """Deve extrair substância principal de campo multi-valor."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter="MG")

        df = pd.read_parquet(path)
        assert "substancia_principal" in df.columns
        # Registro com "OURO, PRATA" deve ter "OURO" como principal
        beta = df[df["processo_norm"] == "005370/1964"]
        assert len(beta) == 1
        assert beta.iloc[0]["substancia_principal"] == "OURO"

    def test_municipio_principal(self, tmp_data_dir: Path) -> None:
        """Deve extrair município principal de campo multi-valor."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter="MG")

        df = pd.read_parquet(path)
        assert "municipio_principal" in df.columns

    def test_cnpj_normalized(self, tmp_data_dir: Path) -> None:
        """Deve normalizar CNPJ removendo pontuação."""
        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            path = collect_scm(tmp_data_dir, uf_filter="MG")

        df = pd.read_parquet(path)
        cnpj_col = next(c for c in df.columns if "cnpj" in c.lower() or "cpf" in c.lower())
        alpha = df[df["processo_norm"] == "830001/2020"]
        assert alpha.iloc[0][cnpj_col] == "12345678000190"

    def test_saves_collection_metadata(self, tmp_data_dir: Path) -> None:
        """Deve salvar metadados de coleta."""
        import json

        with patch(
            "licenciaminer.collectors.anm_scm._download_csv",
            side_effect=_mock_download,
        ):
            collect_scm(tmp_data_dir, uf_filter="MG")

        meta_path = tmp_data_dir / "processed" / "collection_metadata.json"
        assert meta_path.exists()
        with open(meta_path) as f:
            meta = json.load(f)
        assert "anm_scm" in meta
        assert int(meta["anm_scm"]["records"]) == 5


class TestNormalizeProcesso:
    """Testes para normalização de número de processo."""

    def test_with_dots(self) -> None:
        assert normalize_processo("830.001/2020") == "830001/2020"

    def test_with_leading_zeros(self) -> None:
        assert normalize_processo("005.370/1964") == "005370/1964"

    def test_already_clean(self) -> None:
        assert normalize_processo("830001/2020") == "830001/2020"

    def test_short_number(self) -> None:
        assert normalize_processo("5370/1964") == "005370/1964"

    def test_invalid_format(self) -> None:
        assert normalize_processo("invalid") == "invalid"

    def test_empty_string(self) -> None:
        assert normalize_processo("") == ""
