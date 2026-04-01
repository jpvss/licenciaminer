"""Endpoints de Due Diligence ambiental."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.components.dd_inventory import (
    LICENCA_DESC,
    LICENCA_TIPOS,
    filtrar_documentos,
    filtrar_requisitos,
    load_inventario,
    load_requisitos,
)
from app.components.dd_scoring import (
    CONFORMIDADE_ESCALA,
    calcular_checklist_completude,
    calcular_conformidade,
    gerar_recomendacoes,
)

router = APIRouter()


@router.get("/due-diligence/license-types")
def list_license_types():
    """Lista tipos de licença disponíveis com descrições."""
    return [
        {"code": code, "description": LICENCA_DESC.get(code, code)}
        for code in LICENCA_TIPOS
    ]


@router.get("/due-diligence/scale")
def get_conformidade_scale():
    """Retorna escala de conformidade (labels, cores, faixas)."""
    return CONFORMIDADE_ESCALA


@router.get("/due-diligence/documents")
def get_documents(
    licenca_tipo: str = Query(..., description="Tipo de licença (LAS, LAS-RAS, LAC1, etc.)"),
):
    """Retorna documentos aplicáveis para um tipo de licença."""
    docs = filtrar_documentos(licenca_tipo)
    return {
        "licenca_tipo": licenca_tipo,
        "total": len(docs),
        "documents": docs,
    }


@router.get("/due-diligence/requirements")
def get_requirements(
    documento: str = Query(..., description="Nome do documento"),
):
    """Retorna requisitos de teste para um documento específico."""
    reqs = filtrar_requisitos(documento)
    return {
        "documento": documento,
        "total": len(reqs),
        "requirements": reqs,
    }


class ScoreRequest(BaseModel):
    """Payload para cálculo de conformidade."""
    avaliacoes: dict[str, str]
    pesos: dict[str, float] | None = None
    doc_status: dict[str, str] | None = None


@router.post("/due-diligence/score")
def calculate_score(request: ScoreRequest):
    """Calcula score de conformidade a partir das avaliações.

    Aceita avaliações (requisito_id → "Atende" | "Atende Parcialmente" | "Não Atende" | "Não Aplica")
    e opcionalmente pesos e status de documentos.
    """
    resultado = calcular_conformidade(request.avaliacoes, request.pesos)

    response = {
        "total_requisitos": resultado.total_requisitos,
        "requisitos_aplicaveis": resultado.requisitos_aplicaveis,
        "atende": resultado.atende,
        "atende_parcial": resultado.atende_parcial,
        "nao_atende": resultado.nao_atende,
        "nao_aplica": resultado.nao_aplica,
        "conformidade_nao_ponderada": resultado.conformidade_nao_ponderada,
        "conformidade_ponderada": resultado.conformidade_ponderada,
        "nota_maxima": resultado.nota_maxima,
        "nota_obtida": resultado.nota_obtida,
        "classificacao": resultado.classificacao,
        "cor": resultado.cor,
        "descricao": resultado.descricao,
    }

    # Checklist de documentos (se fornecido)
    if request.doc_status:
        response["checklist"] = calcular_checklist_completude(request.doc_status)

    # Recomendações
    all_reqs = load_requisitos()
    response["recomendacoes"] = gerar_recomendacoes(request.avaliacoes, all_reqs)

    return response
