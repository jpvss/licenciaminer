"""Coletor de dados geoespaciais de restrições ambientais.

Baixa shapefiles de:
- ICMBio: Unidades de Conservação (UCs)
- FUNAI: Terras Indígenas (TIs)
- IBGE: Biomas
- ANM: Processos minerários com geometria (shapefile bulk)

Realiza spatial join com processos ANM para identificar sobreposições.
"""

import io
import logging
import zipfile
from pathlib import Path

import geopandas as gpd
import httpx
import pandas as pd
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from licenciaminer.collectors.metadata import save_collection_metadata
from licenciaminer.config import (
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import add_metadata, atomic_parquet_write

logger = logging.getLogger(__name__)

# Download URLs
ANM_SHAPEFILE_URL = (
    "https://app.anm.gov.br/dadosabertos/SIGMINE/PROCESSOS_MINERARIOS/BRASIL.zip"
)
IBGE_BIOMAS_URL = (
    "http://geoftp.ibge.gov.br/informacoes_ambientais/"
    "estudos_ambientais/biomas/vetores/Biomas_250mil.zip"
)
# FUNAI shapefiles
FUNAI_TI_URL = (
    "https://geoserver.funai.gov.br/geoserver/Funai/ows"
    "?service=WFS&version=1.0.0&request=GetFeature"
    "&typeName=Funai:tis_poligonais_portarias"
    "&outputFormat=SHAPE-ZIP"
    "&CQL_FILTER=uf_sigla%20LIKE%20%27%25MG%25%27"
)
# CECAV cave occurrence areas
CECAV_CAVES_URL = (
    "https://www.gov.br/icmbio/pt-br/assuntos/centros-de-pesquisa/"
    "cavernas/publicacoes/Area%20de%20Ocorrencia%20de%20Cavernas/"
    "areas_ocorrencia_cavernas_brasil.zip"
)


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _download_file(url: str, timeout: float = 300.0) -> bytes:
    """Baixa arquivo via HTTP."""
    logger.info("Baixando %s", url[:100])
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def _read_shapefile_from_zip(zip_bytes: bytes) -> gpd.GeoDataFrame:
    """Lê shapefile de dentro de um ZIP."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(tmp_path)

        # Encontrar o .shp
        shp_files = list(tmp_path.rglob("*.shp"))
        if not shp_files:
            raise ValueError("Nenhum .shp encontrado no ZIP")

        gdf: gpd.GeoDataFrame = gpd.read_file(shp_files[0])
        return gdf


def collect_ibge_biomas(data_dir: Path) -> Path:
    """Baixa e salva shapefile de biomas do IBGE."""
    zip_bytes = _download_file(IBGE_BIOMAS_URL)
    gdf = _read_shapefile_from_zip(zip_bytes)
    logger.info("IBGE Biomas: %d polígonos", len(gdf))

    output_path = data_dir / "reference" / "ibge_biomas.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(output_path)
    save_collection_metadata(data_dir, "ibge_biomas", len(gdf))
    logger.info("IBGE Biomas: salvos em %s", output_path)
    return output_path


def collect_icmbio_ucs(data_dir: Path) -> Path:
    """Baixa Unidades de Conservação federais do ICMBio."""
    # Download direto do shapefile oficial
    url = (
        "https://www.gov.br/icmbio/pt-br/assuntos/dados_geoespaciais/"
        "mapa-tematico-e-dados-geoestatisticos-das-unidades-de-"
        "conservacao-federais/limites_ucs_federais_022026_a.zip"
    )
    zip_bytes = _download_file(url)
    gdf = _read_shapefile_from_zip(zip_bytes)

    logger.info("ICMBio UCs: %d unidades de conservação", len(gdf))

    output_path = data_dir / "reference" / "icmbio_ucs.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(output_path)
    save_collection_metadata(data_dir, "icmbio_ucs", len(gdf))
    logger.info("ICMBio UCs: salvos em %s", output_path)
    return output_path


def collect_funai_tis(data_dir: Path) -> Path:
    """Baixa Terras Indígenas da FUNAI via WFS (filtrado para MG)."""
    try:
        zip_bytes = _download_file(FUNAI_TI_URL)
        gdf = _read_shapefile_from_zip(zip_bytes)
    except Exception:
        logger.warning(
            "FUNAI WFS falhou — tentando GeoJSON"
        )
        url = (
            "https://geoserver.funai.gov.br/geoserver/Funai/ows"
            "?service=WFS&version=1.0.0&request=GetFeature"
            "&typeName=Funai:tis_poligonais_portarias"
            "&outputFormat=application/json"
            "&CQL_FILTER=uf_sigla%20LIKE%20%27%25MG%25%27"
        )
        json_bytes = _download_file(url)
        gdf = gpd.read_file(io.BytesIO(json_bytes))

    logger.info("FUNAI TIs: %d terras indígenas", len(gdf))

    output_path = data_dir / "reference" / "funai_tis.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(output_path)
    save_collection_metadata(data_dir, "funai_tis", len(gdf))
    logger.info("FUNAI TIs: salvos em %s", output_path)
    return output_path


def collect_cecav_caves(data_dir: Path) -> Path:
    """Baixa áreas de ocorrência de cavernas do CECAV/ICMBio."""
    zip_bytes = _download_file(CECAV_CAVES_URL)
    gdf = _read_shapefile_from_zip(zip_bytes)
    logger.info("CECAV Cavernas: %d áreas de ocorrência", len(gdf))

    output_path = data_dir / "reference" / "cecav_cavernas.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(output_path)
    save_collection_metadata(data_dir, "cecav_cavernas", len(gdf))
    logger.info("CECAV Cavernas: salvos em %s", output_path)
    return output_path


def collect_anm_geometries(data_dir: Path) -> Path:
    """Baixa shapefile completo da ANM com geometrias dos processos.

    Arquivo grande (~122MB ZIP). Filtra para MG após download.
    """
    zip_bytes = _download_file(ANM_SHAPEFILE_URL, timeout=600.0)
    logger.info("ANM Shapefile: %d MB baixados", len(zip_bytes) // 1_000_000)

    gdf = _read_shapefile_from_zip(zip_bytes)
    logger.info("ANM Shapefile: %d processos (Brasil)", len(gdf))

    # Filtrar MG
    uf_col = next(
        (c for c in gdf.columns if c.upper() == "UF"), None
    )
    if uf_col:
        gdf = gdf[gdf[uf_col] == "MG"].copy()
        logger.info("ANM Shapefile: %d processos em MG", len(gdf))

    output_path = data_dir / "reference" / "anm_geometrias_mg.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(output_path)
    save_collection_metadata(data_dir, "anm_geometrias_mg", len(gdf))
    logger.info("ANM Geometrias MG: salvos em %s", output_path)
    return output_path


def compute_spatial_overlaps(data_dir: Path) -> Path:
    """Calcula sobreposições entre processos ANM e camadas de restrição.

    Para cada processo ANM em MG, verifica se há sobreposição com:
    - Unidades de Conservação (UCs)
    - Terras Indígenas (TIs)
    - Biomas

    Salva resultado como parquet com colunas de overlap.
    """
    ref_dir = data_dir / "reference"

    # Carregar geometrias ANM
    anm_path = ref_dir / "anm_geometrias_mg.parquet"
    if not anm_path.exists():
        raise FileNotFoundError(
            f"ANM geometrias não encontradas: {anm_path}. "
            "Execute 'licenciaminer collect spatial-anm' primeiro."
        )
    gdf_anm = gpd.read_parquet(anm_path)
    logger.info("Spatial: %d processos ANM carregados", len(gdf_anm))

    # Garantir CRS consistente (SIRGAS 2000 = EPSG:4674)
    gdf_anm = (
        gdf_anm.set_crs("EPSG:4674")
        if gdf_anm.crs is None
        else gdf_anm.to_crs("EPSG:4674")
    )

    processo_col = next(
        (c for c in gdf_anm.columns if c.upper() == "PROCESSO"), "PROCESSO"
    )

    # Overlap com UCs
    uc_path = ref_dir / "icmbio_ucs.parquet"
    if uc_path.exists():
        gdf_uc = gpd.read_parquet(uc_path).to_crs("EPSG:4674")
        joined = gpd.sjoin(gdf_anm, gdf_uc, how="left", predicate="intersects")
        # Agregar: lista de UCs que sobrepõem cada processo
        uc_col = next(
            (c for c in gdf_uc.columns if "nome" in c.lower()), "index_right"
        )
        uc_overlap = (
            joined.groupby(processo_col)[uc_col]
            .apply(lambda x: ";".join(x.dropna().unique()))
            .reset_index()
            .rename(columns={uc_col: "ucs_sobrepostas"})
        )
        gdf_anm = gdf_anm.merge(uc_overlap, on=processo_col, how="left")
        gdf_anm["tem_uc"] = gdf_anm["ucs_sobrepostas"].str.len() > 0
        n_uc = gdf_anm["tem_uc"].sum()
        logger.info("Spatial: %d processos com sobreposição UC", n_uc)
    else:
        logger.warning("ICMBio UCs não encontradas — pulando")

    # Overlap com TIs
    ti_path = ref_dir / "funai_tis.parquet"
    if ti_path.exists():
        gdf_ti = gpd.read_parquet(ti_path).to_crs("EPSG:4674")
        joined = gpd.sjoin(gdf_anm, gdf_ti, how="left", predicate="intersects")
        ti_col = next(
            (c for c in gdf_ti.columns if "nome" in c.lower()), "index_right"
        )
        ti_overlap = (
            joined.groupby(processo_col)[ti_col]
            .apply(lambda x: ";".join(x.dropna().unique()))
            .reset_index()
            .rename(columns={ti_col: "tis_sobrepostas"})
        )
        gdf_anm = gdf_anm.merge(ti_overlap, on=processo_col, how="left")
        gdf_anm["tem_ti"] = gdf_anm["tis_sobrepostas"].str.len() > 0
        n_ti = gdf_anm["tem_ti"].sum()
        logger.info("Spatial: %d processos com sobreposição TI", n_ti)
    else:
        logger.warning("FUNAI TIs não encontradas — pulando")

    # Overlap com Biomas
    bioma_path = ref_dir / "ibge_biomas.parquet"
    if bioma_path.exists():
        gdf_bioma = gpd.read_parquet(bioma_path).to_crs("EPSG:4674")
        joined = gpd.sjoin(gdf_anm, gdf_bioma, how="left", predicate="intersects")
        bioma_col = next(
            (c for c in gdf_bioma.columns if "bioma" in c.lower()), "index_right"
        )
        bioma_result = (
            joined.groupby(processo_col)[bioma_col]
            .apply(lambda x: ";".join(x.dropna().unique()))
            .reset_index()
            .rename(columns={bioma_col: "biomas"})
        )
        gdf_anm = gdf_anm.merge(bioma_result, on=processo_col, how="left")
        logger.info(
            "Spatial: biomas atribuídos a %d processos",
            gdf_anm["biomas"].notna().sum(),
        )
    else:
        logger.warning("IBGE Biomas não encontrados — pulando")

    # Salvar resultado (sem geometria — apenas atributos + overlaps)
    result_df = pd.DataFrame(gdf_anm.drop(columns=["geometry"], errors="ignore"))
    result_df = add_metadata(result_df, source="spatial_overlaps")

    output_path = data_dir / "processed" / "anm_spatial_overlaps.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(result_df, output_path)
    save_collection_metadata(data_dir, "spatial_overlaps", len(result_df))
    logger.info(
        "Spatial: resultado salvo em %s (%d registros)", output_path, len(result_df)
    )
    return output_path
