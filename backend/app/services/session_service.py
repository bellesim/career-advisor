from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings
from app.core.supabase_client import get_supabase_client


def create_guest_session() -> dict:
    client = get_supabase_client()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.GUEST_SESSION_EXPIRY_HOURS)
    result = client.table("sessions").insert({
        "is_guest": True,
        "expires_at": expires_at.isoformat(),
    }).execute()
    return result.data[0]


def create_auth_session(user_id: str) -> dict:
    client = get_supabase_client()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.AUTH_SESSION_EXPIRY_DAYS)
    result = client.table("sessions").insert({
        "user_id": user_id,
        "is_guest": False,
        "expires_at": expires_at.isoformat(),
    }).execute()
    return result.data[0]


def validate_session(session_id: str) -> Optional[dict]:
    client = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    result = (
        client.table("sessions")
        .select("*")
        .eq("id", session_id)
        .gt("expires_at", now)
        .execute()
    )
    return result.data[0] if result.data else None


def cleanup_expired_sessions() -> int:
    client = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    result = (
        client.table("sessions")
        .delete()
        .eq("is_guest", True)
        .lt("expires_at", now)
        .execute()
    )
    return len(result.data) if result.data else 0
