"""
Feedback and Signal Correction Schemas
Schemas for discrepancy reports and signal correction
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DiscrepancyReport(BaseModel):
    """Report of a discrepancy between expected and actual behavior."""
    
    report_id: str = Field(..., description="Unique report identifier")
    report_type: str = Field("discrepancy", description="Type of report")
    target: str = Field(..., description="Target of the discrepancy (URL, app, service)")
    expected_behavior: str = Field(..., description="Expected accessibility behavior")
    actual_behavior: str = Field(..., description="Actual observed behavior")
    severity: str = Field("medium", description="Severity (low, medium, high, critical)")
    timestamp: str = Field(..., description="Report timestamp (ISO 8601)")
    reporter_id: Optional[str] = Field(None, description="ID of the reporter")
    evidence: Optional[List[str]] = Field(default_factory=list, description="Evidence (screenshots, logs, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "disc_abc123",
                "report_type": "discrepancy",
                "target": "https://example.app",
                "expected_behavior": "Captions should appear for all video content",
                "actual_behavior": "Captions missing for embedded videos",
                "severity": "high",
                "timestamp": "2025-12-20T18:03:00Z",
                "reporter_id": "user_456",
                "evidence": ["screenshot_url_1", "log_entry_1"]
            }
        }


class FalsePositiveReport(BaseModel):
    """Report of a false positive in validation results."""
    
    report_id: str = Field(..., description="Unique report identifier")
    validation_report_id: str = Field(..., description="ID of the validation report with false positive")
    check_name: str = Field(..., description="Name of the check that produced false positive")
    reported_status: str = Field(..., description="Status reported by validation (pass, fail, etc.)")
    actual_status: str = Field(..., description="Actual correct status")
    explanation: str = Field(..., description="Explanation of why it's a false positive")
    timestamp: str = Field(..., description="Report timestamp (ISO 8601)")
    reporter_id: Optional[str] = Field(None, description="ID of the reporter")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "fp_abc123",
                "validation_report_id": "report_xyz789",
                "check_name": "sign_language_support",
                "reported_status": "fail",
                "actual_status": "pass",
                "explanation": "ASL videos are present but in a non-standard embed format",
                "timestamp": "2025-12-20T18:03:00Z",
                "reporter_id": "user_456"
            }
        }


class UserMismatchReport(BaseModel):
    """Report of user-declared mismatch between system state and reality."""
    
    report_id: str = Field(..., description="Unique report identifier")
    context_id: Optional[str] = Field(None, description="Associated accessibility context ID")
    mismatch_type: str = Field(..., description="Type of mismatch (preference, capability, feature)")
    system_state: Dict[str, Any] = Field(default_factory=dict, description="What the system thinks")
    actual_state: Dict[str, Any] = Field(default_factory=dict, description="What the user experiences")
    impact: str = Field("medium", description="Impact level (low, medium, high)")
    timestamp: str = Field(..., description="Report timestamp (ISO 8601)")
    user_id: Optional[str] = Field(None, description="ID of the user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "mismatch_abc123",
                "context_id": "ctx_xyz789",
                "mismatch_type": "capability",
                "system_state": {
                    "captions_enabled": True,
                    "caption_quality": "high"
                },
                "actual_state": {
                    "captions_enabled": True,
                    "caption_quality": "low",
                    "caption_accuracy": "poor"
                },
                "impact": "high",
                "timestamp": "2025-12-20T18:03:00Z",
                "user_id": "user_456"
            }
        }


class SignalCorrection(BaseModel):
    """Aggregated signal correction based on feedback."""
    
    correction_id: str = Field(..., description="Unique correction identifier")
    target: str = Field(..., description="Target being corrected (URL, app, service)")
    correction_type: str = Field(..., description="Type of correction (validation, capability, preference)")
    original_value: Any = Field(..., description="Original value/state")
    corrected_value: Any = Field(..., description="Corrected value/state")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in correction")
    source_reports: List[str] = Field(default_factory=list, description="IDs of reports supporting this correction")
    timestamp: str = Field(..., description="Correction timestamp (ISO 8601)")
    status: str = Field("pending", description="Status (pending, applied, rejected)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "correction_id": "corr_abc123",
                "target": "https://example.app",
                "correction_type": "validation",
                "original_value": {
                    "sign_language_support": "fail"
                },
                "corrected_value": {
                    "sign_language_support": "partial"
                },
                "confidence": 0.85,
                "source_reports": ["disc_001", "fp_002"],
                "timestamp": "2025-12-20T18:03:00Z",
                "status": "applied"
            }
        }
