"""
Accessibility Events Schemas
Schemas for real-time accessibility event streaming
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """Types of accessibility events."""
    
    # User preference events
    USER_REQUIRES_SIGN_LANGUAGE = "user.requires_sign_language"
    USER_ENABLED_VISUAL_ONLY_MODE = "user.enabled_visual_only_mode"
    USER_ENABLED_CAPTIONS = "user.enabled_captions"
    USER_CHANGED_CONTRAST = "user.changed_contrast"
    USER_CHANGED_TEXT_SIZE = "user.changed_text_size"
    MOTION_REDUCED_DUE_TO_PREFERENCE = "motion_reduced_due_to_preference"
    
    # Application state events
    APP_ENTERED_AUDIO_STATE = "app.entered_audio_state"
    APP_ENTERED_VIDEO_STATE = "app.entered_video_state"
    APP_LOST_ACCESSIBILITY_SUPPORT = "app.lost_accessibility_support"
    APP_GAINED_ACCESSIBILITY_SUPPORT = "app.gained_accessibility_support"
    
    # Interaction events
    ACCESSIBILITY_FEATURE_USED = "accessibility_feature_used"
    ACCESSIBILITY_FEATURE_FAILED = "accessibility_feature_failed"
    FALLBACK_MODE_ACTIVATED = "fallback_mode_activated"
    
    # Compliance events
    COMPLIANCE_CHECK_PASSED = "compliance_check_passed"
    COMPLIANCE_CHECK_FAILED = "compliance_check_failed"
    VALIDATION_REQUESTED = "validation_requested"
    VALIDATION_COMPLETED = "validation_completed"


class AccessibilityEvent(BaseModel):
    """Single accessibility event."""
    
    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: str = Field(..., description="Event timestamp (ISO 8601)")
    source: str = Field(..., description="Event source (app_id, user_id, service_id)")
    context_id: Optional[str] = Field(None, description="Associated accessibility context ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_abc123",
                "event_type": "user.requires_sign_language",
                "timestamp": "2025-12-20T18:03:00Z",
                "source": "user_456",
                "context_id": "ctx_abc123",
                "data": {
                    "preference_enabled": True,
                    "language": "ASL"
                },
                "metadata": {
                    "app_version": "1.0.0",
                    "platform": "web"
                }
            }
        }


class EventBatch(BaseModel):
    """Batch of accessibility events."""
    
    batch_id: str = Field(..., description="Unique batch identifier")
    events: List[AccessibilityEvent] = Field(..., description="List of events in batch")
    batch_timestamp: str = Field(..., description="Batch creation timestamp (ISO 8601)")
    source_context: Optional[str] = Field(None, description="Source context for the batch")
    
    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "batch_xyz789",
                "events": [
                    {
                        "event_id": "evt_001",
                        "event_type": "user.requires_sign_language",
                        "timestamp": "2025-12-20T18:03:00Z",
                        "source": "user_456",
                        "data": {}
                    },
                    {
                        "event_id": "evt_002",
                        "event_type": "app.entered_video_state",
                        "timestamp": "2025-12-20T18:03:01Z",
                        "source": "app_123",
                        "data": {}
                    }
                ],
                "batch_timestamp": "2025-12-20T18:03:02Z",
                "source_context": "session_abc"
            }
        }


class EventResponse(BaseModel):
    """Response for event submission."""
    
    status: str = Field("success", description="Submission status")
    accepted_count: int = Field(0, description="Number of events accepted")
    rejected_count: int = Field(0, description="Number of events rejected")
    event_ids: List[str] = Field(default_factory=list, description="IDs of accepted events")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="Errors for rejected events")
    timestamp: str = Field(..., description="Response timestamp (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "accepted_count": 2,
                "rejected_count": 0,
                "event_ids": ["evt_001", "evt_002"],
                "errors": [],
                "timestamp": "2025-12-20T18:03:02Z"
            }
        }
