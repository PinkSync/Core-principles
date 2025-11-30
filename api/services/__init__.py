"""PinkSync Services - Comprehensive DEAF FIRST service definitions."""

from typing import Dict, Any

# Import biometric and subscription services
from .biometric import ASLBiometricService, asl_biometric_service
from .stripe_subscription import StripeSubscriptionService, stripe_service


class PinkSyncServices:
    """
    PinkSync Services for DEAF FIRST Platform.
    Building what WE understand, not fitting into THEIR system.
    Middleware for all networks of accessibility partners and services.
    """

    def __init__(self):
        """Initialize PinkSync services."""
        self.services = self._build_services()

    def _build_services(self) -> Dict[str, Any]:
        """Build comprehensive service catalog."""
        return {
            # COMMUNICATION SERVICES
            "communication": {
                "visual_chat": {
                    "text_based": True,
                    "rich_formatting": True,
                    "file_sharing": True,
                    "screen_sharing": True,
                    "whiteboard": True
                },
                "asl_video_call": {
                    "high_definition": True,
                    "low_latency": True,
                    "adjustable_lighting": True,
                    "background_blur": True,
                    "multiple_angles": True
                },
                "text_relay": {
                    "phone_to_text": True,
                    "text_to_phone": True,
                    "conference_relay": True,
                    "emergency_relay": True
                },
                "document_services": {
                    "legal_document_review": True,
                    "contract_explainer": True,
                    "government_form_help": True,
                    "medical_document_translation": True
                }
            },
            # FINANCIAL SERVICES
            "financial": {
                "tax_services": {
                    "visual_tax_prep": True,
                    "deaf_tax_advisor": True,
                    "irs_correspondence_help": True,
                    "audit_support": True,
                    "text_based_tax_interview": True
                },
                "insurance_services": {
                    "policy_explainer": True,
                    "claims_assistance": True,
                    "compare_tool": True,
                    "renewal_reminders": True,
                    "dispute_help": True
                },
                "real_estate_services": {
                    "property_search": True,
                    "mortgage_guidance": True,
                    "contract_review": True,
                    "inspection_reports": True,
                    "closing_support": True
                },
                "financial_planning": {
                    "budget_visualizer": True,
                    "investment_education": True,
                    "retirement_planning": True,
                    "debt_management": True,
                    "savings_goals": True
                }
            },
            # ACCESSIBILITY SERVICES
            "accessibility": {
                "captioning": {
                    "live_captions": True,
                    "meeting_transcripts": True,
                    "phone_call_captions": True,
                    "broadcast_captions": True,
                    "custom_vocabulary": True
                },
                "visual_alerts": {
                    "sound_to_light": True,
                    "vibration_patterns": True,
                    "flashing_notifications": True,
                    "color_coded_alerts": True,
                    "custom_alert_tones": True
                },
                "environmental_awareness": {
                    "sound_detection": True,
                    "direction_indicators": True,
                    "proximity_alerts": True,
                    "safety_notifications": True
                }
            },
            # EDUCATION SERVICES
            "education": {
                "asl_education": {
                    "vocabulary_builder": True,
                    "grammar_lessons": True,
                    "practice_partners": True,
                    "skill_assessment": True
                },
                "financial_education": {
                    "basic_banking": True,
                    "credit_education": True,
                    "investment_basics": True,
                    "tax_literacy": True,
                    "insurance_education": True
                },
                "tech_training": {
                    "digital_literacy": True,
                    "accessibility_tools": True,
                    "smartphone_optimization": True,
                    "emergency_tech": True
                }
            },
            # PROFESSIONAL SERVICES
            "professional": {
                "legal_services": {
                    "legal_document_review": True,
                    "court_interpreter": True,
                    "rights_education": True,
                    "advocacy_support": True,
                    "legal_research": True
                },
                "healthcare_services": {
                    "appointment_support": True,
                    "medical_interpreter": True,
                    "insurance_navigation": True,
                    "prescription_help": True,
                    "health_record_management": True
                },
                "employment_services": {
                    "job_search_assistance": True,
                    "resume_review": True,
                    "interview_prep": True,
                    "workplace_advocacy": True,
                    "career_development": True
                }
            },
            # COMMUNITY SERVICES
            "community": {
                "networking": {
                    "local_events": True,
                    "professional_groups": True,
                    "mentorship_programs": True,
                    "business_networking": True
                },
                "resource_sharing": {
                    "recommended_services": True,
                    "review_system": True,
                    "experience_sharing": True,
                    "warning_system": True  # Alert about non-deaf-friendly services
                },
                "advocacy": {
                    "rights_education": True,
                    "discrimination_reporting": True,
                    "legal_support": True,
                    "community_organizing": True
                }
            },
            # EMERGENCY SERVICES
            "emergency": {
                "emergency_comm": {
                    "text_to_911": True,
                    "video_emergency_call": True,
                    "medical_alert": True,
                    "location_sharing": True
                },
                "crisis_support": {
                    "mental_health_support": True,
                    "financial_crisis": True,
                    "legal_emergency": True,
                    "family_emergency": True
                }
            },
            # BUSINESS SERVICES (For deaf entrepreneurs)
            "business": {
                "business_dev": {
                    "business_plan_review": True,
                    "funding_guidance": True,
                    "marketing_help": True,
                    "legal_structuring": True
                },
                "business_financial": {
                    "bookkeeping_setup": True,
                    "tax_preparation": True,
                    "cash_flow_management": True,
                    "investor_relations": True
                }
            }
        }

    def get_all_services(self) -> Dict[str, Any]:
        """Return all available services."""
        return self.services

    def get_service_category(self, category: str) -> Dict[str, Any]:
        """Get services by category."""
        return self.services.get(category, {})

    def get_service_names(self, category: str = None) -> list:
        """Get list of service names, optionally filtered by category."""
        if category:
            cat_services = self.services.get(category, {})
            return list(cat_services.keys())
        
        all_names = []
        for cat, services in self.services.items():
            all_names.extend(list(services.keys()))
        return all_names


# Service discovery mapping
SERVICE_DISCOVERY_MAP = {
    # Financial queries
    "tax help": ["Visual Tax Prep", "IRS Correspondence Help", "Deaf Tax Advisor"],
    "insurance question": ["Policy Explainer", "Claims Assistance", "Compare Tool"],
    "buying house": ["Property Search", "Mortgage Guidance", "Contract Review"],
    "budget help": ["Budget Visualizer", "Debt Management", "Savings Goals"],
    
    # Legal queries
    "contract review": ["Legal Document Review", "Rights Education", "Advocacy Support"],
    "rights violation": ["Discrimination Reporting", "Legal Support", "Advocacy"],
    "workplace issue": ["Workplace Advocacy", "Job Search Assistance", "Career Development"],
    
    # Healthcare queries
    "doctor appointment": ["Appointment Support", "Medical Interpreter", "Health Record Management"],
    "medical bills": ["Insurance Navigation", "Claims Assistance", "Dispute Help"],
    
    # Emergency queries
    "emergency": ["Text to 911", "Video Emergency Call", "Medical Alert", "Location Sharing"],
    "crisis": ["Mental Health Support", "Financial Crisis", "Legal Emergency", "Family Emergency"],
    
    # Business queries
    "start business": ["Business Plan Review", "Funding Guidance", "Legal Structuring"],
    "business taxes": ["Bookkeeping Setup", "Tax Preparation", "Cash Flow Management"]
}


def discover_services(query: str) -> dict:
    """Discover services based on user query."""
    query_lower = query.lower()
    
    matched = SERVICE_DISCOVERY_MAP.get(query_lower, [])
    
    # Find alternative services if no exact match
    alternatives = []
    if not matched:
        for key, services in SERVICE_DISCOVERY_MAP.items():
            if any(word in query_lower for word in key.split()):
                alternatives.extend(services)
    
    return {
        "matched_services": matched,
        "alternative_services": alternatives[:5],  # Limit to 5 alternatives
        "community_recommendations": []  # Placeholder for community recommendations
    }
