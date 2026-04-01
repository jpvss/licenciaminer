"""Due Diligence — Motor de scoring de conformidade.

Calcula scores de conformidade ponderados e não ponderados
com base nas avaliações do usuário, seguindo a metodologia
do modelo Excel (Summo Quartile).
"""

from dataclasses import dataclass, field
from typing import Any

# ── Escala de conformidade ──
CONFORMIDADE_ESCALA = [
    {
        "min": 0.90, "max": 1.00, "label": "Alta aderência",
        "cor": "#5BA77D", "descricao": "Processo em conformidade com a legislação",
    },
    {
        "min": 0.80, "max": 0.90, "label": "Sob controle",
        "cor": "#8BB85C", "descricao": "Processo pode melhorar em pontos específicos",
    },
    {
        "min": 0.65, "max": 0.80, "label": "Melhorias pontuais",
        "cor": "#D4A847", "descricao": "Requer ajustes em áreas identificadas",
    },
    {
        "min": 0.50, "max": 0.65, "label": "Melhorias significativas",
        "cor": "#C17F59", "descricao": "Requer atenção imediata em múltiplas áreas",
    },
    {
        "min": 0.00, "max": 0.50, "label": "Não conforme",
        "cor": "#C45B52", "descricao": "Ações imediatas necessárias para regularização",
    },
]

# Valores possíveis para avaliação de requisitos
AVALIACOES = {
    "Atende": 1.0,
    "Atende Parcialmente": 0.5,
    "Não Atende": 0.0,
    "Não Aplica": None,  # Excluído do cálculo
}

# Status de documentos
DOC_STATUS = ["Apresentado", "Não Apresentado", "Parcial"]


@dataclass
class ResultadoConformidade:
    """Resultado do cálculo de conformidade."""

    total_requisitos: int = 0
    requisitos_aplicaveis: int = 0
    atende: int = 0
    atende_parcial: int = 0
    nao_atende: int = 0
    nao_aplica: int = 0

    # Scores
    conformidade_nao_ponderada: float = 0.0
    conformidade_ponderada: float = 0.0
    nota_maxima: float = 0.0
    nota_obtida: float = 0.0
    nota_maxima_ponderada: float = 0.0
    nota_obtida_ponderada: float = 0.0

    # Classificação
    classificacao: str = ""
    cor: str = ""
    descricao: str = ""

    # Por documento
    por_documento: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Recomendações
    recomendacoes: list[dict[str, str]] = field(default_factory=list)


def classificar_conformidade(score: float) -> dict[str, str]:
    """Classifica um score de conformidade na escala definida."""
    for faixa in CONFORMIDADE_ESCALA:
        if faixa["min"] <= score <= faixa["max"]:
            return {"label": faixa["label"], "cor": faixa["cor"], "descricao": faixa["descricao"]}
    return CONFORMIDADE_ESCALA[-1]


def calcular_conformidade(
    avaliacoes: dict[str, str],
    pesos: dict[str, float] | None = None,
) -> ResultadoConformidade:
    """Calcula score de conformidade a partir das avaliações.

    Args:
        avaliacoes: Dict {requisito_id: avaliação} onde avaliação é
                    "Atende", "Atende Parcialmente", "Não Atende" ou "Não Aplica".
        pesos: Dict opcional {requisito_id: peso} para cálculo ponderado.

    Returns:
        ResultadoConformidade com scores e classificação.
    """
    result = ResultadoConformidade()
    result.total_requisitos = len(avaliacoes)

    nota_sum = 0.0
    nota_max = 0.0
    nota_pond_sum = 0.0
    nota_pond_max = 0.0

    for req_id, avaliacao in avaliacoes.items():
        valor = AVALIACOES.get(avaliacao)
        peso = pesos.get(req_id, 1.0) if pesos else 1.0

        if valor is None:  # Não Aplica
            result.nao_aplica += 1
            continue

        result.requisitos_aplicaveis += 1
        nota_max += 1.0
        nota_pond_max += peso

        if avaliacao == "Atende":
            result.atende += 1
            nota_sum += 1.0
            nota_pond_sum += peso
        elif avaliacao == "Atende Parcialmente":
            result.atende_parcial += 1
            nota_sum += 0.5
            nota_pond_sum += peso * 0.5
        else:  # Não Atende
            result.nao_atende += 1

    # Scores
    result.nota_maxima = nota_max
    result.nota_obtida = nota_sum
    result.nota_maxima_ponderada = nota_pond_max
    result.nota_obtida_ponderada = nota_pond_sum

    if nota_max > 0:
        result.conformidade_nao_ponderada = nota_sum / nota_max
    if nota_pond_max > 0:
        result.conformidade_ponderada = nota_pond_sum / nota_pond_max

    # Classificação (usa score não ponderado como principal)
    cls = classificar_conformidade(result.conformidade_nao_ponderada)
    result.classificacao = cls["label"]
    result.cor = cls["cor"]
    result.descricao = cls["descricao"]

    return result


def calcular_conformidade_por_documento(
    avaliacoes_por_doc: dict[str, dict[str, str]],
) -> dict[str, ResultadoConformidade]:
    """Calcula conformidade agrupada por documento.

    Args:
        avaliacoes_por_doc: Dict {documento: {requisito_id: avaliação}}.

    Returns:
        Dict {documento: ResultadoConformidade}.
    """
    return {
        doc: calcular_conformidade(avals)
        for doc, avals in avaliacoes_por_doc.items()
    }


def gerar_recomendacoes(
    avaliacoes: dict[str, str],
    requisitos: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Gera recomendações a partir de requisitos não atendidos.

    Args:
        avaliacoes: Dict {requisito_id: avaliação}.
        requisitos: Lista de requisitos de referência.

    Returns:
        Lista de recomendações com tipo, descrição e prioridade.
    """
    req_map = {r["requisito_id"]: r for r in requisitos}
    recomendacoes = []

    for req_id, avaliacao in avaliacoes.items():
        if avaliacao in ("Não Atende", "Atende Parcialmente"):
            req = req_map.get(req_id, {})
            tipo = "Procedimento inconforme" if avaliacao == "Não Atende" else "Ponto de atenção"
            prioridade = "Alta" if avaliacao == "Não Atende" else "Média"

            recomendacoes.append({
                "requisito_id": req_id,
                "tipo": tipo,
                "prioridade": prioridade,
                "documento": req.get("documento", ""),
                "topico": req.get("topico", ""),
                "teste": req.get("teste_aderencia", ""),
                "evidencia": req.get("evidencia_esperada", ""),
            })

    # Ordenar: Alta primeiro, depois Média
    recomendacoes.sort(key=lambda r: (0 if r["prioridade"] == "Alta" else 1, r["requisito_id"]))
    return recomendacoes


def calcular_checklist_completude(
    status_docs: dict[str, str],
) -> dict[str, Any]:
    """Calcula completude do checklist de documentos.

    Args:
        status_docs: Dict {documento: status} onde status é
                     "Apresentado", "Não Apresentado" ou "Parcial".

    Returns:
        Dict com total, apresentados, faltantes, percentual.
    """
    total = len(status_docs)
    apresentados = sum(1 for s in status_docs.values() if s == "Apresentado")
    parciais = sum(1 for s in status_docs.values() if s == "Parcial")
    faltantes = sum(1 for s in status_docs.values() if s == "Não Apresentado")

    return {
        "total": total,
        "apresentados": apresentados,
        "parciais": parciais,
        "faltantes": faltantes,
        "percentual": apresentados / total if total > 0 else 0.0,
        "percentual_com_parciais": (apresentados + parciais * 0.5) / total if total > 0 else 0.0,
    }
