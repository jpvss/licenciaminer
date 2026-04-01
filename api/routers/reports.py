"""Endpoints de geração de relatórios PDF."""

import logging
import time
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path
from fastapi.responses import Response

from api.services.database import fmt_reais, run_query
from licenciaminer.database.queries import (
    QUERY_CNPJ_ANM_TITULOS,
    QUERY_CNPJ_CFEM,
    QUERY_CNPJ_INFRACOES,
    QUERY_CNPJ_PROFILE,
    QUERY_HISTORICO_CNPJ,
    QUERY_INFRACOES_FAIXA_DECISAO,
    QUERY_MG_SUMMARY,
    QUERY_SPATIAL_VS_APROVACAO,
    query_approval_stats,
    query_similar_cases,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store para PDFs gerados com TTL (24h auto-cleanup)
_report_store: dict[str, dict] = {}
_REPORT_TTL_SECONDS = 86400  # 24 hours
_MAX_STORED_REPORTS = 50


def _cleanup_old_reports():
    """Remove relatórios com mais de 24h ou quando excede o limite."""
    now = time.time()
    expired = [
        k for k, v in _report_store.items()
        if now - v.get("created_at", 0) > _REPORT_TTL_SECONDS
    ]
    for k in expired:
        del _report_store[k]

    # Se ainda excede o limite, remove os mais antigos
    if len(_report_store) > _MAX_STORED_REPORTS:
        sorted_keys = sorted(
            _report_store.keys(),
            key=lambda k: _report_store[k].get("created_at", 0),
        )
        for k in sorted_keys[:len(_report_store) - _MAX_STORED_REPORTS]:
            del _report_store[k]


def _collect_report_data(cnpj: str) -> dict:
    """Coleta dados para relatório — versão sem dependência do Streamlit.

    Reimplementa app/components/report_data.py::collect_report_data()
    usando api.services.database em vez de app.components.data_loader.
    """
    data = {
        "cnpj": cnpj,
        "generated_at": datetime.now().isoformat(),
        "razao_social": cnpj,
        "cnae_fiscal": "",
        "cnae_descricao": "",
        "porte": "",
        "data_abertura": "",
        "situacao": "",
        "total_decisoes": 0,
        "deferidos": 0,
        "indeferidos": 0,
        "arquivamentos": 0,
        "taxa_aprovacao": 0.0,
        "total_infracoes": 0,
        "anos_com_infracao": 0,
        "cfem_meses_pagamento": 0,
        "cfem_total_pago": 0.0,
        "decisoes": [],
        "taxa_aprovacao_geral": 0.0,
        "total_decisoes_geral": 0,
        "casos_similares": [],
        "taxa_aprovacao_filtrada": 0.0,
        "total_filtrado": 0,
        "atividade_principal": "",
        "faixas_infracoes": [],
        "analise_espacial": [],
        "titulos_anm": [],
        "risk_level": "MODERADO",
        "findings": [],
    }

    # 1. Perfil
    try:
        profile = run_query(QUERY_CNPJ_PROFILE, [cnpj])
        if profile:
            p = profile[0]
            data["razao_social"] = p.get("razao_social") or cnpj
            data["cnae_fiscal"] = p.get("cnae_fiscal") or ""
            data["cnae_descricao"] = p.get("cnae_descricao") or ""
            data["porte"] = p.get("porte") or ""
            data["data_abertura"] = str(p.get("data_abertura", ""))
            data["situacao"] = p.get("situacao") or ""
            data["total_decisoes"] = p.get("total_decisoes", 0) or 0
            data["deferidos"] = p.get("deferidos", 0) or 0
            data["indeferidos"] = p.get("indeferidos", 0) or 0
            data["arquivamentos"] = p.get("arquivamentos", 0) or 0
            data["taxa_aprovacao"] = p.get("taxa_aprovacao", 0) or 0
    except Exception:
        logger.exception("Erro perfil CNPJ %s", cnpj)

    # 2. Infrações
    try:
        inf = run_query(QUERY_CNPJ_INFRACOES, [cnpj])
        if inf and inf[0].get("total_infracoes"):
            data["total_infracoes"] = inf[0]["total_infracoes"]
            data["anos_com_infracao"] = inf[0].get("anos_com_infracao", 0) or 0
    except Exception:
        logger.exception("Erro infrações CNPJ %s", cnpj)

    # 3. CFEM
    try:
        cfem = run_query(QUERY_CNPJ_CFEM, [cnpj])
        if cfem and cfem[0].get("meses_pagamento"):
            data["cfem_meses_pagamento"] = cfem[0]["meses_pagamento"]
            data["cfem_total_pago"] = cfem[0].get("total_pago", 0) or 0
    except Exception:
        logger.exception("Erro CFEM CNPJ %s", cnpj)

    # 4. Histórico
    try:
        data["decisoes"] = run_query(QUERY_HISTORICO_CNPJ, [cnpj]) or []
    except Exception:
        logger.exception("Erro histórico CNPJ %s", cnpj)

    # 5. Contexto geral
    try:
        summary = run_query(QUERY_MG_SUMMARY)
        if summary:
            data["taxa_aprovacao_geral"] = summary[0].get("taxa_aprovacao_geral", 0) or 0
            data["total_decisoes_geral"] = summary[0].get("total_decisoes", 0) or 0
    except Exception:
        logger.exception("Erro resumo geral")

    # 6. Aprovação filtrada
    if data["decisoes"]:
        atividades = [d.get("atividade", "") for d in data["decisoes"] if d.get("atividade")]
        if atividades:
            data["atividade_principal"] = max(set(atividades), key=atividades.count)
            prefix = data["atividade_principal"][:7]
            if len(prefix) >= 5:
                try:
                    q, p = query_approval_stats(prefix)
                    stats = run_query(q, p)
                    if stats and stats[0].get("total", 0) > 0:
                        data["taxa_aprovacao_filtrada"] = stats[0]["taxa_aprovacao"]
                        data["total_filtrado"] = stats[0]["total"]
                except Exception:
                    logger.exception("Erro stats filtradas")

    # 7. Casos similares
    if data["atividade_principal"]:
        prefix = data["atividade_principal"][:7]
        if len(prefix) >= 5:
            try:
                q, p = query_similar_cases(prefix, limit=5)
                data["casos_similares"] = run_query(q, p) or []
            except Exception:
                logger.exception("Erro casos similares")

    # 8. Faixas de infração
    try:
        data["faixas_infracoes"] = run_query(QUERY_INFRACOES_FAIXA_DECISAO) or []
    except Exception:
        logger.exception("Erro faixas infração")

    # 9. Espacial
    try:
        data["analise_espacial"] = run_query(QUERY_SPATIAL_VS_APROVACAO) or []
    except Exception:
        logger.exception("Erro análise espacial")

    # 10. Títulos ANM
    if data["razao_social"] and data["razao_social"] != cnpj:
        try:
            data["titulos_anm"] = run_query(QUERY_CNPJ_ANM_TITULOS, [data["razao_social"]]) or []
        except Exception:
            logger.exception("Erro títulos ANM")

    # Risco
    score = 0
    if data["total_infracoes"] >= 6:
        score += 3
    elif data["total_infracoes"] >= 3:
        score += 2
    elif data["total_infracoes"] >= 1:
        score += 1
    if data["taxa_aprovacao"] < 50:
        score += 3
    elif data["taxa_aprovacao"] < 70:
        score += 1
    if data["cfem_meses_pagamento"] == 0 and data["total_decisoes"] > 0:
        score += 1
    if data["indeferidos"] > data["deferidos"]:
        score += 2

    data["risk_level"] = "ALTO" if score >= 5 else ("MODERADO" if score >= 2 else "BAIXO")

    # Achados
    findings = []
    if data["total_infracoes"] >= 6:
        findings.append(
            f"Empresa possui {data['total_infracoes']} infrações IBAMA em "
            f"{data['anos_com_infracao']} anos — perfil de alto risco regulatório."
        )
    elif data["total_infracoes"] >= 1:
        findings.append(f"Registradas {data['total_infracoes']} infração(ões) IBAMA.")
    else:
        findings.append("Sem infrações IBAMA registradas — histórico limpo.")

    diff = data["taxa_aprovacao"] - data["taxa_aprovacao_geral"]
    if abs(diff) > 5:
        direction = "acima" if diff > 0 else "abaixo"
        findings.append(
            f"Taxa de aprovação ({data['taxa_aprovacao']:.0f}%) está "
            f"{abs(diff):.0f}pp {direction} da média estadual "
            f"({data['taxa_aprovacao_geral']:.0f}%)."
        )

    if data["cfem_total_pago"] > 0:
        findings.append(
            f"Pagamentos CFEM regulares: {fmt_reais(data['cfem_total_pago'])} "
            f"em {data['cfem_meses_pagamento']} meses."
        )
    elif data["total_decisoes"] > 0:
        findings.append("Sem pagamentos CFEM registrados no período analisado.")

    data["findings"] = findings[:5]

    return data


@router.get("/report/{cnpj}/data")
def get_report_data(
    cnpj: str = Path(..., min_length=11, max_length=14),
):
    """Retorna dados consolidados para relatório (sem gerar PDF).

    Útil para o frontend renderizar o relatório ou para prévia.
    """
    return _collect_report_data(cnpj)


@router.post("/report/{cnpj}/generate")
def generate_report(
    cnpj: str = Path(..., min_length=11, max_length=14),
    background_tasks: BackgroundTasks = None,
):
    """Inicia geração de relatório PDF em background.

    Retorna job_id para consultar status e baixar o PDF.
    """
    _cleanup_old_reports()
    job_id = str(uuid.uuid4())[:8]
    _report_store[job_id] = {"status": "generating", "cnpj": cnpj, "created_at": time.time()}

    def _generate(job_id: str, cnpj: str):
        try:
            from app.components.report_generator import generate_report_pdf
            from app.components.report_data import ReportData

            # Coletar dados
            raw = _collect_report_data(cnpj)

            # Converter para dataclass que o gerador espera
            report_data = ReportData(cnpj=cnpj)
            for key, value in raw.items():
                if hasattr(report_data, key) and key != "cnpj":
                    setattr(report_data, key, value)

            pdf_bytes = generate_report_pdf(report_data)

            _report_store[job_id] = {
                "status": "ready",
                "cnpj": cnpj,
                "pdf": pdf_bytes,
                "filename": f"relatorio_{cnpj}_{datetime.now():%Y%m%d}.pdf",
                "empresa": raw.get("razao_social", cnpj),
                "risk_level": raw.get("risk_level", "MODERADO"),
            }
        except Exception as e:
            logger.exception("Erro ao gerar PDF para %s", cnpj)
            _report_store[job_id] = {"status": "error", "cnpj": cnpj, "error": str(e)}

    background_tasks.add_task(_generate, job_id, cnpj)
    return {"job_id": job_id, "status": "generating"}


@router.get("/report/{job_id}/status")
def get_report_status(job_id: str):
    """Consulta status de geração do relatório."""
    job = _report_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    return {
        "job_id": job_id,
        "status": job["status"],
        "cnpj": job.get("cnpj"),
        "empresa": job.get("empresa"),
        "risk_level": job.get("risk_level"),
        "error": job.get("error"),
    }


@router.get("/report/{job_id}/download")
def download_report(job_id: str):
    """Download do PDF gerado."""
    job = _report_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    if job["status"] != "ready":
        raise HTTPException(status_code=409, detail=f"Relatório não pronto: {job['status']}")

    return Response(
        content=job["pdf"],
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{job["filename"]}"'},
    )


@router.post("/report/{cnpj}/download-sync")
def download_report_sync(
    cnpj: str = Path(..., min_length=11, max_length=14),
):
    """Gera e retorna PDF em uma única requisição (síncrono).

    Mais simples para o frontend: POST → blob → download.
    Timeout recomendado: 60s no cliente.
    """
    try:
        from app.components.report_generator import generate_report_pdf
        from app.components.report_data import ReportData

        raw = _collect_report_data(cnpj)

        report_data = ReportData(cnpj=cnpj)
        for key, value in raw.items():
            if hasattr(report_data, key) and key != "cnpj":
                setattr(report_data, key, value)

        pdf_bytes = generate_report_pdf(report_data)
        filename = f"relatorio_{cnpj}_{datetime.now():%Y%m%d}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception("Erro ao gerar PDF síncrono para %s", cnpj)
        raise HTTPException(status_code=500, detail=f"Erro na geração do relatório: {e}")
