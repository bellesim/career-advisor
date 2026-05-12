"""
Common Pydantic schemas for request/response validation.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    
    All API errors follow this structure for consistency.
    """
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Optional additional context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier for debugging")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_FILE_FORMAT",
                "message": "Unsupported file format. Supported formats: PDF, DOCX",
                "details": {"provided_format": "txt"},
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123"
            }
        }


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = Field(default=True, description="Operation success status")
    message: Optional[str] = Field(None, description="Optional success message")
    data: Optional[dict] = Field(None, description="Optional response data")
