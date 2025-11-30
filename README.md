# PinkSync API - DEAF FIRST Platform Services

> Building what WE understand, not fitting into THEIR system.

PinkSync API is a comprehensive middleware and API broker for deaf accessibility services. It serves as the backbone for the DEAF FIRST Platform, providing seamless integration with accessibility partners and services.

## 🎯 Core Philosophy

- **Text-based primary**: Text is the primary interface
- **Visual indicators**: Visual feedback for everything  
- **No audio requirements**: Never requires hearing
- **Cultural competency**: Understands deaf culture
- **Accessibility first**: Built for accessibility, not retrofitted

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
├── api/
│   ├── main.py              # FastAPI application
│   ├── models/
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

## 🔗 Integration with 360 Magicians

PinkSync API integrates seamlessly with 360 Business Magician as middleware:

1. **Browser Integration**: Embed components in web applications
2. **Docker Deployment**: Run as containerized microservice
3. **API Broker**: Connect multiple accessibility services
4. **DeafAUTH Integration**: Secure authentication for deaf users

## 🤝 Contributing

See [Core.md](Core.md) for core principles and contribution guidelines.

## 📜 License

Built with ❤️ for the deaf community.

---

*DEAF FIRST • Built for accessibility, not retrofitted* 🤟
