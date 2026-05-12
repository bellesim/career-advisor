from fastapi import APIRouter

from app.api.v1.endpoints import upload, questions, analyze, report

api_router = APIRouter()

api_router.include_router(upload.router,    prefix="/upload",    tags=["upload"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(analyze.router,   prefix="/analyze",   tags=["analyze"])
api_router.include_router(report.router,    prefix="/report",    tags=["report"])


@api_router.get("/")
async def api_root():
    return {"message": "Career Advisor API v1"}
