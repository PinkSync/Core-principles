#!/usr/bin/env python3
"""
PinkSync Broker API Integration Test

Tests the v1 broker endpoints to ensure they're working correctly.
"""

import httpx
import json
import sys
import uuid
from datetime import datetime


API_BASE = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = httpx.get(f"{API_BASE}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")


def test_submit_event():
    """Test event submission."""
    print("\nTesting event submission...")
    
    event = {
        "app_id": "integration-test-app",
        "user_id": "test-user-123",
        "intent": "visual_only",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metadata": {
            "severity": "required",
            "context": "test_scenario"
        },
        "compliance_level": "bronze"
    }
    
    response = httpx.post(f"{API_BASE}/v1/events", json=event)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "accepted"
    assert "event_id" in data
    assert "signature" in data
    print(f"✓ Event submitted successfully: {data['event_id']}")
    return data["event_id"]


def test_submit_multiple_events(app_id, count=55):
    """Submit multiple events to test compliance level progression."""
    print(f"\nSubmitting {count} events for {app_id}...")
    
    for i in range(count):
        event = {
            "app_id": app_id,
            "intent": "captions_mandatory",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        response = httpx.post(f"{API_BASE}/v1/events", json=event)
        assert response.status_code == 201
    
    print(f"✓ Submitted {count} events successfully")


def test_compliance_check(app_id):
    """Test compliance endpoint."""
    print(f"\nTesting compliance check for {app_id}...")
    
    response = httpx.get(f"{API_BASE}/v1/compliance/{app_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["app_id"] == app_id
    assert data["status"] in ["compliant", "non-compliant", "pending"]
    assert "compliance_level" in data
    assert "events_count" in data
    
    print(f"✓ Compliance check passed")
    print(f"  Level: {data['compliance_level']}")
    print(f"  Status: {data['status']}")
    print(f"  Events: {data['events_count']}")
    if data.get("certificate_url"):
        print(f"  Certificate: {data['certificate_url']}")
    
    return data


def test_list_capabilities():
    """Test capabilities listing."""
    print("\nTesting capabilities listing...")
    
    response = httpx.get(f"{API_BASE}/v1/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert "capabilities" in data
    assert "total" in data
    
    print(f"✓ Capabilities listed: {data['total']} total")


def test_subscribe():
    """Test subscription creation."""
    print("\nTesting subscription creation...")
    
    # Use unique consumer_id to avoid conflicts
    consumer_id = f"integration-test-consumer-{uuid.uuid4().hex[:8]}"
    
    subscription = {
        "consumer_id": consumer_id,
        "event_types": ["visual_only", "captions_mandatory"],
        "webhook_url": "https://test.example.com/webhook",
        "filter": {
            "compliance_levels": ["silver", "gold"]
        }
    }
    
    response = httpx.post(f"{API_BASE}/v1/subscribe", json=subscription)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "active"
    assert "subscription_id" in data
    
    print(f"✓ Subscription created: {data['subscription_id']}")
    return consumer_id


def test_duplicate_subscription(consumer_id):
    """Test that duplicate subscriptions are rejected."""
    print("\nTesting duplicate subscription rejection...")
    
    subscription = {
        "consumer_id": consumer_id,
        "event_types": ["visual_only"]
    }
    
    response = httpx.post(f"{API_BASE}/v1/subscribe", json=subscription)
    assert response.status_code == 409  # Conflict
    
    print("✓ Duplicate subscription properly rejected")


def test_compliance_levels():
    """Test compliance level progression."""
    print("\nTesting compliance level progression...")
    
    # Test Bronze level (10+ events)
    bronze_app = "test-bronze-app"
    test_submit_multiple_events(bronze_app, 12)
    compliance = test_compliance_check(bronze_app)
    assert compliance["compliance_level"] == "bronze"
    print("✓ Bronze level achieved")
    
    # Test Silver level (50+ events)
    silver_app = "test-silver-app"
    test_submit_multiple_events(silver_app, 55)
    compliance = test_compliance_check(silver_app)
    assert compliance["compliance_level"] == "silver"
    print("✓ Silver level achieved")


def main():
    print("PinkSync Broker API Integration Test")
    print("=" * 60)
    
    try:
        # Run tests
        test_health()
        test_submit_event()
        test_list_capabilities()
        consumer_id = test_subscribe()
        test_duplicate_subscription(consumer_id)
        test_compliance_levels()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except httpx.ConnectError:
        print("\n✗ Could not connect to API. Is the server running?")
        print("  Start the server with: uvicorn api.main:app --reload")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
