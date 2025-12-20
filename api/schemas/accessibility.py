"""
Accessibility Context Schemas
Schemas for initializing accessibility contexts for consumer apps or agents
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AccessibilityPreferences(BaseModel):
    """User-declared accessibility preferences."""
    
    requires_sign_language: bool = Field(False, description="User requires sign language support")
    requires_captions: bool = Field(False, description="User requires captions")
    visual_only_mode: bool = Field(False, description="User operates in visual-only mode")
    motion_reduced: bool = Field(False, description="User prefers reduced motion")
    high_contrast: bool = Field(False, description="User requires high contrast")
    text_size_preference: Optional[str] = Field("medium", description="Text size preference (small, medium, large, xlarge)")
    color_blindness_type: Optional[str] = Field(None, description="Type of color blindness if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requires_sign_language": True,
                "requires_captions": True,
                "visual_only_mode": True,
                "motion_reduced": False,
                "high_contrast": True,
                "text_size_preference": "large",
                "color_blindness_type": None
            }
        }


class AppCapabilities(BaseModel):
    """Application-declared accessibility capabilities."""
    
    app_name: str = Field(..., description="Application name")
    app_version: str = Field(..., description="Application version")
    supports_sign_language: bool = Field(False, description="Supports sign language")
    supports_captions: bool = Field(False, description="Supports captions")
    supports_visual_only: bool = Field(False, description="Supports visual-only mode")
    supports_reduced_motion: bool = Field(False, description="Supports reduced motion")
    supports_high_contrast: bool = Field(False, description="Supports high contrast themes")
    text_scaling_available: bool = Field(False, description="Supports text scaling")
    spec_version: str = Field("1.0.0", description="Accessibility spec version compliance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "MyDeafApp",
                "app_version": "2.1.0",
                "supports_sign_language": True,
                "supports_captions": True,
                "supports_visual_only": True,
                "supports_reduced_motion": True,
                "supports_high_contrast": True,
                "text_scaling_available": True,
                "spec_version": "1.0.0"
            }
        }


class ContextConstraints(BaseModel):
    """Constraints and defaults returned by broker."""
    
    required_capabilities: List[str] = Field(default_factory=list, description="Required capabilities for this context")
    recommended_capabilities: List[str] = Field(default_factory=list, description="Recommended capabilities")
    fallback_options: Dict[str, str] = Field(default_factory=dict, description="Fallback options if capabilities missing")
    default_settings: Dict[str, Any] = Field(default_factory=dict, description="Default settings for this context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "required_capabilities": ["captions", "visual_indicators"],
                "recommended_capabilities": ["sign_language_support", "high_contrast"],
                "fallback_options": {
                    "audio_content": "text_transcript",
                    "video_only": "image_descriptions"
                },
                "default_settings": {
                    "caption_size": "large",
                    "contrast_mode": "high"
                }
            }
        }


class AccessibilityContextRequest(BaseModel):
    """Request to initialize an accessibility context."""
    
    user_preferences: AccessibilityPreferences = Field(..., description="User accessibility preferences")
    app_capabilities: AppCapabilities = Field(..., description="Application capabilities")
    context_type: str = Field("standard", description="Type of context (standard, emergency, educational, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_preferences": {
                    "requires_sign_language": True,
                    "requires_captions": True,
                    "visual_only_mode": True
                },
                "app_capabilities": {
                    "app_name": "MyApp",
                    "app_version": "1.0.0",
                    "supports_sign_language": True,
                    "supports_captions": True,
                    "supports_visual_only": True,
                    "spec_version": "1.0.0"
                },
                "context_type": "standard"
            }
        }


class AccessibilityContext(BaseModel):
    """Initialized accessibility context response."""
    
    context_id: str = Field(..., description="Unique context identifier")
    user_preferences: AccessibilityPreferences = Field(..., description="User preferences")
    app_capabilities: AppCapabilities = Field(..., description="App capabilities")
    constraints: ContextConstraints = Field(..., description="Context constraints and defaults")
    compatibility_score: float = Field(..., ge=0.0, le=1.0, description="Compatibility score between preferences and capabilities")
    warnings: List[str] = Field(default_factory=list, description="Compatibility warnings")
    timestamp: str = Field(..., description="Context creation timestamp (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "context_id": "ctx_abc123",
                "user_preferences": {
                    "requires_sign_language": True,
                    "requires_captions": True,
                    "visual_only_mode": True
                },
                "app_capabilities": {
                    "app_name": "MyApp",
                    "app_version": "1.0.0",
                    "supports_sign_language": True,
                    "supports_captions": True,
                    "supports_visual_only": True,
                    "spec_version": "1.0.0"
                },
                "constraints": {
                    "required_capabilities": ["captions"],
                    "recommended_capabilities": ["sign_language_support"]
                },
                "compatibility_score": 0.95,
                "warnings": [],
                "timestamp": "2025-12-20T18:03:00Z"
            }
        }
