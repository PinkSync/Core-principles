"""Service-related data models for PinkSync API."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ServiceCategory(BaseModel):
    """Service category configuration."""
    
    name: str = Field(..., description="Category name")
    enabled: bool = Field(True, description="Whether category is enabled")
    features: Dict[str, bool] = Field(default_factory=dict, description="Feature flags")
    priority: str = Field("normal", description="Priority level")
    usage: str = Field("as-needed", description="Usage frequency")


class ServiceResponse(BaseModel):
    """Response model for service discovery."""
    
    matched_services: List[str] = Field(default_factory=list, description="Matched services")
    alternative_services: List[str] = Field(default_factory=list, description="Alternative services")
    community_recommendations: List[str] = Field(default_factory=list, description="Community recommendations")


class DashboardConfig(BaseModel):
    """Dashboard configuration for user."""
    
    dashboard_title: str = Field(..., description="Dashboard title")
    quick_access: List[str] = Field(default_factory=list, description="Quick access items")
    service_categories: Dict[str, List[str]] = Field(default_factory=dict, description="Categorized services")
    personalized_content: Dict[str, Any] = Field(default_factory=dict, description="Personalized content")
    integrations: Dict[str, Any] = Field(default_factory=dict, description="Integration configs")


class ValidationRequest(BaseModel):
    """Request model for AI validation."""
    
    task: str = Field("validate_batch", description="Validation task type")
    urls: List[str] = Field(default_factory=list, description="URLs to validate")


class ValidationResult(BaseModel):
    """Result model for URL validation."""
    
    url: str = Field(..., description="Validated URL")
    deaf_score: int = Field(0, ge=0, le=100, description="Deaf accessibility score")
    asl_compatible: bool = Field(False, description="ASL compatibility")
    audio_issues_found: bool = Field(False, description="Audio dependency issues found")


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    
    status: str = Field("success", description="Validation status")
    results: List[ValidationResult] = Field(default_factory=list, description="Validation results")
