"""Stripe subscription models for ASL Biometric System."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status values."""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


class PricingPlan(BaseModel):
    """Pricing plan configuration."""
    
    id: str = Field(..., description="Plan identifier")
    name: str = Field(..., description="Plan display name")
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    price_monthly: float = Field(..., description="Monthly price in USD")
    price_yearly: float = Field(..., description="Yearly price in USD")
    stripe_price_id_monthly: Optional[str] = Field(None, description="Stripe price ID for monthly billing")
    stripe_price_id_yearly: Optional[str] = Field(None, description="Stripe price ID for yearly billing")
    features: List[str] = Field(default_factory=list, description="Included features")
    verifications_included: int = Field(..., description="Number of verifications included per month")
    overage_cost: float = Field(..., description="Cost per additional verification")
    use_cases: List[str] = Field(default_factory=list, description="Supported use cases")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "starter",
                "name": "Starter Plan",
                "tier": "starter",
                "price_monthly": 49.00,
                "price_yearly": 470.00,
                "features": [
                    "Up to 100 verifications/month",
                    "Telehealth verification",
                    "Remote work verification",
                    "Email support"
                ],
                "verifications_included": 100,
                "overage_cost": 0.75,
                "use_cases": ["healthcare", "business"]
            }
        }


class CustomerInfo(BaseModel):
    """Customer information for subscription."""
    
    email: str = Field(..., description="Customer email")
    name: str = Field(..., description="Customer or organization name")
    organization_type: Optional[str] = Field(None, description="Type of organization")
    tax_id: Optional[str] = Field(None, description="Tax ID for business customers")
    address: Optional[Dict[str, str]] = Field(None, description="Billing address")


class CreateCheckoutRequest(BaseModel):
    """Request to create a Stripe checkout session."""
    
    plan_id: str = Field(..., description="Plan identifier to subscribe to")
    billing_period: str = Field("monthly", description="Billing period (monthly/yearly)")
    customer_email: str = Field(..., description="Customer email address")
    success_url: str = Field(..., description="URL to redirect after successful payment")
    cancel_url: str = Field(..., description="URL to redirect after cancelled payment")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "professional",
                "billing_period": "monthly",
                "customer_email": "user@example.com",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel"
            }
        }


class CheckoutSessionResponse(BaseModel):
    """Response from checkout session creation."""
    
    session_id: str = Field(..., description="Stripe checkout session ID")
    url: str = Field(..., description="Checkout URL to redirect customer")
    expires_at: Optional[str] = Field(None, description="Session expiration timestamp")


class SubscriptionInfo(BaseModel):
    """Subscription information."""
    
    subscription_id: str = Field(..., description="Stripe subscription ID")
    customer_id: str = Field(..., description="Stripe customer ID")
    plan_id: str = Field(..., description="Plan identifier")
    status: SubscriptionStatus = Field(..., description="Subscription status")
    current_period_start: str = Field(..., description="Current period start date")
    current_period_end: str = Field(..., description="Current period end date")
    cancel_at_period_end: bool = Field(False, description="Whether subscription cancels at period end")
    verifications_used: int = Field(0, description="Verifications used this period")
    verifications_remaining: int = Field(..., description="Verifications remaining this period")


class UsageReport(BaseModel):
    """Usage report for subscription."""
    
    subscription_id: str = Field(..., description="Subscription ID")
    period_start: str = Field(..., description="Period start date")
    period_end: str = Field(..., description="Period end date")
    verifications_included: int = Field(..., description="Included verifications")
    verifications_used: int = Field(..., description="Verifications used")
    overage_count: int = Field(0, description="Overage verifications")
    overage_cost: float = Field(0.0, description="Total overage cost")
    breakdown_by_use_case: Dict[str, int] = Field(default_factory=dict, description="Usage by category")


class WebhookEvent(BaseModel):
    """Stripe webhook event model."""
    
    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    created: int = Field(..., description="Event creation timestamp")


class PortalSessionResponse(BaseModel):
    """Response for customer portal session."""
    
    url: str = Field(..., description="Customer portal URL")
    return_url: str = Field(..., description="Return URL after portal session")


# Define pricing plans
PRICING_PLANS = {
    "starter": PricingPlan(
        id="starter",
        name="Starter",
        tier=SubscriptionTier.STARTER,
        price_monthly=49.00,
        price_yearly=470.00,
        features=[
            "Up to 100 verifications/month",
            "Telehealth consent verification",
            "Remote work attendance tracking",
            "Basic analytics dashboard",
            "Email support",
            "API access"
        ],
        verifications_included=100,
        overage_cost=0.75,
        use_cases=["healthcare", "business"]
    ),
    "professional": PricingPlan(
        id="professional",
        name="Professional",
        tier=SubscriptionTier.PROFESSIONAL,
        price_monthly=199.00,
        price_yearly=1910.00,
        features=[
            "Up to 500 verifications/month",
            "All Starter features",
            "Pharmacy verification",
            "Court interpreter verification",
            "Exam proctoring",
            "Priority support",
            "Advanced analytics",
            "Webhooks & integrations",
            "Custom branding"
        ],
        verifications_included=500,
        overage_cost=0.50,
        use_cases=["healthcare", "business", "legal", "education"]
    ),
    "enterprise": PricingPlan(
        id="enterprise",
        name="Enterprise",
        tier=SubscriptionTier.ENTERPRISE,
        price_monthly=499.00,
        price_yearly=4790.00,
        features=[
            "Unlimited verifications",
            "All Professional features",
            "Government benefits verification",
            "Housing assistance verification",
            "Domestic violence protection",
            "Special education tracking",
            "Dedicated account manager",
            "SLA guarantee (99.9% uptime)",
            "Custom integrations",
            "On-premise deployment option",
            "HIPAA BAA available",
            "SOC 2 compliance reports"
        ],
        verifications_included=10000,
        overage_cost=0.25,
        use_cases=["healthcare", "business", "legal", "education", "government", "social_services"]
    )
}
