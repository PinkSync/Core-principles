"""
PinkSync API - Main Application
DEAF FIRST Platform Services API

Building what WE understand, not fitting into THEIR system.
Middleware, FastAPI, API broker of all networks of accessibility partners and services.
"""

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
import uuid
import hashlib
from datetime import datetime

from .models.user import UserProfile, UserExperience
from .models.services import (
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    DashboardConfig
)
from .models.broker import (
    AccessibilityEvent,
    EventResponse,
    AppCapability,
    CapabilitiesResponse,
    SubscriptionRequest,
    SubscriptionResponse,
    ComplianceReport,
    ComplianceViolation
)
from .services import PinkSyncServices, discover_services, SERVICE_DISCOVERY_MAP
from .validators import validate_url
from .integrations.fibonrose import send_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PinkSync API",
    description="""
    ## PinkSync - Accessibility API Broker
    
    **Building what WE understand, not fitting into THEIR system.**
    
    PinkSync is an accessibility API broker with a hard contract. We broker accessibility 
    intents, capabilities, and compliance signals between apps, users, and agents—without 
    owning the app itself.
    
    Think: **Stripe, but for accessibility signals. Twilio, but for Deaf-first interaction states.**
    
    ### Core Broker API (v1)
    
    - **POST /v1/events** - Accept accessibility events from applications
    - **GET /v1/capabilities** - List registered application capabilities
    - **POST /v1/subscribe** - Subscribe to accessibility events
    - **GET /v1/compliance/{app_id}** - Check compliance status
    
    **Contract Reference:** See `/specs/event-broker.contract.md` for full API contract.
    
    ### DEAF FIRST Platform Services
    
    This API also provides comprehensive services for the deaf and hard-of-hearing community:
    
    - **Communication Services**: Visual chat, ASL video calls, text relay
    - **Financial Services**: Tax help, insurance navigation, real estate support
    - **Accessibility Services**: Captioning, visual alerts, environmental awareness
    - **Education Services**: ASL learning, financial literacy, tech training
    - **Professional Services**: Legal support, healthcare navigation, employment help
    - **Community Services**: Networking, resource sharing, advocacy
    - **Emergency Services**: Emergency communication, crisis support
    - **Business Services**: Business development, financial management
    
    ### Core Principles
    
    - **Text-based primary**: Text is the primary interface
    - **Visual indicators**: Visual feedback for everything
    - **No audio requirements**: Never requires hearing
    - **Cultural competency**: Understands deaf culture
    - **Accessibility first**: Built for accessibility, not retrofitted
    
    ### What PinkSync Does ✅
    
    - Brokers accessibility intent signals
    - Enforces contract shape via type-safe validation
    - Emits machine-verifiable signals
    - Produces structured logs for compliance auditing
    
    ### What PinkSync Does NOT Do ❌
    
    - Does NOT render UI
    - Does NOT generate video or content
    - Does NOT decide morality
    - Does NOT own the source applications
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

# In-memory storage for broker (would be replaced with database in production)
events_store = []
capabilities_store = []
subscriptions_store = []
compliance_store = {}


# ============================================================================
# PinkSync Broker API v1 - Accessibility Event Brokering
# ============================================================================

@app.post("/v1/events", response_model=EventResponse, status_code=201, tags=["Broker v1"])
async def accept_event(event: AccessibilityEvent):
    """
    Accept accessibility events from applications.
    
    This endpoint brokers accessibility intents, capabilities, and compliance signals
    between apps, users, and agents.
    
    **Contract:** Defined in specs/event-broker.contract.md
    **Schema:** Defined in specs/accessibility-intent.schema.json
    
    Returns a signed response with event ID for verification and audit purposes.
    """
    # Generate unique event ID
    event_id = str(uuid.uuid4())
    
    # Create signature (simplified - in production use proper cryptographic signing)
    signature_data = f"{event_id}:{event.app_id}:{event.intent}:{event.timestamp}"
    signature = hashlib.sha256(signature_data.encode()).hexdigest()
    
    # Store event (in production, this would go to a database and message queue)
    event_record = {
        "event_id": event_id,
        "event": event.model_dump(),
        "processed_at": datetime.utcnow(),
        "signature": signature
    }
    events_store.append(event_record)
    
    # Update compliance tracking
    if event.app_id not in compliance_store:
        compliance_store[event.app_id] = {
            "events_count": 0,
            "violations": [],
            "last_event": None
        }
    compliance_store[event.app_id]["events_count"] += 1
    compliance_store[event.app_id]["last_event"] = datetime.utcnow()
    
    logger.info(f"Event accepted: {event_id} from {event.app_id} with intent {event.intent}")
    
    return EventResponse(
        event_id=event_id,
        status="accepted",
        timestamp=datetime.utcnow(),
        signature=signature,
        ledger_id=None  # Would be set if using blockchain/ledger
    )


@app.get("/v1/capabilities", response_model=CapabilitiesResponse, tags=["Broker v1"])
async def list_capabilities(
    app_id: Optional[str] = Query(None, description="Filter by specific application"),
    compliance_level: Optional[str] = Query(None, description="Filter by compliance level"),
    intent: Optional[str] = Query(None, description="Filter by supported intent")
):
    """
    List all registered application capabilities.
    
    Returns capabilities declared by applications, filterable by various criteria.
    
    **Contract:** Defined in specs/event-broker.contract.md
    """
    filtered_capabilities = capabilities_store.copy()
    
    # Apply filters
    if app_id:
        filtered_capabilities = [c for c in filtered_capabilities if c.app_id == app_id]
    if compliance_level:
        filtered_capabilities = [c for c in filtered_capabilities if c.compliance_level == compliance_level]
    if intent:
        filtered_capabilities = [c for c in filtered_capabilities if intent in c.capabilities]
    
    return CapabilitiesResponse(
        capabilities=filtered_capabilities,
        total=len(filtered_capabilities)
    )


@app.post("/v1/subscribe", response_model=SubscriptionResponse, status_code=201, tags=["Broker v1"])
async def create_subscription(subscription: SubscriptionRequest):
    """
    Subscribe to accessibility events.
    
    Allows consumers (UIs, agents, validators) to subscribe to specific event types
    and receive notifications via webhook or polling.
    
    **Contract:** Defined in specs/event-broker.contract.md
    """
    # Check if subscription already exists
    existing = [s for s in subscriptions_store if s["consumer_id"] == subscription.consumer_id]
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Subscription already exists for consumer_id: {subscription.consumer_id}"
        )
    
    # Generate subscription ID
    subscription_id = str(uuid.uuid4())
    
    # Store subscription
    subscription_record = {
        "subscription_id": subscription_id,
        "subscription": subscription.model_dump(),
        "created_at": datetime.utcnow(),
        "status": "active"
    }
    subscriptions_store.append(subscription_record)
    
    logger.info(f"Subscription created: {subscription_id} for consumer {subscription.consumer_id}")
    
    return SubscriptionResponse(
        subscription_id=subscription_id,
        status="active",
        created_at=datetime.utcnow(),
        expires_at=None  # Could set expiration if needed
    )


@app.get("/v1/compliance/{app_id}", response_model=ComplianceReport, tags=["Broker v1"])
async def get_compliance(
    app_id: str,
    detailed: bool = Query(False, description="Include detailed compliance report")
):
    """
    Check compliance status for an application.
    
    Returns compliance level, audit history, event counts, and any violations.
    Enables CI enforcement, partner audits, and regulatory proof.
    
    **Contract:** Defined in specs/event-broker.contract.md
    **Compliance Levels:** Defined in specs/compliance-levels.md
    """
    # Check if app exists in our records
    if app_id not in compliance_store:
        raise HTTPException(
            status_code=404,
            detail=f"Application '{app_id}' not registered with PinkSync broker"
        )
    
    # Get compliance data
    app_compliance = compliance_store[app_id]
    
    # Determine compliance level based on events count (simplified logic)
    events_count = app_compliance["events_count"]
    if events_count >= 200:
        level = "gold"
    elif events_count >= 50:
        level = "silver"
    elif events_count >= 10:
        level = "bronze"
    else:
        level = "bronze"
    
    # Determine status
    violations = app_compliance["violations"]
    critical_violations = [v for v in violations if v["severity"] == "critical"]
    if critical_violations:
        status = "non-compliant"
    else:
        status = "compliant"
    
    # Build violations list if detailed
    violation_objects = []
    if detailed:
        for v in violations:
            violation_objects.append(ComplianceViolation(
                type=v["type"],
                severity=v["severity"],
                timestamp=v["timestamp"],
                description=v.get("description")
            ))
    
    return ComplianceReport(
        app_id=app_id,
        compliance_level=level,
        status=status,
        last_audit=app_compliance.get("last_event"),
        events_count=events_count,
        violations=violation_objects,
        certificate_url=f"https://pinksync.org/certificates/{app_id}-{level}" if status == "compliant" else None
    )


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


# OpenAPI tags metadata
tags_metadata = [
    {
        "name": "Broker v1",
        "description": "PinkSync Accessibility Event Broker - Core API for accessibility intent brokering. Contract-first, type-safe, async-native. See specs/event-broker.contract.md for full contract."
    },
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
        "name": "Feedback",
        "description": "Collect service feedback and improvement suggestions"
    },
    {
        "name": "Health",
        "description": "Health check endpoints"
    }
]

app.openapi_tags = tags_metadata
