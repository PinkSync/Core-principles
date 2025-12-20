"""
PinkSync Broker Models
Contract-first, type-safe models for accessibility event brokering.
"""

from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Accessibility Event Models (v1/events)
# ============================================================================

class AccessibilityEvent(BaseModel):
    """
    Accessibility Event - A declared need, state, or capability.
    Schema reference: specs/accessibility-intent.schema.json
    """
    app_id: str = Field(
        ...,
        description="Unique identifier for the application emitting the event",
        pattern="^[a-zA-Z0-9_-]+$",
        min_length=3,
        max_length=64
    )
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier. NULL for anonymous events.",
        pattern="^[a-zA-Z0-9_-]+$",
        max_length=128
    )
    intent: Literal[
        "visual_only",
        "sign_language",
        "reduced_motion",
        "high_contrast",
        "captions_mandatory",
        "no_audio_cues",
        "visual_alerts",
        "text_primary"
    ] = Field(
        ...,
        description="The accessibility intent being declared"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO 8601 timestamp when the event was generated"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the accessibility event"
    )
    compliance_level: Optional[Literal["bronze", "silver", "gold", "platinum"]] = Field(
        None,
        description="The compliance level this event relates to"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "app_id": "health-portal-v2",
                "user_id": "user-12345",
                "intent": "visual_only",
                "timestamp": "2025-12-20T18:00:00Z",
                "metadata": {
                    "severity": "required",
                    "context": "emergency_alert",
                    "capabilities": ["flash_screen", "vibrate", "large_text"]
                },
                "compliance_level": "gold"
            }
        }


class EventResponse(BaseModel):
    """Response for event submission."""
    event_id: str = Field(..., description="Unique event identifier")
    status: Literal["accepted", "rejected"] = Field(..., description="Event acceptance status")
    timestamp: datetime = Field(..., description="When event was processed")
    signature: str = Field(..., description="Cryptographic signature for verification")
    ledger_id: Optional[str] = Field(None, description="Optional ledger entry ID")


# ============================================================================
# Capability Models (v1/capabilities)
# ============================================================================

class AppCapability(BaseModel):
    """Application capability declaration."""
    app_id: str = Field(
        ...,
        description="Unique application identifier",
        pattern="^[a-zA-Z0-9_-]+$"
    )
    capabilities: List[str] = Field(
        ...,
        description="Array of supported accessibility intents"
    )
    compliance_level: Literal["bronze", "silver", "gold", "platinum"] = Field(
        ...,
        description="Declared compliance level"
    )
    version: str = Field(
        ...,
        description="Application version string"
    )
    registered_at: Optional[datetime] = Field(
        None,
        description="When this capability was registered"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "app_id": "video-platform",
                "capabilities": ["captions_mandatory", "visual_only", "high_contrast"],
                "compliance_level": "gold",
                "version": "2.1.0",
                "registered_at": "2025-12-20T18:00:00Z"
            }
        }


class CapabilitiesResponse(BaseModel):
    """Response for capabilities listing."""
    capabilities: List[AppCapability] = Field(
        default_factory=list,
        description="List of application capabilities"
    )
    total: int = Field(..., description="Total number of capabilities")


# ============================================================================
# Subscription Models (v1/subscribe)
# ============================================================================

class SubscriptionFilter(BaseModel):
    """Filter criteria for event subscriptions."""
    app_ids: Optional[List[str]] = Field(None, description="Filter by specific app IDs")
    intents: Optional[List[str]] = Field(None, description="Filter by intent types")
    compliance_levels: Optional[List[str]] = Field(None, description="Filter by compliance levels")


class SubscriptionRequest(BaseModel):
    """Subscription request from consumer."""
    consumer_id: str = Field(
        ...,
        description="Unique consumer identifier",
        pattern="^[a-zA-Z0-9_-]+$"
    )
    event_types: List[str] = Field(
        ...,
        description="Array of event types to receive"
    )
    webhook_url: Optional[str] = Field(
        None,
        description="URL to receive event notifications"
    )
    filter: Optional[SubscriptionFilter] = Field(
        None,
        description="Filter criteria for events"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "consumer_id": "accessibility-monitor-1",
                "event_types": ["visual_only", "captions_mandatory"],
                "webhook_url": "https://monitor.example.com/webhook",
                "filter": {
                    "compliance_levels": ["gold", "platinum"]
                }
            }
        }


class SubscriptionResponse(BaseModel):
    """Response for subscription creation."""
    subscription_id: str = Field(..., description="Unique subscription identifier")
    status: Literal["active", "pending", "inactive"] = Field(..., description="Subscription status")
    created_at: datetime = Field(..., description="When subscription was created")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time")


# ============================================================================
# Compliance Models (v1/compliance)
# ============================================================================

class ComplianceViolation(BaseModel):
    """Record of a compliance violation."""
    type: str = Field(..., description="Type of violation")
    severity: Literal["critical", "warning", "info"] = Field(..., description="Severity level")
    timestamp: datetime = Field(..., description="When violation occurred")
    description: Optional[str] = Field(None, description="Human-readable description")


class ComplianceReport(BaseModel):
    """Compliance status report for an application."""
    app_id: str = Field(..., description="Application identifier")
    compliance_level: Literal["bronze", "silver", "gold", "platinum"] = Field(
        ...,
        description="Current compliance level"
    )
    status: Literal["compliant", "non-compliant", "pending"] = Field(
        ...,
        description="Compliance status"
    )
    last_audit: Optional[datetime] = Field(None, description="Last audit timestamp")
    events_count: int = Field(0, description="Total events emitted")
    violations: List[ComplianceViolation] = Field(
        default_factory=list,
        description="List of violations"
    )
    certificate_url: Optional[str] = Field(
        None,
        description="URL to compliance certificate if available"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "app_id": "health-portal-v2",
                "compliance_level": "gold",
                "status": "compliant",
                "last_audit": "2025-12-15T10:00:00Z",
                "events_count": 1542,
                "violations": [],
                "certificate_url": "https://pinksync.org/certificates/health-portal-v2-gold"
            }
        }


# ============================================================================
# Sign Language Visual State Models
# ============================================================================

class LightingRequirements(BaseModel):
    """Lighting requirements for sign language."""
    adjustable: bool = Field(..., description="Whether lighting can be adjusted")
    background_contrast: Literal["low", "medium", "high"] = Field(
        ...,
        description="Required background contrast level"
    )
    facial_visibility: bool = Field(
        ...,
        description="Whether facial expressions MUST be clearly visible"
    )


class CameraAngle(BaseModel):
    """Camera angle requirements."""
    multiple_angles: bool = Field(..., description="Support for multiple camera angles")
    full_body: bool = Field(..., description="Whether full body signing space is captured")
    face_focus: bool = Field(..., description="Whether facial expressions are emphasized")


class VisualRequirements(BaseModel):
    """Visual requirements for sign language interfaces."""
    video_quality: Literal["720p", "1080p", "4k"] = Field(
        ...,
        description="Minimum video quality for sign language clarity"
    )
    frame_rate: int = Field(
        ...,
        ge=24,
        le=120,
        description="Frames per second - MUST be at least 30 for sign language"
    )
    lighting: LightingRequirements
    camera_angle: Optional[CameraAngle] = None


class LatencyRequirements(BaseModel):
    """Latency requirements for real-time sign language."""
    max_latency_ms: int = Field(
        ...,
        ge=0,
        le=500,
        description="Maximum acceptable latency in milliseconds"
    )
    jitter_tolerance_ms: int = Field(
        ...,
        ge=0,
        le=100,
        description="Maximum jitter tolerance"
    )


class AccessibilityFeatures(BaseModel):
    """Additional accessibility features for sign language."""
    background_blur: bool = Field(False, description="Background blur capability")
    zoom_controls: bool = Field(False, description="Ability to zoom in on signing")
    recording_capability: bool = Field(False, description="Ability to record and replay")
    slow_motion: bool = Field(False, description="Ability to play back in slow motion")


class SignVisualState(BaseModel):
    """
    Sign Language Visual State.
    Schema reference: specs/sign-visual-state.schema.json
    """
    state_id: str = Field(
        ...,
        description="Unique identifier for this visual state",
        pattern="^[a-zA-Z0-9_-]+$"
    )
    visual_requirements: VisualRequirements
    interaction_mode: Literal["live_video", "recorded_video", "avatar_signing", "text_gloss"] = Field(
        ...,
        description="The mode of sign language interaction"
    )
    latency_requirements: Optional[LatencyRequirements] = None
    accessibility_features: Optional[AccessibilityFeatures] = None
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO 8601 timestamp when this state was defined"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the visual state"
    )
