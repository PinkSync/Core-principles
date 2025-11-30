"""User-related data models for PinkSync API."""

from typing import List, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile for DEAF FIRST services."""
    
    name: str = Field(..., description="User's name")
    needs_financial_help: bool = Field(False, description="Whether user needs financial assistance")
    is_business_owner: bool = Field(False, description="Whether user is a business owner")
    needs_healthcare_help: bool = Field(False, description="Whether user needs healthcare assistance")
    location: str = Field("", description="User's location")
    financial_goals: List[str] = Field(default_factory=list, description="User's financial goals")
    preferred_communication: str = Field("text-heavy", description="Preferred communication method")
    connected_banks: Optional[List[str]] = Field(default_factory=list, description="Connected bank accounts")
    insurance_policies: Optional[List[str]] = Field(default_factory=list, description="Insurance policies")
    tax_software: Optional[str] = Field(None, description="Preferred tax software")
    legal_documents: Optional[List[str]] = Field(default_factory=list, description="Legal documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Maria",
                "needs_financial_help": True,
                "is_business_owner": True,
                "needs_healthcare_help": True,
                "location": "Fort Worth, TX",
                "financial_goals": ["Buy house", "Start business", "Plan retirement"],
                "preferred_communication": "text-heavy"
            }
        }


class UserExperience(BaseModel):
    """Feedback model for service experience."""
    
    rating: int = Field(..., ge=1, le=5, description="Overall rating (1-5)")
    accessibility_score: int = Field(..., ge=1, le=10, description="Accessibility score (1-10)")
    deaf_friendliness: int = Field(..., ge=1, le=10, description="Deaf friendliness score (1-10)")
    suggested_improvements: Optional[str] = Field("", description="Suggested improvements")
    would_recommend: bool = Field(True, description="Would recommend to others")
    alternatives_needed: Optional[str] = Field("", description="Alternative services needed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "accessibility_score": 9,
                "deaf_friendliness": 10,
                "suggested_improvements": "Add more ASL video content",
                "would_recommend": True,
                "alternatives_needed": ""
            }
        }
