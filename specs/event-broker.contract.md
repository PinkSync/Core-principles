# Event Broker Contract

**Version:** 1.0.0  
**Status:** Constitutional  
**Last Updated:** 2025-12-20

## Purpose

This contract defines the binding interface between applications, the PinkSync broker, and accessibility consumers. If it's not spec'd here, it doesn't exist.

## Contract Scope

PinkSync is an **accessibility API broker** with a hard contract. It brokers accessibility intents, capabilities, and compliance signals between apps, users, and agents—without owning the app itself.

### What PinkSync Does ✅

- Accepts accessibility events from applications
- Normalizes them into PinkSync contracts
- Routes them to subscribed consumers (UIs, agents, logs, validators)
- Enforces contract shape via type-safe validation
- Emits machine-verifiable signals
- Produces structured logs for compliance auditing

### What PinkSync Does NOT Do ❌

- Does NOT render UI
- Does NOT generate video or visual content
- Does NOT decide morality or make subjective judgments
- Does NOT own or control the source applications
- Does NOT store user data beyond operational logs

## Core Entities

### 1. Accessibility Event

A **declared need, state, or capability**. Not feelings. Signals.

**Schema Reference:** `accessibility-intent.schema.json`

**Examples:**
- `visual_only_mode` - Application must function without audio
- `sign_language_required` - ASL or sign language interface needed
- `reduced_motion` - Minimize animations
- `captions_mandatory` - All media must have captions

### 2. Capability Declaration

Applications **MUST** declare their accessibility capabilities at startup.

**Properties:**
- `app_id` (REQUIRED): Unique application identifier
- `capabilities` (REQUIRED): Array of supported accessibility intents
- `compliance_level` (REQUIRED): bronze | silver | gold | platinum
- `version` (REQUIRED): Application version string

### 3. Event Subscription

Consumers **MAY** subscribe to accessibility events.

**Properties:**
- `consumer_id` (REQUIRED): Unique consumer identifier
- `event_types` (REQUIRED): Array of event types to receive
- `webhook_url` (OPTIONAL): URL to receive event notifications
- `filter` (OPTIONAL): Filter criteria for events

## API Endpoints

### POST /v1/events

**Purpose:** Accept accessibility events from applications

**Request Contract:**
```json
{
  "app_id": "string (REQUIRED)",
  "user_id": "string | null (OPTIONAL)",
  "intent": "enum (REQUIRED)",
  "timestamp": "ISO 8601 (REQUIRED)",
  "metadata": "object (OPTIONAL)",
  "compliance_level": "enum (OPTIONAL)"
}
```

**Response Contract:**
```json
{
  "event_id": "string",
  "status": "accepted | rejected",
  "timestamp": "ISO 8601",
  "signature": "string (cryptographic signature)",
  "ledger_id": "string (optional)"
}
```

**Status Codes:**
- `201` - Event accepted and queued
- `400` - Invalid event format (contract violation)
- `401` - Unauthorized app_id
- `429` - Rate limit exceeded
- `500` - Broker failure

### GET /v1/capabilities

**Purpose:** List all registered application capabilities

**Query Parameters:**
- `app_id` (OPTIONAL): Filter by specific application
- `compliance_level` (OPTIONAL): Filter by compliance level
- `intent` (OPTIONAL): Filter by supported intent

**Response Contract:**
```json
{
  "capabilities": [
    {
      "app_id": "string",
      "capabilities": ["string"],
      "compliance_level": "enum",
      "version": "string",
      "registered_at": "ISO 8601"
    }
  ],
  "total": "integer"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid query parameters
- `500` - Broker failure

### POST /v1/subscribe

**Purpose:** Subscribe to accessibility events

**Request Contract:**
```json
{
  "consumer_id": "string (REQUIRED)",
  "event_types": ["string"] (REQUIRED),
  "webhook_url": "string (OPTIONAL)",
  "filter": {
    "app_ids": ["string"],
    "intents": ["string"],
    "compliance_levels": ["string"]
  }
}
```

**Response Contract:**
```json
{
  "subscription_id": "string",
  "status": "active",
  "created_at": "ISO 8601",
  "expires_at": "ISO 8601 (OPTIONAL)"
}
```

**Status Codes:**
- `201` - Subscription created
- `400` - Invalid subscription request
- `401` - Unauthorized consumer
- `409` - Subscription already exists
- `500` - Broker failure

### GET /v1/compliance/{app_id}

**Purpose:** Check compliance status for an application

**Path Parameters:**
- `app_id` (REQUIRED): Application identifier

**Query Parameters:**
- `detailed` (OPTIONAL): Include detailed compliance report

**Response Contract:**
```json
{
  "app_id": "string",
  "compliance_level": "enum",
  "status": "compliant | non-compliant | pending",
  "last_audit": "ISO 8601",
  "events_count": "integer",
  "violations": [
    {
      "type": "string",
      "severity": "string",
      "timestamp": "ISO 8601"
    }
  ],
  "certificate_url": "string (OPTIONAL)"
}
```

**Status Codes:**
- `200` - Compliance data retrieved
- `404` - Application not registered
- `500` - Broker failure

## Compliance Without Vibes

Every request produces:
- **Structured log** - Machine-readable event log
- **Signed response** - Cryptographically signed for verification
- **Optional ledger write** - Immutable audit trail

This enables:
- ✅ CI enforcement in build pipelines
- ✅ Partner audits and certification
- ✅ App Store eligibility requirements
- ✅ Regulatory proof and compliance reports

## Integration Requirements

### Application Responsibilities

Applications integrating with PinkSync **MUST**:

1. **Declare capabilities** at startup via registration
2. **Emit events** at runtime when accessibility needs change
3. **Respect constraints** returned by the broker
4. **Implement fallbacks** for unsupported intents
5. **Maintain versioning** of their accessibility contract

### Consumer Responsibilities

Consumers (UIs, agents, validators) **MUST**:

1. **Subscribe** to relevant event types
2. **Process events** within defined SLA (typically < 1 second)
3. **Acknowledge receipt** via callback or poll
4. **Handle failures** gracefully with retries

## Contract Versioning

Contract versions follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to contract structure
- **MINOR**: Backward-compatible additions
- **PATCH**: Documentation or clarification updates

**Current Version:** `1.0.0`

## RFC Language

This contract uses RFC 2119 language:

- **MUST** / **REQUIRED**: Absolute requirement
- **SHOULD** / **RECOMMENDED**: Strong recommendation, exceptions allowed with justification
- **MAY** / **OPTIONAL**: Truly optional, discretionary

## Enforcement

Contract violations **WILL**:
- Return `400 Bad Request` with detailed error
- Be logged for audit purposes
- Impact compliance rating if repeated
- May result in app suspension for severe violations

## Support

For contract clarifications or disputes:
- GitHub Issues: `pinksync/specs`
- Email: contracts@pinksync.org
- RFC Process: Submit proposal for contract amendments

---

*This contract is law. Read it like it will be read in court.*

**Contract Authority:** PinkSync Governance Board  
**Next Review:** Quarterly or upon major incident
