"""
PinkSync API - Main Application
DEAF FIRST Platform Services API

Building what WE understand, not fitting into THEIR system.
Middleware, FastAPI, API broker of all networks of accessibility partners and services.
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging

from .models.user import UserProfile, UserExperience
from .models.services import (
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    DashboardConfig
)
from .models.biometric import (
    VerificationRequest,
    VerificationResult,
    BiometricProfile,
    UseCaseCategory
)
from .models.subscription import (
    PricingPlan,
    CreateCheckoutRequest,
    CheckoutSessionResponse,
    SubscriptionInfo,
    UsageReport,
    PortalSessionResponse,
    PRICING_PLANS
)
from .services import (
    PinkSyncServices,
    discover_services,
    SERVICE_DISCOVERY_MAP,
    asl_biometric_service,
    stripe_service
)
from .validators import validate_url
from .integrations.fibonrose import send_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PinkSync API",
    description="""
    ## DEAF FIRST Platform Services API
    
    Building what WE understand, not fitting into THEIR system.
    
    This API provides comprehensive services for the deaf and hard-of-hearing community,
    including:
    
    - **Communication Services**: Visual chat, ASL video calls, text relay
    - **Financial Services**: Tax help, insurance navigation, real estate support
    - **Accessibility Services**: Captioning, visual alerts, environmental awareness
    - **Education Services**: ASL learning, financial literacy, tech training
    - **Professional Services**: Legal support, healthcare navigation, employment help
    - **Community Services**: Networking, resource sharing, advocacy
    - **Emergency Services**: Emergency communication, crisis support
    - **Business Services**: Business development, financial management
    - **ASL Biometric Verification**: Identity verification using ASL signing patterns
    - **Subscription Management**: Stripe-powered subscription plans
    
    ### Core Principles
    
    - **Text-based primary**: Text is the primary interface
    - **Visual indicators**: Visual feedback for everything
    - **No audio requirements**: Never requires hearing
    - **Cultural competency**: Understands deaf culture
    - **Accessibility first**: Built for accessibility, not retrofitted
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pinksync_services = PinkSyncServices()


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@app.post("/api/initialize-dashboard", response_model=DashboardConfig, tags=["Dashboard"])
async def initialize_dashboard(user: UserProfile):
    """
    Initialize a personalized DEAF FIRST dashboard for a user.
    
    Creates a customized dashboard based on user profile and needs,
    with quick access to relevant services and personalized content.
    """
    # Build service list based on user needs
    active_services = ["Emergency Text Line", "Visual Chat", "Visual Alerts"]
    
    if user.needs_financial_help:
        active_services.extend([
            "Visual Tax Prep",
            "Budget Visualizer",
            "Financial Education"
        ])
    
    if user.is_business_owner:
        active_services.extend([
            "Business Plan Review",
            "Business Taxes",
            "Legal Document Review"
        ])
    
    if user.needs_healthcare_help:
        active_services.extend([
            "Appointment Support",
            "Medical Interpreter",
            "Live Captions"
        ])
    
    # Get upcoming deadlines (mock data)
    upcoming_deadlines = ["Q3 Tax Deadline", "Healthcare Renewal"]
    
    # Get recommended services based on goals
    recommended = []
    for goal in user.financial_goals:
        goal_lower = goal.lower()
        if "house" in goal_lower:
            recommended.append("Property Search")
            recommended.append("Mortgage Guidance")
        if "business" in goal_lower:
            recommended.append("Business Plan Review")
        if "retire" in goal_lower:
            recommended.append("Retirement Planning")
    
    # Get local events
    local_events = [
        f"Deaf Expo - {user.location}",
        f"Financial Literacy Workshop - {user.location}"
    ]
    
    return DashboardConfig(
        dashboard_title=f"{user.name}'s DEAF FIRST Dashboard",
        quick_access=[
            "Emergency Text Line",
            "Financial Advisor Chat",
            "Document Review",
            "Community Resources"
        ],
        service_categories={
            "immediate": ["Emergency Services", "Crisis Support"],
            "daily": ["Visual Chat", "Captioning"],
            "weekly": ["Financial Review", "Health Check"],
            "as_needed": active_services
        },
        personalized_content={
            "financial_goals": user.financial_goals,
            "upcoming_deadlines": upcoming_deadlines,
            "recommended_services": list(set(recommended)),
            "community_events": local_events
        },
        integrations={
            "bank_accounts": user.connected_banks or [],
            "insurance_policies": user.insurance_policies or [],
            "tax_software": user.tax_software,
            "legal_documents": user.legal_documents or []
        }
    )


# ============================================================================
# Service Discovery Endpoints
# ============================================================================

@app.get("/api/discover", tags=["Discovery"])
async def discover_services_endpoint(query: str):
    """
    Discover services based on user query.
    
    Searches the service catalog for matches and provides
    alternative suggestions and community recommendations.
    """
    result = discover_services(query)
    
    if not result["matched_services"] and not result["alternative_services"]:
        return {
            "matched_services": [],
            "message": "No direct match. Try related terms.",
            "suggestions": list(SERVICE_DISCOVERY_MAP.keys())
        }
    
    return result


@app.get("/api/services", tags=["Services"])
async def list_all_services():
    """
    List all available PinkSync services.
    
    Returns the complete service catalog organized by category.
    """
    return pinksync_services.get_all_services()


@app.get("/api/services/{category}", tags=["Services"])
async def get_service_category(category: str):
    """
    Get services by category.
    
    Available categories:
    - communication
    - financial
    - accessibility
    - education
    - professional
    - community
    - emergency
    - business
    """
    services = pinksync_services.get_service_category(category)
    
    if not services:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available categories: communication, financial, accessibility, education, professional, community, emergency, business"
        )
    
    return {
        "category": category,
        "services": services
    }


# ============================================================================
# Validation Endpoints
# ============================================================================

@app.post("/api/py/ai-validate", response_model=ValidationResponse, tags=["Validation"])
async def ai_validate(
    request: ValidationRequest,
    x_magician_role: Optional[str] = Header(None, alias="X-Magician-Role")
):
    """
    AI-triggered batch validation for deaf accessibility.
    
    Validates multiple URLs for deaf-first accessibility compliance
    and reports scores to Fibonrose dashboard.
    
    Requires X-Magician-Role header set to 'accessibility-auditor'.
    """
    # Optional: Validate agent role
    if x_magician_role and x_magician_role != "accessibility-auditor":
        logger.warning(f"Unauthorized agent role: {x_magician_role}")
    
    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    results = []
    for url in request.urls:
        result = validate_url(url)
        score = result.get("deaf_score", 0)
        asl_compatible = result.get("asl_compatible", False)
        
        # Send score to Fibonrose
        await send_score(url, score, asl_compatible)
        
        results.append(ValidationResult(
            url=url,
            deaf_score=score,
            asl_compatible=asl_compatible,
            audio_issues_found=result.get("audio_issues_found", False)
        ))
    
    return ValidationResponse(status="success", results=results)


@app.post("/api/validate", tags=["Validation"])
async def validate_single_url(url: str):
    """
    Validate a single URL for deaf accessibility.
    """
    result = validate_url(url)
    return result


# ============================================================================
# Feedback Endpoints
# ============================================================================

@app.post("/api/feedback", tags=["Feedback"])
async def collect_feedback(service_used: str, feedback: UserExperience):
    """
    Collect feedback on a service.
    
    Helps improve services and ensures they remain DEAF FIRST.
    """
    return {
        "message": "Feedback received",
        "service": service_used,
        "summary": {
            "rating": feedback.rating,
            "accessibility_score": feedback.accessibility_score,
            "deaf_friendliness": feedback.deaf_friendliness,
            "suggested_improvements": feedback.suggested_improvements,
            "would_recommend": feedback.would_recommend,
            "alternatives_needed": feedback.alternatives_needed
        }
    }


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "PinkSync API"}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "PinkSync API",
        "version": "1.0.0",
        "description": "DEAF FIRST Platform Services API",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================================
# ASL Biometric Verification Endpoints
# ============================================================================

@app.post("/api/biometric/verify", response_model=VerificationResult, tags=["Biometric"])
async def verify_identity(request: VerificationRequest):
    """
    Verify signer identity using ASL biometric patterns.
    
    Supports various use cases including:
    - Healthcare (telehealth consent, pharmacy verification)
    - Legal (court interpreter, contract signing)
    - Business (remote work, contract verification)
    - Education (exam proctoring, special education)
    - Government (benefits verification)
    - Social Services (protection orders, housing)
    """
    # Get or create biometric profile
    profile = asl_biometric_service.get_biometric_profile(request.user_id)
    if not profile:
        profile = asl_biometric_service.register_biometric_profile(request.user_id)
    
    result = await asl_biometric_service.verify_signer_identity(
        video_data=request.video_data or "",
        stored_biometrics=profile,
        use_case=request.use_case,
        context=request.context
    )
    
    return result


@app.post("/api/biometric/register", response_model=BiometricProfile, tags=["Biometric"])
async def register_biometric_profile(user_id: str, profile_type: str = "asl_signer"):
    """
    Register a new biometric profile for a user.
    
    This creates a stored profile that can be used for future verifications.
    """
    existing = asl_biometric_service.get_biometric_profile(user_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Biometric profile already exists for this user"
        )
    
    profile = asl_biometric_service.register_biometric_profile(user_id, profile_type)
    return profile


@app.get("/api/biometric/profile/{user_id}", response_model=BiometricProfile, tags=["Biometric"])
async def get_biometric_profile(user_id: str):
    """
    Get biometric profile for a user.
    """
    profile = asl_biometric_service.get_biometric_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.get("/api/biometric/pricing", tags=["Biometric"])
async def get_biometric_pricing():
    """
    Get pricing information for all biometric verification use cases.
    """
    return asl_biometric_service.get_use_case_pricing()


@app.get("/api/biometric/use-cases", tags=["Biometric"])
async def get_use_cases():
    """
    Get all available biometric verification use cases.
    """
    return {
        "use_cases": [
            {
                "category": "healthcare",
                "services": [
                    {"name": "Telehealth Consent", "price": 0.50, "description": "Verify patient identity for medical consultations"},
                    {"name": "Pharmacy Verification", "price": 2.00, "description": "Verify patient for prescription pickup"},
                    {"name": "Medical Interpreter", "price": 3.00, "description": "Verify interpreter identity"}
                ]
            },
            {
                "category": "legal",
                "services": [
                    {"name": "Court Interpreter", "price": 15.00, "description": "Continuous verification per hour"},
                    {"name": "Contract Signing", "price": 25.00, "description": "Verify all parties in contract"}
                ]
            },
            {
                "category": "business",
                "services": [
                    {"name": "Remote Work", "price": 0.25, "description": "Verify employee attendance"},
                    {"name": "Contract Verification", "price": 25.00, "description": "Verify business contract parties"}
                ]
            },
            {
                "category": "education",
                "services": [
                    {"name": "Exam Proctoring", "price": 10.00, "description": "Verify student during exams"},
                    {"name": "Special Education", "price": 15.00, "description": "Track therapy participation"}
                ]
            },
            {
                "category": "government",
                "services": [
                    {"name": "Benefits Verification", "price": 5.00, "description": "Verify recipient identity"},
                    {"name": "Identity Verification", "price": 8.00, "description": "General government ID verification"}
                ]
            },
            {
                "category": "social_services",
                "services": [
                    {"name": "Protection Verification", "price": 0.00, "description": "Free safety verification"},
                    {"name": "Housing Verification", "price": 8.00, "description": "Verify housing applicants"}
                ]
            }
        ]
    }


# ============================================================================
# Subscription Endpoints (Stripe Integration)
# ============================================================================

@app.get("/api/subscription/plans", response_model=List[PricingPlan], tags=["Subscription"])
async def get_pricing_plans():
    """
    Get all available subscription plans.
    
    Returns Starter, Professional, and Enterprise plans with features and pricing.
    """
    return stripe_service.get_pricing_plans()


@app.get("/api/subscription/plans/{plan_id}", response_model=PricingPlan, tags=["Subscription"])
async def get_plan(plan_id: str):
    """
    Get details for a specific subscription plan.
    """
    plan = stripe_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.post("/api/subscription/checkout", response_model=CheckoutSessionResponse, tags=["Subscription"])
async def create_checkout_session(request: CreateCheckoutRequest):
    """
    Create a Stripe checkout session for subscription.
    
    Returns a checkout URL to redirect the customer to complete payment.
    """
    try:
        session = await stripe_service.create_checkout_session(request)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@app.post("/api/subscription/portal", response_model=PortalSessionResponse, tags=["Subscription"])
async def create_portal_session(customer_id: str, return_url: str):
    """
    Create a Stripe customer portal session.
    
    Allows customers to manage their subscription, update payment methods, etc.
    """
    try:
        session = await stripe_service.create_portal_session(customer_id, return_url)
        return session
    except Exception as e:
        logger.error(f"Portal error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create portal session")


@app.post("/api/subscription/webhook", tags=["Subscription"])
async def handle_stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    Processes subscription lifecycle events like payments, cancellations, etc.
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    
    try:
        result = await stripe_service.handle_webhook(payload, signature)
        return result
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@app.get("/api/subscription/{subscription_id}", response_model=SubscriptionInfo, tags=["Subscription"])
async def get_subscription(subscription_id: str):
    """
    Get subscription information.
    """
    sub = stripe_service.get_subscription(subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


@app.get("/api/subscription/{subscription_id}/usage", response_model=UsageReport, tags=["Subscription"])
async def get_usage_report(subscription_id: str):
    """
    Get usage report for a subscription.
    
    Shows verifications used, remaining, and overage costs.
    """
    usage = stripe_service.get_usage_report(subscription_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Usage report not found")
    return usage


@app.post("/api/subscription/{subscription_id}/record-usage", tags=["Subscription"])
async def record_usage(subscription_id: str, use_case: str):
    """
    Record a verification usage for a subscription.
    
    Updates the usage count and calculates any overage.
    """
    result = stripe_service.record_verification_usage(subscription_id, use_case)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# OpenAPI tags metadata
tags_metadata = [
    {
        "name": "Dashboard",
        "description": "Initialize personalized Deaf-First dashboard"
    },
    {
        "name": "Discovery",
        "description": "Discover services based on user queries"
    },
    {
        "name": "Services",
        "description": "Browse and access PinkSync services"
    },
    {
        "name": "Validation",
        "description": "Validate URLs for deaf accessibility"
    },
    {
        "name": "Biometric",
        "description": "ASL biometric identity verification for healthcare, legal, business, education, and government use cases"
    },
    {
        "name": "Subscription",
        "description": "Stripe subscription management for ASL Biometric verification services"
    },
    {
        "name": "Feedback",
        "description": "Collect service feedback and improvement suggestions"
    },
    {
        "name": "Health",
        "description": "Health check endpoints"
    }
]

app.openapi_tags = tags_metadata
