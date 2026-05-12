from fastapi import APIRouter, HTTPException

from app.core.supabase_client import get_supabase_client
from app.schemas.analyze import QuestionsRequest, QuestionsResponse
from app.services.ai.analyzer import generate_questions

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


@router.post("/", response_model=QuestionsResponse)
async def get_questions(req: QuestionsRequest):
    resume_text = _get_parsed_text("resumes", req.resume_id, "resume")
    jd_text = _get_parsed_text("job_descriptions", req.jd_id, "job description")
    questions = generate_questions(resume_text, jd_text)
    return QuestionsResponse(questions=questions)
