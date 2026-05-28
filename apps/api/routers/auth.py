from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
import re
from typing import Dict, Any
from services.local_db import (
    create_user,
    get_user_by_email,
    verify_password,
    get_user_dashboard_stats
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Developer Authentication"])

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class SignUpRequest(BaseModel):
    email: str = Field(..., description="Developer company email address")
    password: str = Field(..., min_length=6, description="Developer account password (min 6 characters)")

class LoginRequest(BaseModel):
    email: str = Field(..., description="Developer account email address")
    password: str = Field(..., description="Developer account password")

class UserProfileResponse(BaseModel):
    id: str
    email: str
    plan: str

class AuthSuccessResponse(BaseModel):
    success: bool
    message: str
    token: str
    user: UserProfileResponse

# ==========================================
# ENDPOINTS
# ==========================================

@router.post("/signup", response_model=AuthSuccessResponse, status_code=status.HTTP_201_CREATED)
async def signup_endpoint(req: SignUpRequest):
    """
    Registers a new developer account and stores their credentials in the database.
    Prevents duplicate entries and automatically issues an authentication session token.
    """
    email = req.email.strip().lower()
    
    # Validate email format
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format. Please provide a valid email."
        )
    
    # 1. Prevent duplicate email entries
    existing_user = get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate entry: Account with this email already exists."
        )
        
    # 2. Store credentials in database (SQLite fallback)
    new_user = create_user(email, req.password)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user in database. Please try again."
        )
        
    # 3. Create a unique session token mapping to the user ID
    session_token = f"pp_session_{new_user['id']}"
    
    return AuthSuccessResponse(
        success=True,
        message="Developer account created successfully.",
        token=session_token,
        user=UserProfileResponse(
            id=new_user["id"],
            email=new_user["email"],
            plan=new_user["plan"]
        )
    )

@router.post("/login", response_model=AuthSuccessResponse)
async def login_endpoint(req: LoginRequest):
    """
    Authenticates a developer using their email and password.
    Returns a session token upon correct verification.
    """
    email = req.email.strip().lower()
    
    # Validate email format
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format. Please provide a valid email."
        )
    
    # 1. Fetch user from database
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
        
    # 2. Verify cryptographically hashed password
    is_valid = verify_password(req.password, user["salt"], user["password_hash"])
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
        
    # 3. Issue session token
    session_token = f"pp_session_{user['id']}"
    
    return AuthSuccessResponse(
        success=True,
        message="Authentication successful.",
        token=session_token,
        user=UserProfileResponse(
            id=user["id"],
            email=user["email"],
            plan=user["plan"]
        )
    )

@router.get("/me", response_model=UserProfileResponse)
async def me_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Returns current authenticated user details from session token lookup.
    """
    return UserProfileResponse(
        id=current_user["id"],
        email=current_user["email"],
        plan=current_user["plan"]
    )

@router.get("/dashboard-stats")
async def dashboard_stats_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Retrieves dynamic, database-backed dashboard metrics and compression logs
    for the specific authenticated developer.
    """
    user_id = current_user["id"]
    stats_data = get_user_dashboard_stats(user_id)
    return stats_data
