from fastapi import APIRouter, HTTPException

from app.core.supabase_client import get_supabase_client

router = APIRouter()


@router.get("/{report_id}")
async def get_report(report_id: str):
    client = get_supabase_client()
    result = client.table("reports").select("*").eq("id", report_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found")
    return result.data[0]
