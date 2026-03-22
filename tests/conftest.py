"""Fixtures compartilhadas para testes."""

import json
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Cria estrutura de diretórios temporária para testes."""
    (tmp_path / "raw").mkdir()
    (tmp_path / "processed").mkdir()
    (tmp_path / "reference").mkdir()
    return tmp_path


@pytest.fixture
def sample_ibama_response() -> list[dict[str, str]]:
    """Resposta simulada da API IBAMA SISLIC."""
    return [
        {
            "desTipoLicenca": "LO",
            "numLicenca": "1234/2023",
            "dataEmissao": "15/03/2023",
            "dataVencimento": "15/03/2027",
            "empreendimento": "Mina Teste Alpha",
            "nomePessoa": "Mineradora Alpha Ltda",
            "numeroProcesso": "02001.000123/2020-01",
            "tipologia": "Mineração - Lavra a céu aberto",
            "pac": "Nao",
            "Atualizacao": "2023-03-20T10:00:00",
        },
        {
            "desTipoLicenca": "LI",
            "numLicenca": "5678/2022",
            "dataEmissao": "10/06/2022",
            "dataVencimento": "10/06/2028",
            "empreendimento": "Mina Beta Subterrânea",
            "nomePessoa": "Empresa Beta SA",
            "numeroProcesso": "02001.000456/2019-50",
            "tipologia": "Mineração - Lavra subterrânea",
            "pac": "Sim",
            "Atualizacao": "2022-07-01T08:30:00",
        },
        {
            "desTipoLicenca": "LP",
            "numLicenca": "9999/2024",
            "dataEmissao": "01/01/2024",
            "dataVencimento": "01/01/2029",
            "empreendimento": "Usina Termelétrica Gama",
            "nomePessoa": "Energia Gama SA",
            "numeroProcesso": "02001.000789/2021-15",
            "tipologia": "Energia - Termelétrica",
            "pac": "Nao",
            "Atualizacao": "2024-01-05T12:00:00",
        },
    ]


@pytest.fixture
def sample_anm_response() -> dict[str, object]:
    """Resposta simulada da API ArcGIS ANM SIGMINE."""
    return {
        "features": [
            {
                "attributes": {
                    "PROCESSO": "830001/2020",
                    "NUMERO": 830001,
                    "ANO": 2020,
                    "AREA_HA": 150.5,
                    "FASE": "CONCESSÃO DE LAVRA",
                    "ULT_EVENTO": "ALVARÁ DE PESQUISA",
                    "NOME": "MINERADORA ALPHA LTDA",
                    "SUBS": "FERRO",
                    "USO": "INDUSTRIAL",
                    "UF": "MG",
                    "FID": 1,
                }
            },
            {
                "attributes": {
                    "PROCESSO": "830002/2021",
                    "NUMERO": 830002,
                    "ANO": 2021,
                    "AREA_HA": 75.3,
                    "FASE": "REQUERIMENTO DE PESQUISA",
                    "ULT_EVENTO": "REQUERIMENTO PROTOCOLADO",
                    "NOME": "EMPRESA BETA SA",
                    "SUBS": "OURO",
                    "USO": "INDUSTRIAL",
                    "UF": "MG",
                    "FID": 2,
                }
            },
        ],
        "exceededTransferLimit": False,
    }


@pytest.fixture
def sample_mg_excel(tmp_data_dir: Path) -> Path:
    """Cria um arquivo Excel simulado da SEMAD/MG para testes."""
    data = {
        "Regional": ["SUPRAM CM", "SUPRAM CM", "SUPRAM NM", "SUPRAM SM"],
        "Município": ["Belo Horizonte", "Ouro Preto", "Montes Claros", "Juiz de Fora"],
        "Empreendimento": ["Mina Alpha", "Mina Beta", "Mina Gama", "Fábrica Delta"],
        "CNPJ/CPF": [
            "12.345.678/0001-90",
            "98.765.432/0001-10",
            "11.222.333/0001-44",
            "55.666.777/0001-88",
        ],
        "Modalidade": ["LAT", "LAC", "LAT", "LAS"],
        "Processo Administrativo": ["PA-001/2023", "PA-002/2023", "PA-003/2023", "PA-004/2023"],
        "Protocolo": ["PROT-001", "PROT-002", "PROT-003", "PROT-004"],
        "Código de Atividade": ["A-02-01-1", "A-03-01-1", "A-05-01-1", "B-01-01-1"],
        "Atividade": [
            "Lavra a céu aberto - Classe 5",
            "Lavra subterrânea - Classe 4",
            "Beneficiamento mineral",
            "Indústria química",
        ],
        "Classe": [5, 4, 3, 2],
        "Ano": [2023, 2023, 2022, 2023],
        "Mês": [3, 6, 11, 1],
        "Data Publicação DOEMG": ["15/03/2023", "20/06/2023", "10/11/2022", "05/01/2023"],
        "Decisão": ["Deferido", "Indeferido", "Deferido", "Deferido"],
    }
    df = pd.DataFrame(data)
    path = tmp_data_dir / "raw" / "mg_decisoes.xlsx"
    df.to_excel(path, index=False, engine="openpyxl")
    return path


@pytest.fixture
def ibama_fixture_path() -> Path:
    """Caminho do fixture JSON do IBAMA."""
    return Path(__file__).parent / "fixtures" / "ibama_sample.json"


@pytest.fixture
def anm_fixture_path() -> Path:
    """Caminho do fixture JSON do ANM."""
    return Path(__file__).parent / "fixtures" / "anm_sample.json"
