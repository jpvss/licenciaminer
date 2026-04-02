"""Endpoints de visão geral e estatísticas agregadas."""

import logging

from fastapi import APIRouter

from api.services.database import load_metadata, run_query
from licenciaminer.database.queries import (
    QUERY_ANM_SUMMARY,
    QUERY_IBAMA_SUMMARY,
    QUERY_MG_SUMMARY,
    QUERY_MINING_SUMMARY,
    QUERY_MINING_TREND,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview/stats")
def get_overview_stats():
    """Retorna KPIs agregados do dashboard principal."""
    mg = run_query(QUERY_MG_SUMMARY)
    mining = run_query(QUERY_MINING_SUMMARY)
    ibama = run_query(QUERY_IBAMA_SUMMARY)
    anm = run_query(QUERY_ANM_SUMMARY)

    return {
        "mg_summary": mg[0] if mg else None,
        "mining_summary": mining[0] if mining else None,
        "ibama_summary": ibama[0] if ibama else None,
        "anm_summary": anm[0] if anm else None,
    }


@router.get("/overview/trend")
def get_mining_trend():
    """Tendência temporal de aprovação de mineração."""
    return run_query(QUERY_MINING_TREND)


@router.get("/overview/insights")
def get_overview_insights():
    """Retorna 4 insights calculados do dashboard (worst class, regional, etc.)."""

    def _safe(sql: str) -> list[dict]:
        try:
            return run_query(sql) or []
        except Exception:
            logger.exception("insight query failed")
            return []

    mg = _safe(QUERY_MG_SUMMARY)
    mining = _safe(QUERY_MINING_SUMMARY)

    general_rate = mg[0].get("taxa_aprovacao_geral", 0) if mg else 0
    mining_rate = mining[0].get("taxa_aprovacao_mineracao", 0) if mining else 0
    mining_count = mining[0].get("total_decisoes", 0) if mining else 0

    # Insight 1: Mining vs general approval rate
    diff = round(mining_rate - general_rate, 1)
    insight_1 = {
        "title": "Mineração vs Geral",
        "value": f"{mining_rate}% vs {general_rate}%",
        "detail": (
            f"Mineração tem taxa {'menor' if diff < 0 else 'maior'} "
            f"({abs(diff):.0f}pp) · N={mining_count:,}".replace(",", ".")
        ),
        "tone": "negative" if diff < 0 else "positive",
    }

    # Insight 2: Worst class (lowest approval rate)
    class_stats = _safe("""
        SELECT classe, COUNT(*) AS n,
            ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1) AS taxa
        FROM v_mg_semad WHERE atividade LIKE 'A-0%' AND classe IS NOT NULL
        GROUP BY classe ORDER BY classe
    """)
    valid = [c for c in class_stats if c.get("taxa") is not None]
    if valid:
        worst = min(valid, key=lambda x: x["taxa"])
        insight_2 = {
            "title": "Classe Mais Difícil",
            "value": f"Classe {int(worst['classe'])}: {worst['taxa']}%",
            "detail": f"Menor taxa de aprovação · N={int(worst['n']):,}".replace(",", "."),
            "tone": "negative",
        }
    else:
        insight_2 = {
            "title": "Classes", "value": "—", "detail": "Sem dados", "tone": "neutral",
        }

    # Insight 3: Worst regional (most rigorous)
    regional_stats = _safe("""
        SELECT
            REPLACE(regional, 'Unidade Regional de Regularização Ambiental ', '') AS reg,
            COUNT(*) AS n,
            ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1) AS taxa
        FROM v_mg_semad WHERE atividade LIKE 'A-0%'
        GROUP BY regional HAVING COUNT(*) >= 50
        ORDER BY taxa ASC LIMIT 1
    """)
    if regional_stats:
        r = regional_stats[0]
        insight_3 = {
            "title": "Regional Mais Rigorosa",
            "value": f"{r['reg']}: {r['taxa']}%",
            "detail": f"Regional com menor taxa · N={int(r['n']):,}".replace(",", "."),
            "tone": "negative",
        }
    else:
        insight_3 = {
            "title": "Regionais", "value": "—", "detail": "Sem dados", "tone": "neutral",
        }

    # Insight 4: Companies with 6+ infractions
    inf = _safe("""
        WITH ei AS (
            SELECT REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g') AS cnpj,
                COUNT(*) AS n_inf
            FROM v_ibama_infracoes WHERE UF = 'MG'
            GROUP BY REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g')
            HAVING COUNT(*) >= 6
        )
        SELECT COUNT(*) AS n,
            ROUND(100.0 * SUM(CASE WHEN s.decisao = 'deferido' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 1) AS taxa
        FROM v_mg_semad s
        INNER JOIN ei ON s.cnpj_cpf = ei.cnpj
        WHERE s.atividade LIKE 'A-0%'
    """)
    if inf and inf[0].get("n", 0) > 0:
        i = inf[0]
        insight_4 = {
            "title": "Empresas com 6+ Infrações",
            "value": f"{i['taxa']}% aprovação",
            "detail": f"Empresas maiores navegam melhor o sistema · N={int(i['n']):,}".replace(",", "."),
            "tone": "neutral",
        }
    else:
        insight_4 = {
            "title": "Infrações", "value": "—", "detail": "Sem dados cruzados", "tone": "neutral",
        }

    return [insight_1, insight_2, insight_3, insight_4]


@router.get("/overview/metadata")
def get_metadata():
    """Retorna metadados de coleta de dados."""
    return load_metadata()


@router.get("/meta/freshness")
def get_freshness():
    """Retorna data mais recente de coleta entre todas as fontes."""
    metadata = load_metadata()
    dates = [
        str(v.get("last_collected", ""))[:10]
        for v in metadata.values()
        if v.get("last_collected")
    ]
    latest = max(dates) if dates else None
    return {"last_updated": latest}


@router.get("/meta/sources")
def get_source_metadata():
    """Retorna metadados de todas as fontes com contagem e datas."""
    metadata = load_metadata()

    source_defs = [
        ("mg_semad", "MG SEMAD Decisões", "v_mg_semad",
         "https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca"),
        ("ibama_licencas", "IBAMA Licenças Federais", "v_ibama",
         "https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json"),
        ("anm_processos", "ANM SIGMINE Processos", "v_anm",
         "https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0"),
        ("ibama_infracoes", "IBAMA Infrações Ambientais", "v_ibama_infracoes",
         "https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao"),
        ("anm_cfem", "ANM CFEM Royalties", "v_cfem",
         "https://app.anm.gov.br/dadosabertos/ARRECADACAO/"),
        ("anm_ral", "ANM RAL Produção", "v_ral",
         "https://app.anm.gov.br/dadosabertos/AMB/"),
        ("receita_federal_cnpj", "Receita Federal CNPJ", "v_cnpj_empresas",
         "https://brasilapi.com.br/api/cnpj/v1/"),
        ("copam_cmi", "COPAM CMI Reuniões", "v_copam_deliberacoes",
         "https://sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam/index-externo"),
        ("icmbio_ucs", "ICMBio Unidades Conservação", "v_ucs",
         "https://www.gov.br/icmbio/pt-br/assuntos/dados_geoespaciais/"),
        ("funai_tis", "FUNAI Terras Indígenas", "v_tis",
         "https://geoserver.funai.gov.br/geoserver/Funai/ows"),
        ("ibge_biomas", "IBGE Biomas", "v_biomas",
         "http://geoftp.ibge.gov.br/informacoes_ambientais/"),
        ("spatial_overlaps", "Sobreposições Espaciais", "v_spatial_overlaps", ""),
        ("anm_scm", "ANM SCM Concessões", "v_scm",
         "https://app.anm.gov.br/dadosabertos/SCM/"),
        ("concessoes_mg", "Concessões MG Consolidadas", "v_concessoes", ""),
        ("bcb_ptax", "BCB PTAX Câmbio USD/BRL", "v_bcb_cotacoes",
         "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"),
        ("comex_stat", "Comex Stat Comércio Exterior", "v_comex_mineracao",
         "https://api-comexstat.mdic.gov.br/"),
    ]

    results = []
    for key, name, view, url in source_defs:
        meta = metadata.get(key, {})
        records = meta.get("records")
        last_collected = str(meta.get("last_collected", ""))[:10] or None

        # Fallback: count from view
        if not records:
            try:
                r = run_query(f"SELECT COUNT(*) AS n FROM {view}")
                records = r[0]["n"] if r else None
            except Exception:
                records = None

        results.append({
            "key": key,
            "name": name,
            "records": records,
            "last_collected": last_collected if last_collected else None,
            "url": url or None,
        })

    return results
