from fastapi import APIRouter, HTTPException

from app.core.supabase_client import get_supabase_client
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.ai.analyzer import analyze

router = APIRouter()


def _get_parsed_text(table: str, record_id: str, label: str) -> str:
    try:
        client = get_supabase_client()
        result = client.table(table).select("parsed_data").eq("id", record_id).execute()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid {label} ID: {e}")
    if not result.data:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return (result.data[0].get("parsed_data") or {}).get("raw_text", "")


@router.post("/", response_model=AnalyzeResponse)
async def run_analysis(req: AnalyzeRequest):
    resume_text = _get_parsed_text("resumes", req.resume_id, "resume")
    jd_text = _get_parsed_text("job_descriptions", req.jd_id, "job description")

    answers = [a.model_dump() for a in req.answers] if req.answers else None

    try:
        result = analyze(resume_text, jd_text, answers)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {e}")

    try:
        client = get_supabase_client()
        report = client.table("reports").insert({
            "session_id": req.session_id,
            "resume_id": req.resume_id,
            "jd_id": req.jd_id,
            "candidate_name": result.get("candidate_name", "Unknown"),
            "target_role": result.get("target_role", "Unknown"),
            "overall_score": int(result.get("overall_score", 0)),
            "category_scores": result.get("category_scores", {}),
            "gaps": result.get("gaps", []),
            "strengths": result.get("strengths", []),
            "action_plan": result.get("action_plan", {}),
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save report: {e}")

    return AnalyzeResponse(report_id=report.data[0]["id"])
