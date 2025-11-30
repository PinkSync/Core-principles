"""ASL Biometric System models for DEAF FIRST platform."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class VerificationStatus(str, Enum):
    """Status of biometric verification."""
    VERIFIED = "verified"
    FAILED = "failed"
    PENDING = "pending"
    EXPIRED = "expired"


class UseCaseCategory(str, Enum):
    """Categories of ASL Biometric use cases."""
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    BUSINESS = "business"
    EDUCATION = "education"
    SOCIAL_SERVICES = "social_services"
    GOVERNMENT = "government"


class BiometricProfile(BaseModel):
    """Stored biometric profile for a user."""
    
    user_id: str = Field(..., description="Unique user identifier")
    profile_type: str = Field("asl_signer", description="Type of biometric profile")
    created_at: Optional[str] = Field(None, description="Profile creation timestamp")
    is_active: bool = Field(True, description="Whether profile is active")


class VerificationRequest(BaseModel):
    """Request model for biometric verification."""
    
    video_data: Optional[str] = Field(None, description="Base64 encoded video data or video URL")
    user_id: str = Field(..., description="User identifier to verify against")
    use_case: UseCaseCategory = Field(..., description="Use case category for this verification")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_data": "https://example.com/video/session123.webm",
                "user_id": "patient_12345",
                "use_case": "healthcare",
                "context": {"appointment_id": "apt_789"}
            }
        }


class VerificationResult(BaseModel):
    """Result of biometric verification."""
    
    verified: bool = Field(..., description="Whether verification passed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    status: VerificationStatus = Field(..., description="Verification status")
    use_case: UseCaseCategory = Field(..., description="Use case category")
    legal_compliance: Optional[str] = Field(None, description="Legal compliance status")
    cost: float = Field(..., description="Cost for this verification")
    timestamp: Optional[str] = Field(None, description="Verification timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "verified": True,
                "confidence": 0.95,
                "status": "verified",
                "use_case": "healthcare",
                "legal_compliance": "HIPAA_ACCESSIBLE",
                "cost": 0.50,
                "timestamp": "2025-11-30T04:57:38Z"
            }
        }


class TelehealthVerification(BaseModel):
    """Model for telehealth consent verification."""
    
    patient_id: str = Field(..., description="Patient identifier")
    appointment_id: str = Field(..., description="Appointment identifier")
    verification_result: VerificationResult = Field(..., description="Verification result")
    medical_record: str = Field("CONSENT_VERIFIED", description="Medical record status")
    cost_per_verification: float = Field(0.50, description="Cost per verification")


class PharmacyVerification(BaseModel):
    """Model for pharmacy prescription pickup verification."""
    
    patient_id: str = Field(..., description="Patient identifier")
    prescription_id: str = Field(..., description="Prescription identifier")
    verified: bool = Field(..., description="Verification status")
    status: str = Field(..., description="Medication status")
    legal_compliance: str = Field("COMPLIANT", description="Legal compliance status")
    cost: float = Field(2.00, description="Cost per verification")


class CourtVerification(BaseModel):
    """Model for court interpreter verification."""
    
    case_id: str = Field(..., description="Court case identifier")
    interpreter_id: str = Field(..., description="Interpreter identifier")
    admissible: bool = Field(..., description="Whether evidence is admissible")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Verification confidence")
    hourly_cost: float = Field(15.00, description="Cost per hour of court time")
    daily_revenue: float = Field(150.00, description="Revenue per court day")


class ExamProctoring(BaseModel):
    """Model for online exam proctoring verification."""
    
    student_id: str = Field(..., description="Student identifier")
    exam_id: str = Field(..., description="Exam identifier")
    exam_valid: bool = Field(..., description="Whether exam is valid")
    academic_integrity: str = Field("MAINTAINED", description="Academic integrity status")
    accommodations: str = Field("DEAF_ACCESSIBLE", description="Accommodations status")
    cost_per_exam: float = Field(10.00, description="Cost per exam")


class GovernmentBenefitsVerification(BaseModel):
    """Model for government benefits authentication."""
    
    recipient_id: str = Field(..., description="Recipient identifier")
    application_id: str = Field(..., description="Application identifier")
    verified: bool = Field(..., description="Verification status")
    status: str = Field("BENEFITS_APPROVED", description="Benefits status")
    fraud_prevention: bool = Field(True, description="Fraud prevention status")
    cost: float = Field(5.00, description="Cost per verification")


class RemoteWorkVerification(BaseModel):
    """Model for remote work attendance tracking."""
    
    employee_id: str = Field(..., description="Employee identifier")
    meeting_id: str = Field(..., description="Meeting identifier")
    attendance_verified: bool = Field(..., description="Attendance verification status")
    billable_hours: float = Field(..., description="Billable hours")
    payroll_status: str = Field("VERIFIED_FOR_PAYMENT", description="Payroll status")
    cost_per_check: float = Field(0.25, description="Cost per check")


class ContractSigningVerification(BaseModel):
    """Model for contract signing verification."""
    
    contract_id: str = Field(..., description="Contract identifier")
    parties_verified: List[str] = Field(default_factory=list, description="Verified party IDs")
    contract_valid: bool = Field(..., description="Contract validity")
    enforcement: str = Field("COURT_ADMISSIBLE", description="Legal enforcement status")
    cost_per_contract: float = Field(25.00, description="Cost per contract")


class ProtectionVerification(BaseModel):
    """Model for domestic violence protection verification."""
    
    case_id: str = Field(..., description="Case identifier")
    victim_id: str = Field(..., description="Victim identifier (anonymized)")
    identity_confirmed: bool = Field(..., description="Identity confirmation status")
    protection_granted: bool = Field(..., description="Protection order status")
    safety_status: str = Field("IDENTITY_CONFIRMED", description="Safety status")


class HousingVerification(BaseModel):
    """Model for housing assistance verification."""
    
    applicant_id: str = Field(..., description="Applicant identifier")
    application_id: str = Field(..., description="Application identifier")
    eligible: bool = Field(..., description="Eligibility status")
    accessibility_confirmed: bool = Field(..., description="Accessibility confirmation")
    funding_compliance: str = Field("HUD_COMPLIANT", description="HUD compliance status")
    cost: float = Field(8.00, description="Cost per verification")


class SpecialEducationTracking(BaseModel):
    """Model for special education compliance tracking."""
    
    student_id: str = Field(..., description="Student identifier")
    session_id: str = Field(..., description="Therapy session identifier")
    participation_verified: bool = Field(..., description="Participation verification")
    compliance: str = Field("IDEA_ACCESSIBLE", description="IDEA compliance status")
    funding_eligibility: str = Field("ELIGIBLE_FOR_REIMBURSEMENT", description="Funding eligibility")
    cost_per_session: float = Field(15.00, description="Cost per session")
