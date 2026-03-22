"""Consultas analíticas pré-definidas para o DuckDB.

Todas as consultas operam sobre views criadas pelo loader.
Consultas cross-source usam CNPJ como chave de ligação.
"""

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

# ============================================================
# CROSS-SOURCE QUERIES (CNPJ bridge)
# ============================================================

# Empresas com infrações IBAMA vs taxa de aprovação MG
QUERY_INFRACOES_VS_APROVACAO = """
WITH empresa_infracoes AS (
    SELECT
        REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g') AS cnpj,
        COUNT(*) AS total_infracoes,
        COUNT(DISTINCT EXTRACT(YEAR FROM
            TRY_CAST(DAT_HORA_AUTO_INFRACAO AS TIMESTAMP)
        )) AS anos_com_infracao
    FROM v_ibama_infracoes
    WHERE UF = 'MG'
    GROUP BY CPF_CNPJ_INFRATOR
),
decisoes_mining AS (
    SELECT
        cnpj_cpf,
        decisao,
        atividade,
        classe
    FROM v_mg_semad
    WHERE atividade LIKE 'A-0%'
      AND LENGTH(cnpj_cpf) = 14
)
SELECT
    CASE
        WHEN ei.cnpj IS NOT NULL THEN 'Com infrações IBAMA'
        ELSE 'Sem infrações IBAMA'
    END AS perfil_empresa,
    COUNT(*) AS total_decisoes,
    SUM(CASE WHEN dm.decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
    SUM(CASE WHEN dm.decisao = 'indeferido' THEN 1 ELSE 0 END) AS indeferidos,
    ROUND(
        100.0 * SUM(CASE WHEN dm.decisao = 'deferido' THEN 1 ELSE 0 END)
        / COUNT(*), 1
    ) AS taxa_aprovacao
FROM decisoes_mining dm
LEFT JOIN empresa_infracoes ei ON dm.cnpj_cpf = ei.cnpj
GROUP BY perfil_empresa
ORDER BY perfil_empresa
"""

# CFEM: empresas que pagam royalties vs taxa de aprovação
QUERY_CFEM_VS_APROVACAO = """
WITH empresa_cfem AS (
    SELECT
        CPF_CNPJ AS cnpj,
        COUNT(*) AS meses_pagamento,
        SUM(TRY_CAST(
            REPLACE(REPLACE(ValorRecolhido, '.', ''), ',', '.') AS DOUBLE
        )) AS total_pago
    FROM v_cfem
    GROUP BY CPF_CNPJ
),
decisoes_mining AS (
    SELECT
        cnpj_cpf,
        decisao
    FROM v_mg_semad
    WHERE atividade LIKE 'A-0%'
      AND LENGTH(cnpj_cpf) = 14
)
SELECT
    CASE
        WHEN ec.cnpj IS NOT NULL THEN 'Paga CFEM'
        ELSE 'Não paga CFEM'
    END AS perfil_empresa,
    COUNT(*) AS total_decisoes,
    SUM(CASE WHEN dm.decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
    SUM(CASE WHEN dm.decisao = 'indeferido' THEN 1 ELSE 0 END) AS indeferidos,
    ROUND(
        100.0 * SUM(CASE WHEN dm.decisao = 'deferido' THEN 1 ELSE 0 END)
        / COUNT(*), 1
    ) AS taxa_aprovacao
FROM decisoes_mining dm
LEFT JOIN empresa_cfem ec ON dm.cnpj_cpf = ec.cnpj
GROUP BY perfil_empresa
ORDER BY perfil_empresa
"""

# Resumo completo cross-source por empresa
QUERY_EMPRESA_PROFILE = """
WITH empresa_infracoes AS (
    SELECT
        REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g') AS cnpj,
        COUNT(*) AS total_infracoes
    FROM v_ibama_infracoes
    WHERE UF = 'MG'
    GROUP BY CPF_CNPJ_INFRATOR
),
empresa_cfem AS (
    SELECT
        CPF_CNPJ AS cnpj,
        COUNT(*) AS meses_pagamento,
        SUM(TRY_CAST(
            REPLACE(REPLACE(ValorRecolhido, '.', ''), ',', '.') AS DOUBLE
        )) AS total_pago
    FROM v_cfem
    GROUP BY CPF_CNPJ
),
empresa_decisoes AS (
    SELECT
        cnpj_cpf,
        COUNT(*) AS total_decisoes,
        SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
        SUM(CASE WHEN decisao = 'indeferido' THEN 1 ELSE 0 END) AS indeferidos
    FROM v_mg_semad
    WHERE atividade LIKE 'A-0%'
      AND LENGTH(cnpj_cpf) = 14
    GROUP BY cnpj_cpf
)
SELECT
    ed.cnpj_cpf AS cnpj,
    ed.total_decisoes,
    ed.deferidos,
    ed.indeferidos,
    ROUND(100.0 * ed.deferidos / ed.total_decisoes, 1) AS taxa_aprovacao,
    COALESCE(ei.total_infracoes, 0) AS infracoes_ibama,
    COALESCE(ec.meses_pagamento, 0) AS meses_cfem,
    ROUND(COALESCE(ec.total_pago, 0), 2) AS total_cfem_pago
FROM empresa_decisoes ed
LEFT JOIN empresa_infracoes ei ON ed.cnpj_cpf = ei.cnpj
LEFT JOIN empresa_cfem ec ON ed.cnpj_cpf = ec.cnpj
ORDER BY ed.total_decisoes DESC
LIMIT 50
"""
