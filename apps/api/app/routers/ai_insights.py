"""
AI Insights Router
==================
Mistral AI-powered insights and recommendations
EU AI Act compliant
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class RenovationStrategyRequest(BaseModel):
    """Request for AI-generated renovation strategy"""
    dpe_class: str = Field(..., pattern="^[A-G]$")
    surface_m2: float = Field(..., gt=0)
    budget_eur: float = Field(..., gt=0)
    is_rental: bool = False


@router.post("/renovation-strategy")
async def generate_renovation_strategy(request: RenovationStrategyRequest):
    """
    Generate AI-powered renovation strategy using Mistral AI

    ⚠️ EU AI Act Compliance: This endpoint uses AI.
    All recommendations include transparency badges.
    """
    return {
        "message": "Mistral AI integration - to be implemented",
        "request": request.dict(),
        "ai_transparency_badge": True,
        "human_verification_required": False,
        "status": "placeholder"
    }


@router.post("/explain-loi-climat-2026")
async def explain_loi_climat(user_question: str):
    """
    RAG-powered explanation of Loi Climat 2026 regulations

    Uses Retrieval-Augmented Generation with Mistral AI.
    """
    return {
        "question": user_question,
        "message": "RAG system - to be implemented",
        "status": "placeholder"
    }
