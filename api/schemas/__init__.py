"""
PinkSync API Schemas
Pydantic models for requests and responses
"""

from .accessibility import (
    AccessibilityContext,
    AccessibilityContextRequest,
    AccessibilityPreferences,
    AppCapabilities,
    ContextConstraints
)
from .capabilities import (
    CapabilityDeclaration,
    CapabilityQuery,
    CapabilityResponse,
    ProviderInfo,
    SpecVersion
)
from .compliance import (
    ComplianceResult,
    ValidationReport,
    ValidationTarget,
    SignedValidationReport
)
from .events import (
    AccessibilityEvent,
    EventType,
    EventBatch,
    EventResponse
)
from .feedback import (
    DiscrepancyReport,
    FalsePositiveReport,
    UserMismatchReport,
    SignalCorrection
)

__all__ = [
    # Accessibility
    "AccessibilityContext",
    "AccessibilityContextRequest",
    "AccessibilityPreferences",
    "AppCapabilities",
    "ContextConstraints",
    # Capabilities
    "CapabilityDeclaration",
    "CapabilityQuery",
    "CapabilityResponse",
    "ProviderInfo",
    "SpecVersion",
    # Compliance
    "ComplianceResult",
    "ValidationReport",
    "ValidationTarget",
    "SignedValidationReport",
    # Events
    "AccessibilityEvent",
    "EventType",
    "EventBatch",
    "EventResponse",
    # Feedback
    "DiscrepancyReport",
    "FalsePositiveReport",
    "UserMismatchReport",
    "SignalCorrection",
]
