"""Consultas analíticas pré-definidas para o DuckDB."""

# MG: Taxa de aprovação por classe/atividade/regional/ano
QUERY_MG_APPROVAL_RATES = """
SELECT
    ano,
    classe,
    atividade,
    regional,
    COUNT(*) AS total,
    SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
    SUM(CASE WHEN decisao = 'indeferido' THEN 1 ELSE 0 END) AS indeferidos,
    ROUND(
        100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS taxa_aprovacao
FROM v_mg_semad
GROUP BY ano, classe, atividade, regional
ORDER BY ano DESC, classe
"""

# MG: Resumo geral de aprovação
QUERY_MG_SUMMARY = """
SELECT
    COUNT(*) AS total_decisoes,
    SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
    SUM(CASE WHEN decisao = 'indeferido' THEN 1 ELSE 0 END) AS indeferidos,
    SUM(CASE WHEN decisao = 'outro' THEN 1 ELSE 0 END) AS outros,
    ROUND(
        100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS taxa_aprovacao_geral
FROM v_mg_semad
"""

# IBAMA: Contagem por tipo de licença/ano
QUERY_IBAMA_BY_TYPE_YEAR = """
SELECT
    EXTRACT(YEAR FROM data_emissao) AS ano,
    tipo_licenca,
    COUNT(*) AS total
FROM v_ibama
GROUP BY ano, tipo_licenca
ORDER BY ano DESC, total DESC
"""

# IBAMA: Resumo geral
QUERY_IBAMA_SUMMARY = """
SELECT
    COUNT(*) AS total_licencas,
    COUNT(DISTINCT tipo_licenca) AS tipos_distintos,
    MIN(data_emissao) AS data_mais_antiga,
    MAX(data_emissao) AS data_mais_recente
FROM v_ibama
"""

# ANM: Distribuição por fase/UF
QUERY_ANM_BY_FASE_UF = """
SELECT
    UF,
    FASE,
    COUNT(*) AS total,
    ROUND(SUM(AREA_HA), 1) AS area_total_ha
FROM v_anm
GROUP BY UF, FASE
ORDER BY UF, total DESC
"""

# ANM: Resumo geral
QUERY_ANM_SUMMARY = """
SELECT
    COUNT(*) AS total_processos,
    COUNT(DISTINCT UF) AS ufs_distintas,
    COUNT(DISTINCT FASE) AS fases_distintas,
    ROUND(SUM(AREA_HA), 1) AS area_total_ha
FROM v_anm
"""
