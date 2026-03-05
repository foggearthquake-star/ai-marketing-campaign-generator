"""Analysis endpoints."""

import ast
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse

router = APIRouter(prefix="/analyses", tags=["analyses"])


def normalize_value(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            try:
                return ast.literal_eval(value)
            except Exception:
                return value
    return value


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db_session)) -> AnalysisResponse:
    """Return analysis details by ID."""
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    structured = analysis.structured_output
    if isinstance(structured, str):
        try:
            structured = json.loads(structured)
        except Exception:
            structured = None
    if isinstance(structured, dict):
        for key, value in structured.items():
            structured[key] = normalize_value(value)

    print("Returning analysis:", analysis.id)
    print("Analysis status:", analysis.status)

    analysis_dict = {
        "id": analysis.id,
        "project_id": analysis.project_id,
        "status": analysis.status,
        "structured_output": structured,
        "error_message": analysis.error_message,
        "model": analysis.model,
        "prompt_tokens": analysis.prompt_tokens,
        "completion_tokens": analysis.completion_tokens,
        "total_tokens": analysis.total_tokens,
        "cost": analysis.cost,
        "created_at": analysis.created_at,
        "updated_at": analysis.updated_at,
    }
    return analysis_dict
