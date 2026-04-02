"""Endpoint de chat com LLM via Anthropic SDK (streaming SSE)."""

import os
import logging

import anthropic
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.services.database import run_query, safe_query

logger = logging.getLogger(__name__)

router = APIRouter()

SYSTEM_PROMPT = """Você é o assistente de inteligência ambiental do Summo Quartile.
Seu papel é ajudar consultores ambientais a interpretar dados de licenciamento minerário em Minas Gerais.

Fontes de dados disponíveis:
- SEMAD MG: decisões de licenciamento ambiental (deferidos, indeferidos, arquivamentos)
- IBAMA SISLIC: licenças ambientais federais emitidas
- ANM (SIGMINE): títulos minerários, concessões, alvarás
- CFEM: royalties minerários pagos
- COPAM: reuniões do conselho de política ambiental

Diretrizes:
- Responda sempre em português brasileiro
- Cite fontes de dados quando relevante
- Se não souber a resposta, diga claramente
- Forneça contexto regulatório quando aplicável (DN COPAM 217/2017, etc.)
- Use números formatados no padrão brasileiro (1.234,56)
"""


class ChatRequest(BaseModel):
    """Payload de requisição de chat."""
    messages: list[dict[str, str]]


def _get_db_context() -> str:
    """Coleta contexto resumido do banco para enriquecer respostas."""
    try:
        stats = run_query(
            "SELECT COUNT(*) as total FROM v_mg_semad"
        )
        total = stats[0]["total"] if stats else 0
        return f"\n[Contexto: banco contém {total:,} decisões de licenciamento MG]"
    except Exception:
        return ""


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming de chat com Claude via SSE."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY não configurada",
        )

    system = SYSTEM_PROMPT + _get_db_context()

    # Validate messages
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages vazio")

    client = anthropic.Anthropic(api_key=api_key)

    def generate():
        try:
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=system,
                messages=request.messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {text}\n\n"
            yield "data: [DONE]\n\n"
        except anthropic.APIError as e:
            logger.error("Anthropic API error: %s", e)
            yield f"data: [ERROR] {e.message}\n\n"
        except Exception as e:
            logger.error("Chat stream error: %s", e)
            yield f"data: [ERROR] Erro interno\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
