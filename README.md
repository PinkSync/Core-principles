# PinkSync API - Accessibility API Broker

> **Not a Deaf app. A Deaf-first protocol.**

**PinkSync is an accessibility API broker with a hard contract.** We broker accessibility intents, capabilities, and compliance signals between apps, users, and agents—without owning the app itself.

Think: **Stripe, but for accessibility signals. Twilio, but for Deaf-first interaction states.**

## 🎯 What PinkSync Does

### Core Broker (v1) ✅
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
# PinkSync API - DEAF FIRST Platform Services

> Building what WE understand, not fitting into THEIR system.

PinkSync API is a comprehensive middleware and API broker for deaf accessibility services. It serves as the backbone for the DEAF FIRST Platform, providing seamless integration with accessibility partners and services.

## 🎯 Core Philosophy

- **Text-based primary**: Text is the primary interface
- **Visual indicators**: Visual feedback for everything  
- **No audio requirements**: Never requires hearing
- **Cultural competency**: Understands deaf culture
- **Accessibility first**: Built for accessibility, not retrofitted
>>>>>>> 9cdb22b... Add PinkSync API - DEAF FIRST Platform Services with FastAPI, frontend components, Docker, and documentation

## 🚀 Quick Start

### Using Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Python directly

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

<<<<<<< HEAD
## 📚 API Endpoints (v1)

### 🔥 PinkSync Broker API (v1)

The core accessibility event brokering API. **Contract-first, type-safe, async-native.**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/events` | POST | Accept accessibility events from applications |
| `/v1/capabilities` | GET | List registered application capabilities |
| `/v1/subscribe` | POST | Subscribe to accessibility events |
| `/v1/compliance/{app_id}` | GET | Check compliance status for an application |

**Contract Reference:** See [`/specs/event-broker.contract.md`](/specs/event-broker.contract.md)  
**Schema Reference:** See [`/specs/accessibility-intent.schema.json`](/specs/accessibility-intent.schema.json)
I Endpoints
>>>>>>> 9cdb22b... Add PinkSync API - DEAF FIRST Platform Services with FastAPI, frontend components, Docker, and documentation

### Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
<<<<<<< HEAD
| `/v| `/v1/context/initialize` | POST | Initialize accessibility context (handshake) |

### Capability Registry

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/capabilities` | GET | Query capability registry |
| `/v1/providers` | GET | List accessibility providers |

### Validation & Compliance

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/validate` | POST | Validate target for compliance |
| `/v1/validate/batch` | POST | Batch validate multiple targets |

### Accessibility Events

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/events` | POST | Submit accessibility event |
| `/v1/events/batch` | POST | Submit event batch |
| `/v1/events/types` | GET | List supported event types |

### Signal Correction

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/feedback/discrepancy` | POST | Report discrepancy |
| `/v1/feedback/false-positive` | POST | Report false positive |
| `/v1/feedback/mismatch` | POST | Report user mismatch |

### Legacy Endpoints

Legacy endpoints under `/api/` are maintained for backward compatibility but are deprecated. Use `/v1/` endpoints for new integrations.
>>>>>>>+HEAD
itialize-dashboard` | POST | Initialize personalized DEAF FIRST dashboard |

### Service Discovery

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/discover` | GET | Discover services based on query |
| `/api/services` | GET | List all available services |
| `/api/services/{category}` | GET | Get services by category |

### Validation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/py/ai-validate` | POST | AI batch validation for deaf accessibility |
| `/api/validate` | POST | Validate single URL |

### Feedback

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/feedback` | POST | Collect service feedback |
>>>>>>> 9cdb22b... Add PinkSync API - DEAF FIRST Platform Services with FastAPI, frontend components, Docker, and documentation

## 🛠️ Service Categories

### Communication Services
- Visual Chat (text-based, rich formatting, file sharing)
- ASL Video Call (HD, low latency, adjustable lighting)
- Text Relay (phone-to-text, conference relay)
- Document Services (legal review, contract explainer)

### Financial Services
- Tax Services (visual tax prep, deaf tax advisor)
- Insurance Services (policy explainer, claims assistance)
- Real Estate Services (property search, mortgage guidance)
- Financial Planning (budget visualizer, retirement planning)

### Accessibility Services
- Captioning (live captions, meeting transcripts)
- Visual Alerts (sound-to-light, vibration patterns)
- Environmental Awareness (sound detection, safety notifications)

### Education Services
- ASL Education (vocabulary builder, practice partners)
- Financial Education (banking basics, tax literacy)
- Tech Training (digital literacy, accessibility tools)

### Professional Services
- Legal Services (document review, rights education)
- Healthcare Services (appointment support, interpreter)
- Employment Services (job search, resume review)

### Community Services
- Networking (local events, mentorship)
- Resource Sharing (reviews, recommendations)
- Advocacy (rights education, discrimination reporting)

### Emergency Services
- Emergency Communication (text-to-911, video emergency)
- Crisis Support (mental health, financial crisis)

### Business Services
- Business Development (business plan, funding guidance)
- Business Financial (bookkeeping, tax preparation)

## 🔌 Integration Examples

<<<<<<< HEAD
### Broker ### Broker API - Submit Accessibility Event

```python
import httpx
from datetime import datetime

event = {
    "app_id": "my-app-v2",
    "user_id": "user-12345",
    "intent": "visual_only",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "metadata": {
        "severity": "required",
        "context": "emergency_alert",
        "capabilities": ["flash_screen", "vibrate", "large_text"]
    },
    "compliance_level": "gold"
}

response = httpx.post(
    "http://localhost:8000/v1/events",
    json=event
)

# Response includes event_id, signature, and status
result = response.json()
print(f"Event accepted: {result['event_id']}")
print(f"Signature: {result['signature']}")
```

### Broker API - Check Compliance

```python
import httpx

response = httpx.get(
    "http://localhost:8000/v1/compliance/my-app-v2"
)

compliance = response.json()
print(f"Level: {compliance['compliance_level']}")
print(f"Status: {compliance['status']}")
print(f"Events: {compliance['events_count']}")
print(f"Certificate: {compliance['certificate_url']}")
```

### Broker API - Subscribe to Events

```python
import httpx

subscription = {
    "consumer_id": "accessibility-monitor-1",
    "event_types": ["visual_only", "captions_mandatory"],
    "webhook_url": "https://monitor.example.com/webhook",
    "filter": {
        "compliance_levels": ["gold", "platinum"]
    }
}

response = httpx.post(
    "http://localhost:8000/v1/subscribe",
    json=subscription
)

result = response.json()
print(f"Subscription ID: {result['subscription_id']}")
```

>>>>>>>+HEAD
.. Add PinkSync API - DEAF FIRST Platform Services with FastAPI, frontend components, Docker, and documentation
### Initialize Dashboard

```python
import httpx

<<<<<<< HEAD
context_reqcontext_request = {
    "user_preferences": {
        "requires_sign_language": True,
        "requires_captions": True,
        "visual_only_mode": True,
        "high_contrast": True,
        "text_size_preference": "large"
    },
    "app_capabilities": {
        "app_name": "MyApp",
        "app_version": "1.0.0",
        "supports_sign_language": True,
        "supports_captions": True,
        "supports_visual_only": True,
        "supports_high_contrast": True,
        "text_scaling_available": True,
        "spec_version": "1.0.0"
    },
    "context_type": "standard"
}

response = httpx.post(
    "http://localhost:8000/v1/context/initialize",
    json=context_request
)
context = response.json()
print(f"Context ID: {context['context_id']}")
print(f"Compatibility Score: {context['compatibility_score']}")
```

### Query Capabilities
>>>>>>>+HEAD

    "name": "Maria",
    "needs_financial_help": True,
    "is_business_owner": True,
    "needs_healthcare_help": True,
    "location": "Fort Worth, TX",
    "financial_goals": ["Buy house", "Start business"],
    "preferred_communication": "text-heavy"
}

response = httpx.post(
    "http://localhost:8000/api/initialize-dashboard",
    json=user_profile
)
dashboard = response.json()
```

### Discover Services
>>>>>>> 9cdb22b... Add PinkSync API - DEAF FIRST Platform Services with FastAPI, frontend components, Docker, and documentation

```python
import httpx

response = httpx.get(
<<<<<<< HEAD
    "http:/    "http://localhost:8000/v1/capabilities",
    params={"capability_type": "visual"}
)
capabilities = response.json()
```

### Validate Target for Compliance

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/validate",
    params={
        "target_url": "https://example.com",
        "spec_version": "1.0.0"
    }
)
report = response.json()
print(f"Overall Score: {report['overall_score']}")
print(f"Compliance Results: {report['results']}")
```

### Submit Accessibility Event

```python
import httpx
from datetime import datetime

event = {
    "event_id": "evt_abc123",
    "event_type": "user.requires_sign_language",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "source": "user_456",
    "context_id": "ctx_abc123",
    "data": {
        "preference_enabled": True,
        "language": "ASL"
    },
    "metadata": {
        "app_version": "1.0.0",
        "platform": "web"
    }
}

response = httpx.post(
    "http://localhost:8000/v1/events",
    json=event
)
result = response.json()
print(f"Event accepted: {result['status']}")
```

### Report Discrepancy

```python
import httpx

discrepancy = {
    "report_id": "disc_abc123",
    "report_type": "discrepancy",
    "target": "https://example.app",
    "expected_behavior": "Captions should appear for all video content",
    "actual_behavior": "Captions missing for embedded videos",
    "severity": "high",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "evidence": ["screenshot_url_1"]
}

response = httpx.post(
    "http://localhost:8000/v1/feedback/discrepancy",
    json=discrepancy
)
```

### Legacy Example (Deprecated)

```bash
# Use /v1/validate instead
curl -X POST http://localhost:8000/v1/validate \
  -d "target_url=https://example.com&spec_version=1.0.0"
>>>>>>>+HEAD
lhost:8000/api/discover",
    params={"query": "tax help"}
)
services = response.json()
```

### AI Batch Validation

```bash
curl -X POST http://localhost:8000/api/py/ai-validate \
  -H "Content-Type: application/json" \
  -H "X-Magician-Role: accessibility-auditor" \
  -d '{"urls": ["https://example.com", "https://deaf-friendly-site.com"]}'
>>>>>>> 9cdb22b... Add PinkSync API - DEAF FIRST Platform Services with FastAPI, frontend components, Docker, and documentation
```

## 🎨 Frontend Components

### AITriggerPanel

React component for batch accessibility validation:

```tsx
import { AITriggerPanel } from './components/AITriggerPanel';

<AITriggerPanel apiEndpoint="/api/py/ai-validate" />
```

### Dashboard

Personalized DEAF FIRST dashboard:

```tsx
import { Dashboard } from './components/Dashboard';

<Dashboard 
  userProfile={userProfile}
  apiEndpoint="/api/initialize-dashboard" 
/>
```

### ServiceDiscovery

Natural language service search:

```tsx
import { ServiceDiscovery } from './components/ServiceDiscovery';

<ServiceDiscovery apiEndpoint="/api/discover" />
```

## 🏗️ Architecture

```
<<<<<<< HEAD
PinkSync API - AcPinkSync API - Accessibility Signal Exchange
├── api/
│   ├── main.py              # FastAPI application with v1 endpoints
│   ├── schemas/             # Pydantic schemas (new)
│   │   ├── accessibility.py # Context and preferences
│   │   ├── capabilities.py  # Capability registry
│   │   ├── compliance.py    # Validation reports
│   │   ├── events.py        # Event stream schemas
│   │   └── feedback.py      # Signal correction
│   ├── models/              # Legacy models
│   │   ├── user.py          # User profile models
│   │   └── services.py      # Service models
PinkSync API
├── specs/                          # Source of truth - Contract specifications
│   ├── README.md                   # Specifications overview
│   ├── accessibility-intent.schema.json
│   ├── sign-visual-state.schema.json
│   ├── event-broker.contract.md
│   └── compliance-levels.md
├── api/
│   ├── main.py                     # FastAPI application with Broker v1
│   ├── models/
│   │   ├── broker.py               # Broker event models
│   │   ├── user.py                 # User profile models
│   │   └── services.py             # Service models
│   ├── services/
│   │   └── __init__.py             # Service definitions
│   ├── validators/
│   │   └── __init__.py             # Accessibility validators
│   └── integrations/
│       └── fibonrose.py            # External integrations
>>>>>>>+HEAD
s/
│   │   └── __init__.py      # Accessibility validators
│   └── integrations/
│       └── fibonrose.py     # External integrations
>>>>>>> 9cdb22b... Add PinkSync API - DEAF FIRST Platform Services with FastAPI, frontend components, Docker, and documentation
├── frontend/
│   └── components/
│       ├── AITriggerPanel.tsx
│       ├── Dashboard.tsx
│       └── ServiceDiscovery.tsx
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

<<<<<<< HEAD
## 🔗 PinkSync as Infrastructure

PinkSync operates as an **accessibility signal exchange**:

1. **Not a platform** - It's a protocol layer
2. **Not a service** - It's infrastructure that services integrate with
3. **Not optional** - When compliance matters, PinkSync becomes unavoidable

### Key Principle

The moment PinkSync can say:

> "This app declared X, emitted Y, failed Z"

...it stops being optional. This ## 🔗 PinkSync as Infrastructure

PinkSync operates as an **accessibility signal exchange**:

1. **Not a platform** - It's a protocol layer
2. **Not a service** - It's infrastructure that services integrate with
3. **Not optional** - When compliance matters, PinkSync becomes unavoidable

### Key Principle

The moment PinkSync can say:

> "This app declared X, emitted Y, failed Z"

...it stops being optional. This is how PinkSync turns from impressive into inevitable.

## 📊 Versioning Strategy

- **v1 endpoints** (`/v1/*`) - Current, actively maintained
- **Legacy endpoints** (`/api/*`) - Deprecated but maintained for compatibility
- **Spec version** - All validation tied to specific spec versions (e.g., "1.0.0")

New integrations should use `/v1/` endpoints exclusively.
## 📋 Specifications

PinkSync is **contract-first**. All specifications live in `/specs/`:

- **accessibility-intent.schema.json** - JSON Schema for accessibility events
- **sign-visual-state.schema.json** - JSON Schema for sign language visual requirements
- **event-broker.contract.md** - API contract (RFC-style, legally binding)
- **compliance-levels.md** - Bronze/Silver/Gold/Platinum compliance definitions

**See [/specs/README.md](/specs/README.md) for full specifications documentation.**

## 🔗 Integration with 360 Magicians

PinkSync API serves as infrastructure for accessibility-first applications:

1. **Browser Integration**: Embed validation and event tracking in web applications
2. **Docker Deployment**: Run as containerized microservice
3. **API Broker**: Connect multiple accessibility services through standard protocol
4. **DeafAUTH Integration**: Secure authentication for deaf users

## 🎓 Core Philosophy

### Accessibility as Infrastructure

PinkSync treats accessibility not as a feature, but as **infrastructure**. Like Stripe handles payments or Twilio handles communications, PinkSync handles accessibility signals.

### Contract-First Architecture

Every interaction is defined by a contract:
- **Type-safe** - Enforced by Pydantic models
- **Machine-verifiable** - JSON schemas for validation
- **Legally binding** - Written in RFC 2119 language
- **Auditable** - Every event is signed and logged

### What This Enables

- ✅ **CI Enforcement** - Accessibility tests in your build pipeline
- ✅ **Partner Audits** - Machine-readable compliance reports
- ✅ **App Store Eligibility** - Verifiable accessibility certification
- ✅ **Regulatory Proof** - Immutable audit trail for compliance

### The Difference

| Traditional Approach | PinkSync Approach |
|---------------------|-------------------|
| Accessibility added as afterthought | Contract-first architecture |
| Subjective compliance | Machine-verifiable signals |
| Checkbox exercise | Measurable, enforceable standards |
| No audit trail | Cryptographically signed logs |
| Built for hearing, adapted | Built for deaf, by design |

>>>>>>>+HEAD
astAPI, frontend components, Docker, and documentation
## 🤝 Contributing

See [Core.md](Core.md) for core principles and contribution guidelines.

<<<<<<< HEAD
PinkSync is building a **Deaf-first protocol**, not a Deaf app. Contributions should align with this infrastructure-first approach.
For specification changes, see [/specs/README.md](/specs/README.md).

## 📜 License

Built with ❤️ for the deaf community.

---

*PinkSync: Not a Deaf app. A Deaf-first protocol.* 🤟

*ACCESSIBILITY SIGNAL EXCHANGE • Infrastructure, not features*
