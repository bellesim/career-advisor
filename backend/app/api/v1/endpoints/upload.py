from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.upload import UploadResponse
from app.services.session_service import create_guest_session
from app.services.upload_service import store_jd_file, store_jd_text, store_jd_url, store_resume

router = APIRouter()


@router.post("/", response_model=UploadResponse, summary="Upload resume and job description")
async def upload_files(
    resume_file: UploadFile = File(..., description="Resume file (PDF or DOCX, max 10MB)"),
    jd_text: Optional[str] = Form(None, description="Job description as plain text"),
    jd_file: Optional[UploadFile] = File(None, description="Job description as file (PDF or DOCX)"),
    jd_url: Optional[str] = Form(None, description="Job description as URL"),
):
    has_jd_text = bool(jd_text and jd_text.strip())
    has_jd_file = bool(jd_file and jd_file.filename)
    has_jd_url = bool(jd_url and jd_url.strip())
    provided = sum([has_jd_text, has_jd_file, has_jd_url])

    if provided == 0:
        raise HTTPException(
            status_code=422,
            detail={
                "error_code": "MISSING_JD",
                "message": "Provide exactly one of: jd_text, jd_file, or jd_url",
            },
        )
    if provided > 1:
        raise HTTPException(
            status_code=422,
            detail={
                "error_code": "MULTIPLE_JD_SOURCES",
                "message": "Provide exactly one of: jd_text, jd_file, or jd_url",
            },
        )

    session = create_guest_session()
    session_id = session["id"]

    resume_id = await store_resume(session_id, resume_file)

    if has_jd_text:
        jd_id = await store_jd_text(session_id, jd_text)
    elif has_jd_file:
        jd_id = await store_jd_file(session_id, jd_file)
    else:
        jd_id = await store_jd_url(session_id, jd_url)

    return UploadResponse(session_id=session_id, resume_id=resume_id, jd_id=jd_id)
