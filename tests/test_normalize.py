"""Testes para o módulo de normalização."""

from pathlib import Path

import pandas as pd

from licenciaminer.processors.normalize import (
    add_metadata,
    atomic_parquet_write,
    normalize_cnpj,
    normalize_columns,
    parse_date_br,
    parse_date_epoch_ms,
)


class TestNormalizeColumns:
    """Testes para normalização de nomes de colunas."""

    def test_snake_case(self) -> None:
        df = pd.DataFrame({"CamelCase": [1], "another_one": [2]})
        result = normalize_columns(df)
        assert list(result.columns) == ["camel_case", "another_one"]

    def test_remove_accents(self) -> None:
        df = pd.DataFrame({"Código de Atividade": [1], "Município": [2]})
        result = normalize_columns(df)
        assert "codigo_de_atividade" in result.columns
        assert "municipio" in result.columns

    def test_special_characters(self) -> None:
        df = pd.DataFrame({"CNPJ/CPF": [1], "Data Publicação DOEMG": [2]})
        result = normalize_columns(df)
        assert "cnpj_cpf" in result.columns
        assert "data_publicacao_doemg" in result.columns

    def test_camelcase_ibama(self) -> None:
        df = pd.DataFrame({"desTipoLicenca": [1], "numLicenca": [2], "dataEmissao": [3]})
        result = normalize_columns(df)
        assert "des_tipo_licenca" in result.columns
        assert "num_licenca" in result.columns
        assert "data_emissao" in result.columns


class TestNormalizeCnpj:
    """Testes para normalização de CNPJ/CPF."""

    def test_cnpj_with_punctuation(self) -> None:
        assert normalize_cnpj("12.345.678/0001-90") == "12345678000190"

    def test_cpf_with_punctuation(self) -> None:
        assert normalize_cnpj("123.456.789-01") == "12345678901"

    def test_already_clean(self) -> None:
        assert normalize_cnpj("12345678000190") == "12345678000190"


class TestParseDateBr:
    """Testes para parsing de datas brasileiras."""

    def test_valid_date(self) -> None:
        series = pd.Series(["15/03/2023", "01/01/2024"])
        result = parse_date_br(series)
        assert result.iloc[0].year == 2023  # type: ignore[union-attr]
        assert result.iloc[0].month == 3  # type: ignore[union-attr]
        assert result.iloc[0].day == 15  # type: ignore[union-attr]

    def test_invalid_date(self) -> None:
        series = pd.Series(["invalid", None])
        result = parse_date_br(series)
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[1])


class TestParseDateEpochMs:
    """Testes para parsing de datas em epoch milliseconds."""

    def test_valid_epoch(self) -> None:
        # 2023-01-15 00:00:00 UTC = 1673740800000 ms
        series = pd.Series([1673740800000])
        result = parse_date_epoch_ms(series)
        assert result.iloc[0].year == 2023  # type: ignore[union-attr]

    def test_null_epoch(self) -> None:
        series = pd.Series([None])
        result = parse_date_epoch_ms(series)
        assert pd.isna(result.iloc[0])


class TestAddMetadata:
    """Testes para adição de metadados."""

    def test_adds_columns(self) -> None:
        df = pd.DataFrame({"a": [1, 2]})
        result = add_metadata(df, source="test")
        assert "_source" in result.columns
        assert "_collected_at" in result.columns
        assert result["_source"].iloc[0] == "test"

    def test_does_not_modify_original(self) -> None:
        df = pd.DataFrame({"a": [1]})
        add_metadata(df, source="test")
        assert "_source" not in df.columns


class TestAtomicParquetWrite:
    """Testes para escrita atômica de parquet."""

    def test_writes_file(self, tmp_path: Path) -> None:
        df = pd.DataFrame({"x": [1, 2, 3]})
        path = tmp_path / "test.parquet"
        atomic_parquet_write(df, path)
        assert path.exists()
        result = pd.read_parquet(path)
        assert len(result) == 3

    def test_creates_parent_dir(self, tmp_path: Path) -> None:
        df = pd.DataFrame({"x": [1]})
        path = tmp_path / "sub" / "dir" / "test.parquet"
        atomic_parquet_write(df, path)
        assert path.exists()
