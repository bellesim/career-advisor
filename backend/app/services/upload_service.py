import uuid
from typing import Optional

from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.supabase_client import get_supabase_client
from app.services.parsing.resume_parser import parse_resume
from app.services.parsing.jd_parser import parse_jd_text, parse_jd_file, parse_jd_url

ALLOWED_EXTENSIONS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


async def _read_and_validate(file: UploadFile) -> tuple[bytes, str]:
    ext = _extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail={
                "error_code": "INVALID_FILE_FORMAT",
                "message": f"Unsupported format '.{ext}'. Allowed: PDF, DOCX",
            },
        )
    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=422,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "message": f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
            },
        )
    return content, ext


async def store_resume(session_id: str, file: UploadFile) -> str:
    content, ext = await _read_and_validate(file)
    client = get_supabase_client()
    resume_id = str(uuid.uuid4())
    file_path = f"{session_id}/resume_{resume_id}.{ext}"

    client.storage.from_("resumes").upload(
        file_path,
        content,
        {"content-type": ALLOWED_EXTENSIONS[ext]},
    )

    parsed = parse_resume(content, ext)

    result = client.table("resumes").insert({
        "id": resume_id,
        "session_id": session_id,
        "file_path": file_path,
        "parsed_data": parsed,
    }).execute()
    return result.data[0]["id"]


async def store_jd_text(session_id: str, text: str) -> str:
    client = get_supabase_client()
    parsed = parse_jd_text(text)
    result = client.table("job_descriptions").insert({
        "session_id": session_id,
        "source_type": "text",
        "source_content": text,
        "parsed_data": parsed,
    }).execute()
    return result.data[0]["id"]


async def store_jd_file(session_id: str, file: UploadFile) -> str:
    content, ext = await _read_and_validate(file)
    client = get_supabase_client()
    jd_id = str(uuid.uuid4())
    file_path = f"{session_id}/jd_{jd_id}.{ext}"

    client.storage.from_("resumes").upload(
        file_path,
        content,
        {"content-type": ALLOWED_EXTENSIONS[ext]},
    )

    parsed = parse_jd_file(content, ext)

    result = client.table("job_descriptions").insert({
        "id": jd_id,
        "session_id": session_id,
        "source_type": "file",
        "source_content": file_path,
        "parsed_data": parsed,
    }).execute()
    return result.data[0]["id"]


async def store_jd_url(session_id: str, url: str) -> str:
    client = get_supabase_client()
    parsed = parse_jd_url(url)
    result = client.table("job_descriptions").insert({
        "session_id": session_id,
        "source_type": "url",
        "source_content": url,
        "parsed_data": parsed,
    }).execute()
    return result.data[0]["id"]
