"""Core validators for DEAF FIRST accessibility checking."""

from typing import Dict, Any
import re


# DEAF FIRST requirements for service validation
DEAF_FIRST_REQUIREMENTS = {
    "text_based_primary": "Text is the primary interface",
    "visual_indicators": "Visual feedback for everything",
    "no_audio_requirements": "Never requires hearing",
    "flexible_pacing": "User controls speed/timing",
    "rich_context": "Provides full situational context",
    "cultural_competency": "Understands deaf culture",
    "accessibility_first": "Built for accessibility, not retrofitted"
}


def validate_deaf_first_service(service: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quality assurance - all services must be DEAF FIRST.
    
    Args:
        service: Service configuration dictionary
        
    Returns:
        Validation result with score and details
    """
    features = service.get("features", [])
    
    results = {}
    passed = 0
    total = len(DEAF_FIRST_REQUIREMENTS)
    
    for req_key, req_desc in DEAF_FIRST_REQUIREMENTS.items():
        is_passed = req_key in features or service.get(req_key, False)
        results[req_key] = {
            "passed": is_passed,
            "description": req_desc
        }
        if is_passed:
            passed += 1
    
    return {
        "is_valid": passed == total,
        "score": int((passed / total) * 100),
        "passed": passed,
        "total": total,
        "details": results
    }


def validate_url(url: str) -> Dict[str, Any]:
    """
    Validate a URL for deaf accessibility.
    
    Args:
        url: URL to validate
        
    Returns:
        Validation result with scores
    """
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return {
            "url": url,
            "valid": False,
            "error": "Invalid URL format",
            "deaf_score": 0,
            "asl_compatible": False,
            "audio_issues_found": True
        }
    
    # Simulated accessibility check
    # In production, this would make actual HTTP requests and analyze the page
    deaf_score = 85  # Default score
    asl_compatible = True
    audio_issues_found = False
    
    # Check for known accessibility-friendly domains
    accessibility_keywords = ["deaf", "asl", "accessible", "a11y", "pinksync"]
    if any(kw in url.lower() for kw in accessibility_keywords):
        deaf_score = 95
    
    return {
        "url": url,
        "valid": True,
        "deaf_score": deaf_score,
        "asl_compatible": asl_compatible,
        "audio_issues_found": audio_issues_found
    }


def validate_batch(urls: list) -> list:
    """
    Validate multiple URLs for deaf accessibility.
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        List of validation results
    """
    return [validate_url(url) for url in urls]
