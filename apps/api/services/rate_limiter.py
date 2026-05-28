import time
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Plan Limits Configuration
PLAN_LIMITS = {
    "free": {"requests_per_day": 50, "tokens_per_request": 4000},
    "pro": {"requests_per_day": 5000, "tokens_per_request": 32000},
    "enterprise": {"requests_per_day": -1, "tokens_per_request": -1}  # -1 indicates unlimited
}

# Local in-memory store (user_id -> {"timestamp": float, "count": int})
_usage_store = {}

def check_rate_limit(user_id: str, plan: str, prompt_tokens: int) -> None:
    """
    Checks rate limits based on user's active billing plan and prompt payload token size.
    Raises HTTPException (429 Too Many Requests) or (400 Bad Request) if limits are breached.
    """
    plan_lower = plan.lower()
    if plan_lower not in PLAN_LIMITS:
        plan_lower = "free"
        
    limits = PLAN_LIMITS[plan_lower]
    
    # 1. Payload size check
    token_limit = limits["tokens_per_request"]
    if token_limit != -1 and prompt_tokens > token_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Prompt size ({prompt_tokens} tokens) exceeds your plan's maximum allowed tokens "
                f"per request ({token_limit} tokens). Upgrade to Pro or Enterprise for higher limits."
            )
        )
        
    # 2. Daily Request limit check
    req_limit = limits["requests_per_day"]
    if req_limit == -1:
        # Enterprise plan has unlimited requests
        return
        
    current_time = time.time()
    day_in_seconds = 86400
    
    if user_id not in _usage_store:
        _usage_store[user_id] = {
            "reset_time": current_time + day_in_seconds,
            "request_count": 0
        }
        
    user_usage = _usage_store[user_id]
    
    # Reset count if 24 hours have elapsed
    if current_time > user_usage["reset_time"]:
        user_usage["reset_time"] = current_time + day_in_seconds;
        user_usage["request_count"] = 0;
        
    if user_usage["request_count"] >= req_limit:
        time_left = int(user_usage["reset_time"] - current_time)
        hours_left = max(1, time_left // 3600)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Daily rate limit reached ({req_limit} requests/day). "
                f"Limits will reset in approximately {hours_left} hours. Upgrade to Pro for 5,000 reqs/day."
            )
        )
        
    # Increment request count
    user_usage["request_count"] += 1
    logger.info(f"[Rate Limiter] User {user_id} ({plan_lower}): {user_usage['request_count']}/{req_limit} requests today.")
