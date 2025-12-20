# PinkSync API - Accessibility Signal Exchange

> **Not a Deaf app. A Deaf-first protocol.**

PinkSync is an accessibility signal exchange infrastructure for deaf accessibility services. It serves as a broker that owns accessibility declarations, capability discovery, validation signals, and compliance artifacts. Everything else is downstream.

## 🎯 Core Authority

PinkSync does NOT own:
- Services
- Dashboards  
- UX decisions

PinkSync owns:
- **Accessibility declarations** - Apps and users declare capabilities and preferences
- **Capability discovery** - Find providers that support specific accessibility features
- **Validation signals** - Machine-readable compliance results against versioned specs
- **Compliance artifacts** - Signed validation reports that can block deployments, unlock badges, or satisfy regulators
- **Accessibility events** - Real-time event stream for monitoring and auditing

When PinkSync can say: **"This app declared X, emitted Y, failed Z"** — it stops being optional.

## 🏗️ Infrastructure Components

### 1. Accessibility Context Initialization
Initialize accessibility contexts for consumer apps or agents through a handshake between app capabilities and user preferences. The broker returns constraints and defaults.

**Think: context handshake, not UI.**

### 2. Capability Registry
Discover what accessibility capabilities exist, which providers claim support, and what version of the spec they comply with.

Eventually: **service === accessibility-capable provider**

### 3. Validation Engine  
Machine-readable compliance checking. Results can block deployments, unlock App Store badges, or satisfy regulators.

**This is infrastructure gravity.**

### 4. Event Stream (The Heart of PinkSync)
Append-only, structured, auditable accessibility events like:
- `user.requires_sign_language`
- `user.enabled_visual_only_mode`
- `app.entered_audio_state`
- `motion_reduced_due_to_preference`

Without events, PinkSync is static. With events, PinkSync becomes real-time infrastructure.

### 5. Signal Correction
Feedback is NOT vibes. It's discrepancy reports, false positives, and user-declared mismatches.

**Signal correction, not opinions.**

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

## 📚 API Endpoints (v1)

All new endpoints are versioned under `/v1/`. Legacy endpoints remain under `/api/` for backward compatibility.

### Accessibility Context

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/context/initialize` | POST | Initialize accessibility context (handshake) |

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

### Initialize Accessibility Context

```python
import httpx

context_request = {
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

```python
import httpx

response = httpx.get(
    "http://localhost:8000/v1/capabilities",
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
PinkSync API - Accessibility Signal Exchange
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
│   ├── services/
│   │   └── __init__.py      # Service definitions
│   ├── validators/
│   │   └── __init__.py      # Accessibility validators
│   └── integrations/
│       └── fibonrose.py     # External integrations
├── frontend/
│   └── components/
│       ├── AITriggerPanel.tsx
│       ├── Dashboard.tsx
│       └── ServiceDiscovery.tsx
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🔗 PinkSync as Infrastructure

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

## 🔗 Integration with 360 Magicians

PinkSync API serves as infrastructure for accessibility-first applications:

1. **Browser Integration**: Embed validation and event tracking in web applications
2. **Docker Deployment**: Run as containerized microservice
3. **API Broker**: Connect multiple accessibility services through standard protocol
4. **DeafAUTH Integration**: Secure authentication for deaf users

## 🤝 Contributing

See [Core.md](Core.md) for core principles and contribution guidelines.

PinkSync is building a **Deaf-first protocol**, not a Deaf app. Contributions should align with this infrastructure-first approach.

## 📜 License

Built with ❤️ for the deaf community.

---

*PinkSync: Not a Deaf app. A Deaf-first protocol.* 🤟

*ACCESSIBILITY SIGNAL EXCHANGE • Infrastructure, not features*
