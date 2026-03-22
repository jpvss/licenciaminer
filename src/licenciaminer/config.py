"""Configurações centrais do LicenciaMiner."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REFERENCE_DIR = DATA_DIR / "reference"
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "licenciaminer.duckdb")))

# URLs
IBAMA_SISLIC_URL = os.getenv(
    "IBAMA_SISLIC_URL",
    "https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json",
)
ANM_FEATURESERVER_URL = os.getenv(
    "ANM_FEATURESERVER_URL",
    "https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0/query",
)

# ANM
ANM_PRIORITY_UFS: list[str] = ["MG", "PA", "GO", "BA", "MT", "MA"]
ANM_MAX_RECORDS: int = 5000
ANM_FASES: list[str] = [
    "REQUERIMENTO DE PESQUISA",
    "AUTORIZAÇÃO DE PESQUISA",
    "REQUERIMENTO DE LAVRA",
    "CONCESSÃO DE LAVRA",
    "LICENCIAMENTO",
    "REGISTRO DE EXTRAÇÃO",
    "DISPONIBILIDADE",
]

# MG SEMAD
MG_DEFAULT_FILE: Path = RAW_DIR / "mg_decisoes.xlsx"
MG_MINING_CODE_PREFIX: str = "A-0"

# Timeouts e retry
HTTP_TIMEOUT: float = 120.0
RETRY_ATTEMPTS: int = 5
RETRY_MIN_WAIT: int = 2
RETRY_MAX_WAIT: int = 60
