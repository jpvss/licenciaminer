"""Configurações centrais do LicenciaMiner."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Diretórios
# __file__ is src/licenciaminer/config.py → 3 levels up = repo root
# On Streamlit Cloud the package is installed, so __file__ is in site-packages.
# Fall back to CWD (which Streamlit Cloud sets to the repo root).
_pkg_root = Path(__file__).resolve().parent.parent.parent
_data_candidate = _pkg_root / "data"
if not _data_candidate.exists():
    _data_candidate = Path.cwd() / "data"
BASE_DIR = _data_candidate.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(_data_candidate)))
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
    "LAVRA GARIMPEIRA",
    "APTO PARA DISPONIBILIDADE",
    "REQUERIMENTO DE LICENCIAMENTO",
    "REQUERIMENTO DE REGISTRO DE EXTRAÇÃO",
    "REQUERIMENTO DE LAVRA GARIMPEIRA",
    "DIREITO DE REQUERER A LAVRA",
    "RECONHECIMENTO GEOLÓGICO",
]

# MG SEMAD
MG_DEFAULT_FILE: Path = RAW_DIR / "mg_decisoes.xlsx"
MG_MINING_CODE_PREFIX: str = "A-0"

# Timeouts e retry
HTTP_TIMEOUT: float = 120.0
RETRY_ATTEMPTS: int = 5
RETRY_MIN_WAIT: int = 2
RETRY_MAX_WAIT: int = 60
