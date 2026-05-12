from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    session_id: str = Field(..., description="Created session ID")
    resume_id: str = Field(..., description="Stored resume record ID")
    jd_id: str = Field(..., description="Stored job description record ID")
