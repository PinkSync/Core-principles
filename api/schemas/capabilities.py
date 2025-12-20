"""
Capability Registry Schemas
Schemas for capability discovery and provider registry
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class SpecVersion(BaseModel):
    """Specification version information."""
    
    version: str = Field(..., description="Version string (e.g., '1.0.0')")
    spec_url: Optional[str] = Field(None, description="URL to specification document")
    compliance_level: str = Field("full", description="Compliance level (full, partial, none)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0.0",
                "spec_url": "https://specs.pinksync.org/accessibility/1.0.0",
                "compliance_level": "full"
            }
        }


class ProviderInfo(BaseModel):
    """Information about a capability provider."""
    
    provider_id: str = Field(..., description="Unique provider identifier")
    provider_name: str = Field(..., description="Provider name")
    provider_type: str = Field(..., description="Provider type (service, app, platform)")
    capabilities: List[str] = Field(default_factory=list, description="List of supported capabilities")
    spec_version: SpecVersion = Field(..., description="Spec version compliance")
    endpoint: Optional[str] = Field(None, description="Provider API endpoint")
    status: str = Field("active", description="Provider status (active, inactive, deprecated)")
    last_validated: Optional[str] = Field(None, description="Last validation timestamp (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider_id": "provider_123",
                "provider_name": "Visual Communication Service",
                "provider_type": "service",
                "capabilities": ["visual_chat", "asl_video_call", "text_relay"],
                "spec_version": {
                    "version": "1.0.0",
                    "compliance_level": "full"
                },
                "endpoint": "https://api.example.com/v1",
                "status": "active",
                "last_validated": "2025-12-20T18:00:00Z"
            }
        }


class CapabilityDeclaration(BaseModel):
    """Declaration of a capability by a provider."""
    
    capability_name: str = Field(..., description="Capability name")
    capability_type: str = Field(..., description="Capability type (communication, visual, audio, etc.)")
    description: str = Field(..., description="Capability description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Capability parameters")
    required_features: List[str] = Field(default_factory=list, description="Required features for this capability")
    
    class Config:
        json_schema_extra = {
            "example": {
                "capability_name": "sign_language_support",
                "capability_type": "visual",
                "description": "Support for ASL video communication",
                "parameters": {
                    "video_quality": "HD",
                    "latency": "low"
                },
                "required_features": ["video_streaming", "low_latency_mode"]
            }
        }


class CapabilityQuery(BaseModel):
    """Query for discovering capabilities."""
    
    capability_type: Optional[str] = Field(None, description="Filter by capability type")
    required_features: Optional[List[str]] = Field(None, description="Required features")
    spec_version: Optional[str] = Field(None, description="Minimum spec version")
    provider_type: Optional[str] = Field(None, description="Filter by provider type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "capability_type": "visual",
                "required_features": ["captions", "high_contrast"],
                "spec_version": "1.0.0",
                "provider_type": "service"
            }
        }


class CapabilityResponse(BaseModel):
    """Response for capability discovery."""
    
    capabilities: List[CapabilityDeclaration] = Field(default_factory=list, description="Discovered capabilities")
    providers: List[ProviderInfo] = Field(default_factory=list, description="Providers supporting these capabilities")
    total_count: int = Field(0, description="Total number of matching capabilities")
    query_timestamp: str = Field(..., description="Query execution timestamp (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "capabilities": [
                    {
                        "capability_name": "sign_language_support",
                        "capability_type": "visual",
                        "description": "ASL video support"
                    }
                ],
                "providers": [
                    {
                        "provider_id": "provider_123",
                        "provider_name": "Visual Service",
                        "provider_type": "service",
                        "capabilities": ["sign_language_support"],
                        "spec_version": {"version": "1.0.0", "compliance_level": "full"},
                        "status": "active"
                    }
                ],
                "total_count": 1,
                "query_timestamp": "2025-12-20T18:03:00Z"
            }
        }
