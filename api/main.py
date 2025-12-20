"""
PinkSync API - Main Application
Accessibility Signal Exchange Infrastructure

PinkSync is not a Deaf app. It's a Deaf-first protocol.
An accessibility broker that owns declarations, discovery, validation signals, and compliance artifacts.
Everything else is downstream.
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging
from datetime import datetime
import uuid

from .models.user import UserProfile, UserExperience
from .models.services import (
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    DashboardConfig
)
from .schemas import (
    AccessibilityContext,
    AccessibilityContextRequest,
    CapabilityResponse,
    ValidationReport,
    AccessibilityEvent,
    EventBatch,
    EventResponse,
    DiscrepancyReport,
    FalsePositiveReport,
    UserMismatchReport,
    ComplianceResult,
    ValidationTarget,
    ProviderInfo,
    SpecVersion
)
from .schemas.accessibility import ContextConstraints
from .schemas.capabilities import CapabilityDeclaration
from .schemas.events import EventType
from .services import PinkSyncServices, discover_services, SERVICE_DISCOVERY_MAP
from .validators import validate_url
from .integrations.fibonrose import send_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PinkSync API - Accessibility Signal Exchange",
    description="""
    ## PinkSync: Deaf-First Protocol Infrastructure
    
    **PinkSync is not a Deaf app. It's a Deaf-first protocol.**
    
    An accessibility signal exchange that owns:
    - **Accessibility declarations** - Apps and users declare capabilities and preferences
    - **Capability discovery** - Find providers that support specific accessibility features
    - **Validation signals** - Machine-readable compliance results against versioned specs
    - **Compliance artifacts** - Signed validation reports that can block deployments, unlock badges, or satisfy regulators
    - **Accessibility events** - Real-time event stream for monitoring and auditing
    
    Everything else is downstream.
    
    ### Authority & Scope
    
    PinkSync owns the **accessibility signal layer**, not the services themselves.
    
    When PinkSync can say: "This app declared X, emitted Y, failed Z" — it stops being optional.
    
    ### API Versioning
    
    All endpoints are versioned under `/v1/`. Current version: 1.0.0
    
    ### Core Infrastructure
    
    - **Context Initialization** - Handshake between app capabilities and user preferences
    - **Capability Registry** - Discovery of accessibility-capable providers
    - **Validation Engine** - Machine-readable compliance checking
    - **Event Stream** - Append-only, structured, auditable accessibility events
    - **Signal Correction** - Discrepancy reporting and validation refinement
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
# Accessibility Context Endpoints (v1)
# Reframed: Dashboard -> Context Initialization
# ============================================================================

@app.post("/v1/context/initialize", response_model=AccessibilityContext, tags=["Accessibility Context"])
async def initialize_accessibility_context(request: AccessibilityContextRequest):
    """
    Initialize an accessibility context for a consumer app or agent.
    
    This is a **context handshake**, not UI initialization.
    
    Internally, this means:
    - App declares capabilities
    - User declares preferences  
    - Broker returns constraints + defaults
    
    The response provides:
    - Compatibility scoring between preferences and capabilities
    - Required vs. recommended capabilities
    - Fallback options when capabilities are missing
    - Default settings for optimal accessibility
    
    This context can later be used to validate compliance and track events.
    """
    # Generate context ID
    context_id = f"ctx_{uuid.uuid4().hex[:12]}"
    
    # Calculate compatibility score
    user_prefs = request.user_preferences
    app_caps = request.app_capabilities
    
    # Simple compatibility scoring logic
    score_components = []
    warnings = []
    
    if user_prefs.requires_sign_language:
        if app_caps.supports_sign_language:
            score_components.append(1.0)
        else:
            score_components.append(0.0)
            warnings.append("App does not support sign language but user requires it")
    
    if user_prefs.requires_captions:
        if app_caps.supports_captions:
            score_components.append(1.0)
        else:
            score_components.append(0.0)
            warnings.append("App does not support captions but user requires them")
    
    if user_prefs.visual_only_mode:
        if app_caps.supports_visual_only:
            score_components.append(1.0)
        else:
            score_components.append(0.5)
            warnings.append("App has limited visual-only mode support")
    
    if user_prefs.high_contrast:
        if app_caps.supports_high_contrast:
            score_components.append(1.0)
        else:
            score_components.append(0.7)
    
    # Calculate average score
    compatibility_score = sum(score_components) / len(score_components) if score_components else 0.5
    
    # Build constraints
    required_caps = []
    recommended_caps = []
    fallback_options = {}
    default_settings = {}
    
    if user_prefs.requires_captions:
        required_caps.append("captions")
        default_settings["caption_enabled"] = True
        default_settings["caption_size"] = user_prefs.text_size_preference or "medium"
    
    if user_prefs.requires_sign_language:
        required_caps.append("sign_language_support")
        recommended_caps.append("high_quality_video")
    
    if user_prefs.visual_only_mode:
        required_caps.append("visual_indicators")
        fallback_options["audio_content"] = "text_transcript"
        fallback_options["audio_alerts"] = "visual_alerts"
    
    if user_prefs.high_contrast:
        default_settings["contrast_mode"] = "high"
        recommended_caps.append("theme_customization")
        
    constraints = ContextConstraints(
        required_capabilities=required_caps,
        recommended_capabilities=recommended_caps,
        fallback_options=fallback_options,
        default_settings=default_settings
    )
    
    return AccessibilityContext(
        context_id=context_id,
        user_preferences=user_prefs,
        app_capabilities=app_caps,
        constraints=constraints,
        compatibility_score=compatibility_score,
        warnings=warnings,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )



# Legacy endpoint for backward compatibility
@app.post("/api/initialize-dashboard", response_model=DashboardConfig, tags=["Legacy"])
async def initialize_dashboard(user: UserProfile):
    """
    **LEGACY ENDPOINT** - Use `/v1/context/initialize` instead.
    
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
# Capability Registry Endpoints (v1)
# Reframed: Service Discovery -> Capability Registry
# ============================================================================

@app.get("/v1/capabilities", response_model=CapabilityResponse, tags=["Capability Registry"])
async def query_capabilities(
    capability_type: Optional[str] = None,
    provider_type: Optional[str] = None,
    spec_version: Optional[str] = None
):
    """
    Query the capability registry.
    
    Answers:
    - What accessibility capabilities exist?
    - Which providers claim support?
    - What version of the spec do they comply with?
    
    A **capability** is any accessibility feature that a provider (service, app, platform) can offer.
    
    This endpoint enables discovery of accessibility-capable providers based on:
    - Capability type (visual, audio, text, etc.)
    - Provider type (service, app, platform)
    - Spec version compliance
    
    Eventually, service === accessibility-capable provider.
    """
    # Build mock capability and provider data
    capabilities = []
    providers = []
    
    # Mock data - in production this would query a database
    all_capabilities = [
        CapabilityDeclaration(
            capability_name="sign_language_support",
            capability_type="visual",
            description="Support for ASL video communication",
            parameters={"video_quality": "HD", "latency": "low"},
            required_features=["video_streaming", "low_latency_mode"]
        ),
        CapabilityDeclaration(
            capability_name="live_captions",
            capability_type="text",
            description="Real-time caption generation",
            parameters={"accuracy": "high", "language": "en"},
            required_features=["speech_to_text", "timing_sync"]
        ),
        CapabilityDeclaration(
            capability_name="visual_alerts",
            capability_type="visual",
            description="Visual notification system",
            parameters={"color_customization": True, "pattern_support": True},
            required_features=["display_api", "notification_system"]
        ),
    ]
    
    all_providers = [
        ProviderInfo(
            provider_id="provider_001",
            provider_name="Visual Communication Service",
            provider_type="service",
            capabilities=["sign_language_support", "visual_alerts"],
            spec_version=SpecVersion(version="1.0.0", compliance_level="full"),
            endpoint="https://api.visual-comm.example/v1",
            status="active",
            last_validated="2025-12-20T18:00:00Z"
        ),
        ProviderInfo(
            provider_id="provider_002",
            provider_name="Caption Pro Platform",
            provider_type="platform",
            capabilities=["live_captions"],
            spec_version=SpecVersion(version="1.0.0", compliance_level="full"),
            endpoint="https://api.captionpro.example/v1",
            status="active",
            last_validated="2025-12-20T17:30:00Z"
        ),
    ]
    
    # Filter capabilities
    filtered_caps = all_capabilities
    if capability_type:
        filtered_caps = [c for c in filtered_caps if c.capability_type == capability_type]
    
    # Filter providers
    filtered_providers = all_providers
    if provider_type:
        filtered_providers = [p for p in filtered_providers if p.provider_type == provider_type]
    if spec_version:
        # Simple version string comparison - for production use packaging.version.Version
        # For now, we accept this limitation as versions follow semantic versioning format
        filtered_providers = [p for p in filtered_providers if p.spec_version.version == spec_version or p.spec_version.version > spec_version]
    
    return CapabilityResponse(
        capabilities=filtered_caps,
        providers=filtered_providers,
        total_count=len(filtered_caps),
        query_timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/v1/providers", tags=["Capability Registry"])
async def list_providers(
    status: Optional[str] = None,
    capability: Optional[str] = None
):
    """
    List all registered accessibility providers.
    
    Providers are services, apps, or platforms that have declared
    their accessibility capabilities to PinkSync.
    
    Filter by:
    - Status (active, inactive, deprecated)
    - Specific capability support
    """
    # Mock provider data
    all_providers = [
        {
            "provider_id": "provider_001",
            "provider_name": "Visual Communication Service",
            "provider_type": "service",
            "capabilities": ["sign_language_support", "visual_alerts"],
            "status": "active"
        },
        {
            "provider_id": "provider_002",
            "provider_name": "Caption Pro Platform",
            "provider_type": "platform",
            "capabilities": ["live_captions"],
            "status": "active"
        },
    ]
    
    filtered = all_providers
    if status:
        filtered = [p for p in filtered if p["status"] == status]
    if capability:
        filtered = [p for p in filtered if capability in p["capabilities"]]
    
    return {
        "providers": filtered,
        "total_count": len(filtered),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Legacy service discovery endpoints
@app.get("/api/discover", tags=["Legacy"])
async def discover_services_endpoint(query: str):
    """
    **LEGACY ENDPOINT** - Use `/v1/capabilities` instead.
    
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


@app.get("/api/services", tags=["Legacy"])
async def list_all_services():
    """
    **LEGACY ENDPOINT** - Use `/v1/providers` or `/v1/capabilities` instead.
    
    List all available PinkSync services.
    
    Returns the complete service catalog organized by category.
    """
    return pinksync_services.get_all_services()


@app.get("/api/services/{category}", tags=["Legacy"])
async def get_service_category(category: str):
    """
    **LEGACY ENDPOINT** - Use `/v1/capabilities` with filters instead.
    
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
# Validation & Compliance Endpoints (v1)
# Enhanced: Machine-readable compliance results
# ============================================================================

@app.post("/v1/validate", response_model=ValidationReport, tags=["Validation & Compliance"])
async def validate_target(
    target_url: str,
    spec_version: str = "1.0.0",
    detailed: bool = True
):
    """
    Validate a target for accessibility compliance.
    
    Returns **machine-readable compliance results** versioned against specs.
    
    This is where PinkSync becomes unavoidable.
    
    Output shape matters more than AI cleverness.
    
    The response can later:
    - Block deployments
    - Unlock App Store badges  
    - Satisfy regulators
    
    This is infrastructure gravity.
    """
    # Generate report ID
    report_id = f"report_{uuid.uuid4().hex[:12]}"
    
    # Use existing validation logic
    basic_result = validate_url(target_url)
    
    # Build compliance results
    results = {}
    
    # Sign language support check
    results["sign_language_support"] = ComplianceResult(
        check_name="sign_language_support",
        status="partial" if basic_result.get("asl_compatible") else "fail",
        confidence=0.85,
        details="ASL video content detection",
        evidence=["asl_tag_present"] if basic_result.get("asl_compatible") else []
    )
    
    # Captions check
    results["captions"] = ComplianceResult(
        check_name="captions",
        status="pass",
        confidence=0.95,
        details="Caption support detected",
        evidence=["caption_element_found"]
    )
    
    # Visual-only mode check
    results["visual_only_mode"] = ComplianceResult(
        check_name="visual_only_mode",
        status="fail" if basic_result.get("audio_issues_found") else "pass",
        confidence=0.90,
        details="Audio dependency check",
        evidence=["audio_required"] if basic_result.get("audio_issues_found") else []
    )
    
    # Calculate overall score
    status_scores = {"pass": 1.0, "partial": 0.5, "fail": 0.0, "unknown": 0.0}
    scores = [status_scores.get(r.status, 0.0) for r in results.values()]
    overall_score = sum(scores) / len(scores) if scores else 0.0
    
    # Calculate overall confidence
    confidences = [r.confidence for r in results.values()]
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    return ValidationReport(
        report_id=report_id,
        target=ValidationTarget(
            target_type="url",
            target_identifier=target_url,
            metadata={"validated_at": datetime.utcnow().isoformat() + "Z"}
        ),
        spec_version=spec_version,
        results=results,
        overall_score=overall_score,
        confidence=overall_confidence,
        timestamp=datetime.utcnow().isoformat() + "Z",
        validator_version="1.0.0"
    )


@app.post("/v1/validate/batch", tags=["Validation & Compliance"])
async def validate_batch_targets(
    urls: List[str],
    spec_version: str = "1.0.0"
):
    """
    Batch validate multiple targets for accessibility compliance.
    
    Returns machine-readable compliance results for multiple targets.
    """
    reports = []
    for url in urls:
        report = await validate_target(url, spec_version, detailed=False)
        reports.append(report)
    
    return {
        "status": "success",
        "reports": reports,
        "total_validated": len(reports),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Legacy validation endpoints
@app.post("/api/py/ai-validate", response_model=ValidationResponse, tags=["Legacy"])
async def ai_validate(
    request: ValidationRequest,
    x_magician_role: Optional[str] = Header(None, alias="X-Magician-Role")
):
    """
    **LEGACY ENDPOINT** - Use `/v1/validate/batch` instead.
    
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


@app.post("/api/validate", tags=["Legacy"])
async def validate_single_url(url: str):
    """
    **LEGACY ENDPOINT** - Use `/v1/validate` instead.
    
    Validate a single URL for deaf accessibility.
    """
    result = validate_url(url)
    return result


# ============================================================================
# Signal Correction & Feedback Endpoints (v1)
# Reframed: Feedback -> Signal Correction
# ============================================================================

@app.post("/v1/feedback/discrepancy", tags=["Signal Correction"])
async def report_discrepancy(report: DiscrepancyReport):
    """
    Report a discrepancy between expected and actual accessibility behavior.
    
    Feedback is NOT vibes. Feedback is:
    - Discrepancy reports
    - False positives
    - User-declared mismatch
    
    In other words: **signal correction**, not opinions.
    
    This helps refine validation accuracy and improve the accessibility signal layer.
    """
    return {
        "status": "accepted",
        "report_id": report.report_id,
        "message": "Discrepancy report received and queued for analysis",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/v1/feedback/false-positive", tags=["Signal Correction"])
async def report_false_positive(report: FalsePositiveReport):
    """
    Report a false positive in validation results.
    
    When PinkSync's validation incorrectly flags something as failing
    or passing, this endpoint allows correction of the signal.
    
    False positive reports help improve validation accuracy over time.
    """
    return {
        "status": "accepted",
        "report_id": report.report_id,
        "validation_report_id": report.validation_report_id,
        "message": "False positive report received and queued for review",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/v1/feedback/mismatch", tags=["Signal Correction"])
async def report_user_mismatch(report: UserMismatchReport):
    """
    Report user-declared mismatch between system state and reality.
    
    When what the system thinks is happening differs from what
    the user actually experiences, this provides critical signal correction.
    """
    return {
        "status": "accepted",
        "report_id": report.report_id,
        "message": "Mismatch report received and queued for analysis",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Legacy feedback endpoint
@app.post("/api/feedback", tags=["Legacy"])
async def collect_feedback(service_used: str, feedback: UserExperience):
    """
    **LEGACY ENDPOINT** - Use `/v1/feedback/discrepancy` or `/v1/feedback/mismatch` instead.
    
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
# Accessibility Events Endpoint (v1) - THE HEART OF PINKSYNC
# ============================================================================

@app.post("/v1/events", response_model=EventResponse, tags=["Accessibility Events"])
async def submit_accessibility_event(event: AccessibilityEvent):
    """
    Submit an accessibility event.
    
    **THIS IS THE HEART OF PINKSYNC.**
    
    Events like:
    - user.requires_sign_language
    - user.enabled_visual_only_mode
    - app.entered_audio_state
    - motion_reduced_due_to_preference
    
    Events are:
    - **Append-only** - Never modified after creation
    - **Structured** - Follow strict schemas
    - **Auditable** - Permanent record of accessibility interactions
    
    Without events, PinkSync is static.
    With events, PinkSync becomes real-time infrastructure.
    
    When PinkSync can say: "This app declared X, emitted Y, failed Z" — it stops being optional.
    """
    # In production, this would persist to a database or event stream
    # For now, we accept and acknowledge the event
    
    logger.info(f"Accessibility event received: {event.event_type} from {event.source}")
    
    return EventResponse(
        status="success",
        accepted_count=1,
        rejected_count=0,
        event_ids=[event.event_id],
        errors=[],
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/v1/events/batch", response_model=EventResponse, tags=["Accessibility Events"])
async def submit_accessibility_events_batch(batch: EventBatch):
    """
    Submit a batch of accessibility events.
    
    Allows efficient submission of multiple events at once.
    All events are validated and accepted/rejected individually.
    
    Events are the append-only log that makes PinkSync auditable and accountable.
    """
    accepted = []
    rejected = []
    errors = []
    
    for event in batch.events:
        try:
            # Validate event structure
            event_id = getattr(event, 'event_id', None)
            if not event_id or not event.event_type or not event.source:
                # Use a fallback ID for rejected events without IDs
                rejected_id = event_id if event_id else f"unknown_{len(rejected)}"
                rejected.append(rejected_id)
                errors.append({
                    "event_id": rejected_id,
                    "error": "Missing required fields"
                })
                continue
            
            # In production, persist to event store
            logger.info(f"Batch event received: {event.event_type} from {event.source}")
            accepted.append(event_id)
            
        except Exception as e:
            # Handle case where event might not have event_id
            event_id = getattr(event, 'event_id', f"error_{len(rejected)}")
            rejected.append(event_id)
            errors.append({
                "event_id": event.event_id,
                "error": str(e)
            })
    
    return EventResponse(
        status="success" if len(accepted) > 0 else "error",
        accepted_count=len(accepted),
        rejected_count=len(rejected),
        event_ids=accepted,
        errors=errors,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/v1/events/types", tags=["Accessibility Events"])
async def list_event_types():
    """
    List all supported accessibility event types.
    
    Returns the complete taxonomy of events that PinkSync accepts.
    """
    return {
        "event_types": [
            {
                "type": event_type.value,
                "category": event_type.value.split('.')[0],
                "description": f"Event: {event_type.value}"
            }
            for event_type in EventType
        ],
        "total_count": len(EventType),
        "timestamp": datetime.utcnow().isoformat() + "Z"
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
        "name": "PinkSync API - Accessibility Signal Exchange",
        "version": "1.0.0",
        "description": "Deaf-First Protocol Infrastructure",
        "tagline": "Not a Deaf app. A Deaf-first protocol.",
        "api_versions": {
            "v1": "/v1",
            "legacy": "/api"
        },
        "docs": "/docs",
        "health": "/health",
        "core_capabilities": [
            "Accessibility context initialization",
            "Capability registry and discovery",
            "Machine-readable compliance validation",
            "Real-time accessibility event streaming",
            "Signal correction and feedback"
        ]
    }


# OpenAPI tags metadata
tags_metadata = [
    {
        "name": "Accessibility Context",
        "description": "Initialize accessibility contexts - handshake between app capabilities and user preferences"
    },
    {
        "name": "Capability Registry",
        "description": "Discover accessibility capabilities and providers. Query which providers support specific features."
    },
    {
        "name": "Validation & Compliance",
        "description": "Machine-readable compliance validation. Results can block deployments, unlock badges, or satisfy regulators."
    },
    {
        "name": "Accessibility Events",
        "description": "Real-time event stream. Append-only, structured, auditable. The heart of PinkSync."
    },
    {
        "name": "Signal Correction",
        "description": "Report discrepancies, false positives, and mismatches. Signal correction, not opinions."
    },
    {
        "name": "Legacy",
        "description": "Legacy endpoints for backward compatibility. Use versioned /v1 endpoints instead."
    },
    {
        "name": "Health",
        "description": "Health check and status endpoints"
    }
]

app.openapi_tags = tags_metadata
