"""
Compliance and Validation Schemas
Schemas for machine-readable compliance results and validation reports
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ValidationTarget(BaseModel):
    """Target for validation."""
    
    target_type: str = Field(..., description="Type of target (url, app, service)")
    target_identifier: str = Field(..., description="Target identifier (URL, app ID, service ID)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional target metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_type": "url",
                "target_identifier": "https://example.app",
                "metadata": {
                    "domain": "example.app",
                    "app_name": "Example App"
                }
            }
        }


class ComplianceResult(BaseModel):
    """Individual compliance check result."""
    
    check_name: str = Field(..., description="Name of the compliance check")
    status: str = Field(..., description="Status (pass, fail, partial, unknown)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this result")
    details: Optional[str] = Field(None, description="Additional details about the result")
    evidence: Optional[List[str]] = Field(default_factory=list, description="Evidence supporting this result")
    
    class Config:
        json_schema_extra = {
            "example": {
                "check_name": "sign_language_support",
                "status": "partial",
                "confidence": 0.85,
                "details": "ASL videos present but no closed captions",
                "evidence": ["video_element_found", "asl_tag_present"]
            }
        }


class ValidationReport(BaseModel):
    """Machine-readable validation report."""
    
    report_id: str = Field(..., description="Unique report identifier")
    target: ValidationTarget = Field(..., description="Validation target")
    spec_version: str = Field(..., description="Spec version used for validation")
    results: Dict[str, ComplianceResult] = Field(default_factory=dict, description="Compliance results by category")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall accessibility score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in results")
    timestamp: str = Field(..., description="Validation timestamp (ISO 8601)")
    validator_version: str = Field(..., description="Validator version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "report_abc123",
                "target": {
                    "target_type": "url",
                    "target_identifier": "https://example.app"
                },
                "spec_version": "1.0.0",
                "results": {
                    "sign_language_support": {
                        "check_name": "sign_language_support",
                        "status": "partial",
                        "confidence": 0.85
                    },
                    "captions": {
                        "check_name": "captions",
                        "status": "pass",
                        "confidence": 0.95
                    },
                    "visual_only_mode": {
                        "check_name": "visual_only_mode",
                        "status": "fail",
                        "confidence": 0.90
                    }
                },
                "overall_score": 0.65,
                "confidence": 0.92,
                "timestamp": "2025-12-20T18:03:00Z",
                "validator_version": "1.0.0"
            }
        }


class SignedValidationReport(BaseModel):
    """Cryptographically signed validation report."""
    
    report: ValidationReport = Field(..., description="The validation report")
    signature: str = Field(..., description="Cryptographic signature of the report")
    signer_id: str = Field(..., description="Identity of the signer")
    signature_algorithm: str = Field("RS256", description="Signature algorithm used")
    certificate_chain: Optional[List[str]] = Field(None, description="Certificate chain for verification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report": {
                    "report_id": "report_abc123",
                    "target": {
                        "target_type": "url",
                        "target_identifier": "https://example.app"
                    },
                    "spec_version": "1.0.0",
                    "results": {},
                    "overall_score": 0.85,
                    "confidence": 0.92,
                    "timestamp": "2025-12-20T18:03:00Z",
                    "validator_version": "1.0.0"
                },
                "signature": "base64_encoded_signature_here",
                "signer_id": "pinksync_validator_001",
                "signature_algorithm": "RS256"
            }
        }
