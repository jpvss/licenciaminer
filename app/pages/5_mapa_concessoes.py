"""Tab 5: Mapa de Concessões — Visualização geoespacial de concessões minerárias."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.styles.theme import (  # noqa: E402
    empty_state,
    hero_html,
    inject_theme,
    insight_card,
    section_header,
    source_attribution,
)

inject_theme(st)

st.markdown(
    hero_html(
        "Mapa de Concessões",
        "Polígonos de concessões minerárias em Minas Gerais",
    ),
    unsafe_allow_html=True,
)

# ── Imports pesados (lazy) ──
try:
    import folium  # noqa: E402
    import geopandas as gpd  # noqa: E402
    from streamlit_folium import st_folium  # noqa: E402
except ImportError:
    st.error("Instale: `pip install folium streamlit-folium geopandas`")
    st.stop()

from licenciaminer.config import DATA_DIR, REFERENCE_DIR  # noqa: E402
from licenciaminer.processors.normalize import normalize_processo  # noqa: E402


# ── Carregar geometrias ──
@st.cache_data(ttl=600)
def _load_geometries():
    """Carrega geometrias ANM e simplifica para renderização."""
    geo_path = REFERENCE_DIR / "anm_geometrias_mg.parquet"
    if not geo_path.exists():
        return None

    gdf = gpd.read_parquet(geo_path)
    gdf["processo_norm"] = gdf["PROCESSO"].apply(normalize_processo)

    # Simplificar geometrias para performance
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.001, preserve_topology=True)

    return gdf


@st.cache_data(ttl=600)
def _load_concessoes_data():
    """Carrega dados tabulares do SCM para enriquecer geometrias."""
    import pandas as pd

    # Tentar concessões consolidadas primeiro, depois SCM puro
    for fname in ["concessoes_mg.parquet", "scm_concessoes.parquet"]:
        path = DATA_DIR / "processed" / fname
        if path.exists():
            return pd.read_parquet(path), fname
    return None, None


@st.cache_data(ttl=600)
def _load_restriction_layer(name: str):
    """Carrega camada de restrição espacial."""
    paths = {
        "ucs": REFERENCE_DIR / "icmbio_ucs.parquet",
        "tis": REFERENCE_DIR / "funai_tis.parquet",
    }
    path = paths.get(name)
    if path and path.exists():
        gdf = gpd.read_parquet(path)
        gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.005, preserve_topology=True)
        return gdf
    return None


# ── Carregar dados ──
gdf = _load_geometries()
if gdf is None:
    st.markdown(
        empty_state(
            "🗺️",
            "Geometrias não encontradas. Execute:\n\n"
            "`licenciaminer collect spatial --layer anm-geo`",
        ),
        unsafe_allow_html=True,
    )
    st.stop()

conc_df, conc_source = _load_concessoes_data()

# Enriquecer geometrias com dados do SCM/concessões
if conc_df is not None and "processo_norm" in conc_df.columns:
    # Selecionar colunas úteis para o mapa
    enrich_cols = ["processo_norm"]
    for col in ["titular", "regime", "substancia_principal", "municipio_principal",
                 "categoria", "ativo_cfem", "cfem_total", "estrategico"]:
        if col in conc_df.columns:
            enrich_cols.append(col)

    conc_dedup = conc_df[enrich_cols].drop_duplicates(subset=["processo_norm"])
    gdf = gdf.merge(conc_dedup, on="processo_norm", how="left")
    has_enrichment = True
else:
    has_enrichment = False

# ── Filtros na sidebar ──
MAX_POLYGONS = 5000

with st.sidebar:
    st.markdown(section_header("Filtros do Mapa"), unsafe_allow_html=True)

    filtered = gdf.copy()

    # Filtro por regime
    if has_enrichment and "regime" in filtered.columns:
        regimes = sorted(filtered["regime"].dropna().unique().tolist())
        regime_labels = {
            "portaria_lavra": "Portaria de Lavra",
            "licenciamento": "Licenciamento",
            "plg": "Lavra Garimpeira",
            "registro_extracao": "Registro de Extração",
        }
        selected_regimes = st.multiselect(
            "Regime",
            regimes,
            format_func=lambda x: regime_labels.get(x, x),
        )
        if selected_regimes:
            filtered = filtered[filtered["regime"].isin(selected_regimes)]

    # Filtro por categoria de substância
    if has_enrichment and "categoria" in filtered.columns:
        categorias = sorted(filtered["categoria"].dropna().unique().tolist())
        selected_cats = st.multiselect("Categoria", categorias)
        if selected_cats:
            filtered = filtered[filtered["categoria"].isin(selected_cats)]

    # Filtro por substância
    if has_enrichment and "substancia_principal" in filtered.columns:
        subs = sorted(filtered["substancia_principal"].dropna().unique().tolist())[:100]
        selected_subs = st.multiselect("Substância", subs)
        if selected_subs:
            filtered = filtered[filtered["substancia_principal"].isin(selected_subs)]

    # CFEM ativo
    if has_enrichment and "ativo_cfem" in filtered.columns:
        cfem_opt = st.radio(
            "Status CFEM", ["Todos", "Ativo", "Inativo"], index=0
        )
        if cfem_opt == "Ativo":
            filtered = filtered[filtered["ativo_cfem"] == True]  # noqa: E712
        elif cfem_opt == "Inativo":
            filtered = filtered[
                (filtered["ativo_cfem"] == False) | (filtered["ativo_cfem"].isna())  # noqa: E712
            ]

    # Estratégico
    if has_enrichment and "estrategico" in filtered.columns:
        only_strategic = st.toggle("Apenas estratégicos", value=False)
        if only_strategic:
            filtered = filtered[filtered["estrategico"] == "sim"]

    # Colorir por
    color_by_options = ["FASE"]
    if has_enrichment:
        if "categoria" in filtered.columns:
            color_by_options.insert(0, "categoria")
        if "regime" in filtered.columns:
            color_by_options.append("regime")
        if "ativo_cfem" in filtered.columns:
            color_by_options.append("ativo_cfem")

    color_by = st.selectbox("Colorir por", color_by_options)

    st.divider()

    # Layers de restrição
    st.markdown(section_header("Camadas"), unsafe_allow_html=True)
    show_ucs = st.toggle("Unidades de Conservação", value=False)
    show_tis = st.toggle("Terras Indígenas", value=False)

# ── Limitar polígonos ──
total_filtered = len(filtered)
if total_filtered > MAX_POLYGONS:
    st.warning(
        f"Filtro retornou {total_filtered:,} polígonos. "
        f"Mostrando os primeiros {MAX_POLYGONS:,}. Aplique filtros para refinar."
    )
    filtered = filtered.head(MAX_POLYGONS)

# ── KPIs ──
cols_kpi = st.columns(4)
with cols_kpi[0]:
    st.markdown(
        insight_card("Polígonos", f"{len(filtered):,}", f"de {len(gdf):,} total"),
        unsafe_allow_html=True,
    )
with cols_kpi[1]:
    if has_enrichment and "regime" in filtered.columns:
        matched = filtered["regime"].notna().sum()
        st.markdown(
            insight_card("Enriquecidos", f"{matched:,}", "com dados SCM"),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            insight_card("Processos", f"{len(filtered):,}", "geometrias"),
            unsafe_allow_html=True,
        )
with cols_kpi[2]:
    if has_enrichment and "substancia_principal" in filtered.columns:
        n_subs = filtered["substancia_principal"].nunique()
        st.markdown(
            insight_card("Substâncias", str(n_subs), "distintas"),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            insight_card("UF", "MG", "Minas Gerais"),
            unsafe_allow_html=True,
        )
with cols_kpi[3]:
    area_total = filtered["AREA_HA"].sum() if "AREA_HA" in filtered.columns else 0
    st.markdown(
        insight_card("Área Total", f"{area_total:,.0f}", "hectares"),
        unsafe_allow_html=True,
    )

# ── Paleta de cores ──
CATEGORY_COLORS = {
    "Metálicos Ferrosos": "#C45B52",
    "Metálicos Preciosos": "#D4A847",
    "Metálicos Estratégicos": "#E67E22",
    "Metálicos Não-Ferrosos": "#9B59B6",
    "Gemas e Pedras Preciosas": "#1ABC9C",
    "Industrial": "#3498DB",
    "Construção Civil": "#95A5A6",
    "Rochas Ornamentais": "#8D6E63",
    "Água Mineral": "#2980B9",
}

REGIME_COLORS = {
    "portaria_lavra": "#D4A847",
    "licenciamento": "#3498DB",
    "plg": "#E67E22",
    "registro_extracao": "#95A5A6",
}

FASE_COLORS = {
    "CONCESSÃO DE LAVRA": "#D4A847",
    "CONCESSAO DE LAVRA": "#D4A847",
    "LICENCIAMENTO": "#3498DB",
    "LAVRA GARIMPEIRA": "#E67E22",
    "AUTORIZAÇÃO DE PESQUISA": "#5BA77D",
    "REQUERIMENTO DE PESQUISA": "#95A5A6",
    "REQUERIMENTO DE LAVRA": "#C17F59",
    "DISPONIBILIDADE": "#7f8c8d",
}

DEFAULT_COLOR = "#5E6B80"


def _get_color(row, color_by_col):
    """Retorna cor do polígono baseada na coluna de agrupamento."""
    val = row.get(color_by_col)
    if val is None or (isinstance(val, float) and val != val):
        return DEFAULT_COLOR

    if color_by_col == "categoria":
        return CATEGORY_COLORS.get(str(val), DEFAULT_COLOR)
    elif color_by_col == "regime":
        return REGIME_COLORS.get(str(val), DEFAULT_COLOR)
    elif color_by_col == "FASE":
        return FASE_COLORS.get(str(val), DEFAULT_COLOR)
    elif color_by_col == "ativo_cfem":
        return "#5BA77D" if val else "#C45B52"

    return DEFAULT_COLOR


# ── Construir mapa ──
st.markdown(section_header("Mapa"), unsafe_allow_html=True)

# Centro de MG
m = folium.Map(
    location=[-19.9, -43.9],
    zoom_start=7,
    tiles="CartoDB positron",
)

# Adicionar polígonos de concessões
for _, row in filtered.iterrows():
    geom = row.geometry
    if geom is None or geom.is_empty:
        continue

    color = _get_color(row, color_by)

    # Popup com detalhes
    processo = str(row.get("processo_norm", row.get("PROCESSO", "—")))
    popup_parts = [f"<b>Processo:</b> {processo}"]

    if has_enrichment:
        titular = row.get("titular")
        if titular and str(titular) != "nan":
            popup_parts.append(f"<b>Titular:</b> {str(titular)[:50]}")
        subs = row.get("substancia_principal")
        if subs and str(subs) != "nan":
            popup_parts.append(f"<b>Substância:</b> {subs}")
        cat = row.get("categoria")
        if cat and str(cat) != "nan":
            popup_parts.append(f"<b>Categoria:</b> {cat}")

    area = row.get("AREA_HA")
    if area and area == area:
        popup_parts.append(f"<b>Área:</b> {area:,.1f} ha")

    fase = row.get("FASE")
    if fase and str(fase) != "nan":
        popup_parts.append(f"<b>Fase:</b> {fase}")

    if has_enrichment:
        cfem = row.get("cfem_total")
        if cfem and cfem == cfem:
            popup_parts.append(f"<b>CFEM Total:</b> R$ {cfem:,.2f}")
        ativo = row.get("ativo_cfem")
        if ativo is not None:
            status = "Ativo" if ativo else "Inativo"
            popup_parts.append(f"<b>Status:</b> {status}")

    popup_html = "<br>".join(popup_parts)

    # Renderizar geometria
    geo_json = gpd.GeoDataFrame([row], geometry="geometry").to_json()
    folium.GeoJson(
        geo_json,
        style_function=lambda _, c=color: {
            "fillColor": c,
            "color": c,
            "weight": 1,
            "fillOpacity": 0.4,
        },
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=processo,
    ).add_to(m)

# ── Camadas de restrição ──
if show_ucs:
    ucs = _load_restriction_layer("ucs")
    if ucs is not None:
        folium.GeoJson(
            ucs.to_json(),
            name="Unidades de Conservação",
            style_function=lambda _: {
                "fillColor": "#2ECC71",
                "color": "#27AE60",
                "weight": 1,
                "fillOpacity": 0.15,
            },
            tooltip="Unidade de Conservação",
        ).add_to(m)

if show_tis:
    tis = _load_restriction_layer("tis")
    if tis is not None:
        folium.GeoJson(
            tis.to_json(),
            name="Terras Indígenas",
            style_function=lambda _: {
                "fillColor": "#E74C3C",
                "color": "#C0392B",
                "weight": 1,
                "fillOpacity": 0.15,
            },
            tooltip="Terra Indígena",
        ).add_to(m)

# Layer control se layers ativas
if show_ucs or show_tis:
    folium.LayerControl().add_to(m)

# ── Renderizar mapa ──
st_folium(m, width="100%", height=600, returned_objects=[])

# ── Legenda ──
if color_by == "categoria":
    palette = CATEGORY_COLORS
elif color_by == "regime":
    palette = {
        "Portaria de Lavra": "#D4A847",
        "Licenciamento": "#3498DB",
        "Lavra Garimpeira": "#E67E22",
        "Registro de Extração": "#95A5A6",
    }
elif color_by == "ativo_cfem":
    palette = {"Ativo (CFEM)": "#5BA77D", "Inativo": "#C45B52"}
else:
    palette = {k: v for k, v in list(FASE_COLORS.items())[:6]}

legend_items = " ".join(
    f'<span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px;">'
    f'<span style="width:12px;height:12px;border-radius:2px;background:{color};display:inline-block;"></span>'
    f'<span style="font-size:0.8rem;color:var(--slate);">{label}</span></span>'
    for label, color in palette.items()
)
st.markdown(f'<div style="margin-top:8px;">{legend_items}</div>', unsafe_allow_html=True)

st.markdown(
    source_attribution(
        f"{len(filtered):,} polígonos · SIGMINE/ANM"
        + (f" + {conc_source}" if conc_source else "")
    ),
    unsafe_allow_html=True,
)
