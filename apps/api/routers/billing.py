from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/billing", tags=["Stripe Billing"])

class CheckoutRequest(BaseModel):
    plan: str = Field(..., description="Target tier plan to upgrade to: 'pro' or 'enterprise'")
    success_url: str = Field(..., description="Redirect URL upon successful subscription")
    cancel_url: str = Field(..., description="Redirect URL if customer cancels checkout")

class BillingResponse(BaseModel):
    url: str
    session_id: str

@router.post("/checkout", response_model=BillingResponse)
async def create_checkout_session(
    req: CheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a secure, customized Stripe Checkout Session URL.
    Enforces JWT authentication. Returns a mock Checkout landing URL.
    """
    plan_lower = req.plan.lower()
    if plan_lower not in ["pro", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid billing plan target. Must be 'pro' or 'enterprise'."
        )
        
    # Simulate Stripe API call - redirect user to a beautiful Stripe simulation receipt/checkout page
    session_id = f"cs_live_mock_{current_user['id'][:8]}_{plan_lower}"
    
    # We construct a highly-visual Stripe-styled checkout redirect URL
    mock_stripe_checkout_url = (
        f"https://checkout.stripe.dev/preview/promptpilot-{plan_lower}?"
        f"session_id={session_id}&"
        f"email={current_user['email']}&"
        f"success_url={req.success_url}&"
        f"cancel_url={req.cancel_url}"
    )
    
    return BillingResponse(
        url=mock_stripe_checkout_url,
        session_id=session_id
    )

@router.post("/portal", response_model=BillingResponse)
async def create_customer_portal(
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a mock Stripe Customer Billing Portal URL.
    Allows customers to manage cards, view invoices, and cancel tiers.
    """
    session_id = f"portal_mock_{current_user['id'][:8]}"
    mock_stripe_portal_url = (
        f"https://billing.stripe.com/p/session/{session_id}?"
        f"email={current_user['email']}"
    )
    
    return BillingResponse(
        url=mock_stripe_portal_url,
        session_id=session_id
    )
