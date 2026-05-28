import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase_client: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase database client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase database client: {e}")

def log_compression(
    user_id: str,
    original_tokens: int,
    compressed_tokens: int,
    model: str,
    savings_percent: float
) -> dict:
    """
    Logs compression metrics in Supabase.
    If database connection is offline, falls back to printing metrics to logs.
    """
    if not supabase_client:
        tokens_saved = original_tokens - compressed_tokens
        logger.info(
            f"[OFFLINE METRICS LOG] User: {user_id} | Model: {model} | "
            f"Orig Tokens: {original_tokens} | Comp Tokens: {compressed_tokens} | "
            f"Saved: {tokens_saved} ({savings_percent}%)"
        )
        # Persistent local SQLite logging
        try:
            from services.local_db import log_local_compression
            logged = log_local_compression(
                user_id=user_id,
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                model=model,
                savings_percent=savings_percent
            )
            return {"logged": logged, "reason": "local_sqlite" if logged else "sqlite_error"}
        except Exception as e:
            logger.error(f"SQLite persistent logging failed: {e}")
            return {"logged": False, "reason": "offline_mode", "error": str(e)}

    try:
        data = {
            "user_id": user_id,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "model": model,
            "savings_percent": savings_percent
        }
        res = supabase_client.table("compressions").insert(data).execute()
        return {"logged": True, "data": res.data}
    except Exception as e:
        logger.error(f"Failed to write metrics to Supabase: {e}")
        return {"logged": False, "error": str(e)}
