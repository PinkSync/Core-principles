# PinkSync API - Accessibility API Broker

> Building what WE understand, not fitting into THEIR system.

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

## 📚 API Endpoints

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

### Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/initialize-dashboard` | POST | Initialize personalized DEAF FIRST dashboard |

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

### Broker API - Submit Accessibility Event

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

### Initialize Dashboard

```python
import httpx

user_profile = {
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

```python
import httpx

response = httpx.get(
    "http://localhost:8000/api/discover",
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
├── frontend/
│   └── components/
│       ├── AITriggerPanel.tsx
│       ├── Dashboard.tsx
│       └── ServiceDiscovery.tsx
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 📋 Specifications

PinkSync is **contract-first**. All specifications live in `/specs/`:

- **accessibility-intent.schema.json** - JSON Schema for accessibility events
- **sign-visual-state.schema.json** - JSON Schema for sign language visual requirements
- **event-broker.contract.md** - API contract (RFC-style, legally binding)
- **compliance-levels.md** - Bronze/Silver/Gold/Platinum compliance definitions

**See [/specs/README.md](/specs/README.md) for full specifications documentation.**

## 🔗 Integration with 360 Magicians

PinkSync API integrates seamlessly with 360 Business Magician as middleware:

1. **Browser Integration**: Embed components in web applications
2. **Docker Deployment**: Run as containerized microservice
3. **API Broker**: Connect multiple accessibility services
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

## 🤝 Contributing

See [Core.md](Core.md) for core principles and contribution guidelines.

For specification changes, see [/specs/README.md](/specs/README.md).

## 📜 License

Built with ❤️ for the deaf community.

---

*DEAF FIRST • Built for accessibility, not retrofitted* 🤟
