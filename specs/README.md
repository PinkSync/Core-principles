# PinkSync Specifications

**Version:** 1.0.0  
**Status:** Constitutional  
**Last Updated:** 2025-12-20

## Overview

This directory contains the **source of truth** for PinkSync accessibility contracts. These specifications define the hard contracts between applications, the PinkSync broker, and accessibility consumers.

> **If it's not spec'd here, it doesn't exist.**

## Philosophy

PinkSync is not a feature. PinkSync is an **accessibility API broker with a hard contract**.

Think: **Stripe, but for accessibility signals. Twilio, but for Deaf-first interaction states.**

### PinkSync's Core Role

PinkSync brokers accessibility intents, capabilities, and compliance signals between apps, users, and agents—without owning the app itself.

## Specification Files

### 1. `accessibility-intent.schema.json`

**Type:** JSON Schema (Draft 07)  
**Purpose:** Constitutional schema for accessibility intent events

Defines the structure for declaring accessibility needs, states, and capabilities. All events submitted to the broker MUST conform to this schema.

**Key Concepts:**
- Intent types (visual_only, sign_language, captions_mandatory, etc.)
- Event metadata and severity levels
- Compliance level tracking
- RFC 2119 language for requirements (MUST/SHOULD/MAY)

**Usage:**
```bash
# Validate an event against the schema
jsonschema -i event.json accessibility-intent.schema.json
```

### 2. `sign-visual-state.schema.json`

**Type:** JSON Schema (Draft 07)  
**Purpose:** Visual requirements for sign language interfaces

Defines video quality, frame rates, lighting, and interaction requirements for sign language communication.

**Key Requirements:**
- Minimum 30 FPS for sign language clarity
- 720p minimum resolution (1080p recommended)
- Lighting and background contrast specifications
- Latency requirements (<150ms for live conversation)

**Usage:**
```bash
# Validate visual state configuration
jsonschema -i visual-state.json sign-visual-state.schema.json
```

### 3. `event-broker.contract.md`

**Type:** Markdown specification (RFC-style)  
**Purpose:** API contract for the PinkSync broker

The binding interface between applications, the broker, and consumers. Written in RFC 2119 language (MUST/SHOULD/MAY) like it will be read in court.

**Defines:**
- API endpoint contracts (POST /v1/events, GET /v1/capabilities, etc.)
- Request/response formats
- Status codes and error handling
- Compliance and auditing requirements

**Key Quote:**
> "This contract is law. Read it like it will be read in court."

### 4. `compliance-levels.md`

**Type:** Markdown specification  
**Purpose:** Defines Bronze, Silver, Gold, and Platinum compliance levels

Measurable, verifiable, and enforceable compliance standards for accessibility.

**Levels:**
- **Bronze** - Foundation (bare minimum to not be hostile)
- **Silver** - Functional (actually usable for deaf users)
- **Gold** - Optimized (designed with deaf users in mind)
- **Platinum** - Excellence (setting the standard for the industry)

**Usage:**
- Applications self-assess current level
- Implement requirements for target level
- Request PinkSync audit for certification

## Versioning

All specifications follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR** - Breaking changes to contract structure
- **MINOR** - Backward-compatible additions
- **PATCH** - Documentation or clarification updates

**Current Version:** `1.0.0`

## RFC Language

These specifications use RFC 2119 language:

- **MUST** / **REQUIRED** - Absolute requirement
- **SHOULD** / **RECOMMENDED** - Strong recommendation, exceptions allowed with justification
- **MAY** / **OPTIONAL** - Truly optional, discretionary

## Implementation

### For Application Developers

1. Read `event-broker.contract.md` to understand the API
2. Review `accessibility-intent.schema.json` for event structure
3. Check `compliance-levels.md` to determine your target level
4. Implement event emission at runtime
5. Register with PinkSync broker

### For Consumer Developers

1. Read `event-broker.contract.md` for subscription API
2. Subscribe to relevant event types
3. Process events within SLA (<1 second typically)
4. Acknowledge receipt via callback

### For Validators/Auditors

1. Use JSON schemas for automated validation
2. Review `compliance-levels.md` for audit criteria
3. Check event volume and patterns
4. Verify no critical violations

## OpenAPI Integration

The PinkSync broker automatically generates OpenAPI documentation from these specifications via Pydantic models.

**Access:**
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- JSON schema: `http://localhost:8000/openapi.json`

## Testing

### Validate JSON Schemas

```bash
# Install validator
pip install jsonschema

# Validate accessibility intent
jsonschema -i examples/event.json accessibility-intent.schema.json

# Validate visual state
jsonschema -i examples/visual-state.json sign-visual-state.schema.json
```

### Test API Contracts

```bash
# Submit an event
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -d @examples/event.json

# Check compliance
curl http://localhost:8000/v1/compliance/my-app-id

# List capabilities
curl http://localhost:8000/v1/capabilities
```

## Examples

### Example Accessibility Event

```json
{
  "app_id": "health-portal-v2",
  "user_id": "user-12345",
  "intent": "visual_only",
  "timestamp": "2025-12-20T18:00:00Z",
  "metadata": {
    "severity": "required",
    "context": "emergency_alert",
    "capabilities": ["flash_screen", "vibrate", "large_text"]
  },
  "compliance_level": "gold"
}
```

### Example Visual State

```json
{
  "state_id": "asl-video-call-hd",
  "visual_requirements": {
    "video_quality": "1080p",
    "frame_rate": 60,
    "lighting": {
      "adjustable": true,
      "background_contrast": "high",
      "facial_visibility": true
    }
  },
  "interaction_mode": "live_video",
  "latency_requirements": {
    "max_latency_ms": 100,
    "jitter_tolerance_ms": 20
  },
  "timestamp": "2025-12-20T18:00:00Z"
}
```

## Contributing

### Proposing Changes

1. Open an issue in the repository describing the proposed change
2. If changing contracts, include impact analysis
3. Submit PR with changes to specifications
4. Changes require approval from PinkSync Governance Board

### Writing Standards

- Use RFC 2119 language for normative statements
- Be precise and unambiguous
- Include examples for clarity
- Version appropriately (breaking vs. non-breaking)

### Review Process

1. Technical review by maintainers
2. Community feedback period (7 days)
3. Governance board approval
4. Implementation period before enforcement

## Support

### Questions?

- **Technical Issues:** GitHub Issues
- **Contract Clarifications:** contracts@pinksync.org
- **RFC Proposals:** Submit via GitHub PR
- **Community Discussion:** https://community.pinksync.org

### Resources

- Main Documentation: https://docs.pinksync.org
- API Reference: https://api.pinksync.org/docs
- Community Forum: https://community.pinksync.org
- Status Page: https://status.pinksync.org

## Enforcement

Contract violations:
- Return `400 Bad Request` with detailed error
- Logged for audit purposes
- Impact compliance rating if repeated
- May result in suspension for severe violations

Appeals process available per `event-broker.contract.md`.

---

## What Makes PinkSync Different

### Traditional Approach ❌
- Accessibility added as afterthought
- No machine-verifiable contracts
- Compliance is checkbox exercise
- No audit trail

### PinkSync Approach ✅
- Contract-first accessibility architecture
- Type-safe, machine-verifiable signals
- Measurable, enforceable compliance
- Cryptographically signed audit trail
- Built for deaf community, not retrofitted

---

*These specifications are constitutional. They define what PinkSync is and how it operates.*

**Authority:** PinkSync Governance Board  
**Review Schedule:** Quarterly or upon major incident  
**Next Review:** Q1 2026
