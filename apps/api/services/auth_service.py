import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase_client: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    FastAPI dependency to authenticate requests using Supabase JWT or local SQLite session tokens.
    Extracts Bearer token and verifies it.
    """
    token = credentials.credentials
    
    # 1. Check if it's a local SQLite database session token
    if token.startswith("pp_session_"):
        user_id = token.replace("pp_session_", "")
        from services.local_db import get_user_by_id
        user = get_user_by_id(user_id)
        if user:
            return {
                "id": user["id"],
                "email": user["email"],
                "plan": user["plan"],
                "is_mock": False
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    if not supabase_client:
        # Development fallback mode for non-session tokens
        if token == "mock-dev-token" or token.startswith("pp_"):
            return {
                "id": "00000000-0000-0000-0000-000000000000",
                "email": "dev@promptpilot.ai",
                "plan": "pro",
                "is_mock": True
            }
        # Let developers pass any token locally if Supabase env vars are empty
        return {
            "id": "11111111-1111-1111-1111-111111111111",
            "email": "local-tester@promptpilot.ai",
            "plan": "free",
            "is_mock": True
        }
        
    try:
        # Validate JWT with Supabase Auth
        res = supabase_client.auth.get_user(token)
        if not res or not res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user = res.user
        # Standard Supabase user object format
        return {
            "id": user.id,
            "email": user.email,
            # Fallback plan metadata if not stored in a public table
            "plan": user.user_metadata.get("plan", "free") if user.user_metadata else "free",
            "is_mock": False
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
