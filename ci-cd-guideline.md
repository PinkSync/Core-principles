# 🚀 PinkSync CI/CD Setup Guide

Complete guide to implementing continuous deployment for the MBTQ ecosystem.

-----

## 📋 Prerequisites Checklist

- [ ] GitHub repository with admin access
- [ ] Deno Deploy account (free tier works)
- [ ] Slack workspace for notifications
- [ ] GitHub secrets configured
- [ ] Production domains configured

-----

## ⚙️ Step 1: Configure GitHub Secrets

Add these secrets to your repository (`Settings > Secrets and variables > Actions`):

### Required Secrets

```bash
# Deno Deploy
DENO_DEPLOY_TOKEN=<your_deno_deploy_token>

# Slack Notifications
SLACK_WEBHOOK_URL=<your_slack_webhook_url>
SLACK_WEBHOOK_CRITICAL=<your_critical_alerts_webhook>
SLACK_WEBHOOK_PERF=<your_performance_alerts_webhook>
SLACK_WEBHOOK_URGENT=<your_urgent_alerts_webhook>

# API Keys
GROQ_API_KEY=<your_groq_api_key>
ANTHROPIC_API_KEY=<your_anthropic_api_key>
API_TOKEN=<your_pinksync_api_token>

# Chrome Extension (if publishing)
CHROME_EXTENSION_ID=<your_extension_id>
CHROME_CLIENT_ID=<your_chrome_client_id>
CHROME_CLIENT_SECRET=<your_chrome_client_secret>
CHROME_REFRESH_TOKEN=<your_chrome_refresh_token>

# Monitoring
GRAFANA_API_KEY=<your_grafana_api_key>
```

### How to Get Tokens

#### Deno Deploy Token

1. Go to https://dash.deno.com
1. Click your profile → Settings → Access Tokens
1. Create new token with deployment permissions
1. Copy and add to GitHub secrets

#### Slack Webhook

1. Go to https://api.slack.com/apps
1. Create new app → Incoming Webhooks
1. Activate webhooks
1. Create webhook for each channel (critical, performance, urgent)
1. Copy webhook URLs to GitHub secrets

#### Groq API Key

1. Go to https://console.groq.com
1. Create account
1. Generate API key
1. Copy to GitHub secrets

-----

## 🏗️ Step 2: Create Project Structure

```bash
# In your PinkSync repository root

# Create workflows directory
mkdir -p .github/workflows

# Copy the workflow files from artifacts above:
# - deploy-deafauth.yml
# - deploy-vcode.yml
# - deploy-pinkflow.yml
# - deploy-extension.yml
# - monitoring.yml
# - feature-flags.yml
# - user-feedback.yml
# - dependency-updates.yml
```

-----

## 🎯 Step 3: Configure Deno Deploy Projects

For each microservice, create a Deno Deploy project:

```bash
# 1. DeafAUTH
deno deploy --project=pinksync-deafauth services/deafauth/server.ts

# 2. VCode
deno deploy --project=pinksync-vcode services/vcode/server.ts

# 3. PinkFlow
deno deploy --project=pinksync-pinkflow services/pinkflow/server.ts

# 4. Event Orchestrator
deno deploy --project=pinksync-events services/event-orchestrator/server.ts

# 5. RAG Engine
deno deploy --project=pinksync-rag services/rag-engine/server.ts
```

Or use the Deno Deploy dashboard:

1. Go to https://dash.deno.com
1. Click “New Project”
1. Name it `pinksync-deafauth` (etc.)
1. Link to your GitHub repository
1. Set entry point to `services/deafauth/server.ts`

-----

## 🔧 Step 4: Add Health Endpoints

Each service needs a `/health` endpoint for monitoring.

**Example for DeafAUTH** (`services/deafauth/server.ts`):

```typescript
import { serve } from "https://deno.land/std@0.208.0/http/server.ts";

const handler = async (req: Request): Promise<Response> => {
  const url = new URL(req.url);

  // Health check endpoint
  if (url.pathname === "/health") {
    return new Response(
      JSON.stringify({
        status: "healthy",
        service: "deafauth",
        timestamp: new Date().toISOString(),
        version: Deno.env.get("SERVICE_VERSION") || "1.0.0",
      }),
      { 
        status: 200,
        headers: { "Content-Type": "application/json" }
      }
    );
  }

  // Your other routes...
  return new Response("DeafAUTH Service", { status: 200 });
};

serve(handler, { port: 8000 });
```

Add this to **all** microservices:

- `services/deafauth/server.ts`
- `services/vcode/server.ts`
- `services/pinkflow/server.ts`
- `services/event-orchestrator/server.ts`
- `services/rag-engine/server.ts`

-----

## 🎚️ Step 5: Implement Feature Flags

Create a feature flag configuration service.

**Create** `config/feature-flags.ts`:

```typescript
// Feature flag configuration
export interface FeatureFlags {
  ASL_RECOGNITION_V2: boolean;
  GROQ_TRANSCRIPTION: boolean;
  REAL_TIME_CAPTIONS: boolean;
  MEDIAPIPE_ASL: boolean;
  LIVEKIT_VIDEO: boolean;
}

// Get feature flags from environment
export function getFeatureFlags(): FeatureFlags {
  return {
    ASL_RECOGNITION_V2: Deno.env.get("FEATURE_ASL_V2") === "true",
    GROQ_TRANSCRIPTION: Deno.env.get("FEATURE_GROQ") === "true",
    REAL_TIME_CAPTIONS: Deno.env.get("FEATURE_RTC") === "true",
    MEDIAPIPE_ASL: Deno.env.get("FEATURE_MEDIAPIPE") === "true",
    LIVEKIT_VIDEO: Deno.env.get("FEATURE_LIVEKIT") === "true",
  };
}

// Percentage-based rollout
export function isFeatureEnabled(
  flagName: keyof FeatureFlags,
  userId: string
): boolean {
  const flags = getFeatureFlags();
  
  // If flag is globally enabled
  if (flags[flagName]) {
    return true;
  }
  
  // Percentage-based rollout
  const rolloutPercentage = parseInt(
    Deno.env.get(`ROLLOUT_${flagName}`) || "0"
  );
  
  if (rolloutPercentage === 0) return false;
  if (rolloutPercentage === 100) return true;
  
  // Hash user ID to get consistent percentage
  const hash = userId.split("").reduce(
    (acc, char) => acc + char.charCodeAt(0),
    0
  );
  
  return (hash % 100) < rolloutPercentage;
}
```

**Usage in VCode service**:

```typescript
import { isFeatureEnabled } from "../../config/feature-flags.ts";

// In your caption processing endpoint
async function processCaptions(userId: string, videoUrl: string) {
  if (isFeatureEnabled("GROQ_TRANSCRIPTION", userId)) {
    // Use new Groq AI transcription
    return await groqTranscribe(videoUrl);
  } else {
    // Use legacy transcription
    return await legacyTranscribe(videoUrl);
  }
}
```

-----

## 📊 Step 6: Set Up Monitoring Dashboard

### Option A: Grafana Cloud (Free Tier)

1. Sign up at https://grafana.com
1. Create a new stack
1. Add Prometheus data source
1. Import dashboard template

**Create** `.github/grafana-dashboard.json`:

```json
{
  "dashboard": {
    "title": "PinkSync Services",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job='pinksync-services'}"
          }
        ]
      },
      {
        "title": "Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "http_request_duration_seconds"
          }
        ]
      },
      {
        "title": "Caption Processing Speed",
        "type": "graph",
        "targets": [
          {
            "expr": "caption_processing_duration_seconds"
          }
        ]
      }
    ]
  }
}
```

### Option B: Simple Status Page

Create a simple status page using GitHub Actions artifacts:

**Create** `public/status.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PinkSync Status</title>
  <meta http-equiv="refresh" content="60">
  <style>
    body { 
      font-family: system-ui; 
      max-width: 800px; 
      margin: 40px auto;
      padding: 20px;
    }
    .service {
      display: flex;
      justify-content: space-between;
      padding: 15px;
      margin: 10px 0;
      border-radius: 8px;
      background: #f5f5f5;
    }
    .healthy { background: #d4edda; }
    .unhealthy { background: #f8d7da; }
    .status { font-weight: bold; }
  </style>
</head>
<body>
  <h1>🌊 PinkSync System Status</h1>
  <div id="services"></div>
  
  <script>
    async function checkServices() {
      const services = [
        { name: 'DeafAUTH', url: 'https://deafauth.pinksync.io/health' },
        { name: 'VCode', url: 'https://vcode.pinksync.io/health' },
        { name: 'PinkFlow', url: 'https://pinkflow.pinksync.io/health' },
      ];
      
      const container = document.getElementById('services');
      container.innerHTML = '';
      
      for (const service of services) {
        try {
          const response = await fetch(service.url);
          const data = await response.json();
          
          container.innerHTML += `
            <div class="service healthy">
              <span>${service.name}</span>
              <span class="status">✅ Operational</span>
            </div>
          `;
        } catch (error) {
          container.innerHTML += `
            <div class="service unhealthy">
              <span>${service.name}</span>
              <span class="status">❌ Down</span>
            </div>
          `;
        }
      }
    }
    
    checkServices();
  </script>
</body>
</html>
```

-----

## 🔔 Step 7: Configure Slack Notifications

Create a Slack channel structure:

```
#pinksync-deployments     → All deployment notifications
#pinksync-critical        → Critical alerts (service down)
#pinksync-performance     → Performance degradation
#pinksync-user-feedback   → User-reported issues
```

Test your webhooks:

```bash
# Test critical alert
curl -X POST $SLACK_WEBHOOK_CRITICAL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🧪 Test: Critical webhook working",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Test Alert*\nThis is a test of the critical webhook."
        }
      }
    ]
  }'
```

-----

## 🚢 Step 8: First Deployment

Test your CI/CD pipeline:

```bash
# 1. Make a small change to DeafAUTH
cd services/deafauth
echo "// Test change" >> server.ts

# 2. Commit and push
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main

# 3. Watch the magic happen:
# - GitHub Actions runs tests
# - Security scan completes
# - Service deploys to Deno Deploy
# - Health check confirms success
# - Slack notification sent
```

-----

## 📈 Step 9: Monitor Deployment

1. Go to GitHub Actions tab
1. Watch the workflow run
1. Check Slack for notifications
1. Verify service health: `curl https://deafauth.pinksync.io/health`

-----

## 🎯 Step 10: User Feedback Integration

Create a webhook endpoint to receive user feedback:

**Add to** `services/api-broker/routes/feedback.ts`:

```typescript
import { serve } from "https://deno.land/std@0.208.0/http/server.ts";

const handler = async (req: Request): Promise<Response> => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const feedback = await req.json();
  
  // Send to GitHub Actions via repository_dispatch
  await fetch(
    `https://api.github.com/repos/pinkycollie/pinksync/dispatches`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${Deno.env.get("GITHUB_TOKEN")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        event_type: "user_feedback",
        client_payload: {
          type: feedback.type,
          text: feedback.message,
          user_id: feedback.userId,
          timestamp: new Date().toISOString(),
        },
      }),
    }
  );

  return new Response(
    JSON.stringify({ success: true }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
};

serve(handler, { port: 8001 });
```

-----

## ✅ Testing Checklist

After setup, test these scenarios:

### Deployment Testing

- [ ] Push to `main` triggers deployment
- [ ] Failed tests block deployment
- [ ] Health checks work
- [ ] Slack notifications arrive

### Feature Flag Testing

- [ ] Can enable feature for 10% of users
- [ ] Can disable feature instantly
- [ ] Flags persist across deployments

### Monitoring Testing

- [ ] Health checks run every 15 minutes
- [ ] Performance alerts trigger on slow response
- [ ] Critical alerts trigger on service down

### User Feedback Testing

- [ ] Caption error creates GitHub issue
- [ ] Urgent notifications sent to Slack
- [ ] Issue is labeled correctly

-----

## 🎊 Success Metrics

After 1 week, you should see:

- **Deployment frequency**: 5-10 deploys per day
- **Lead time**: < 30 minutes from commit to production
- **Mean time to recovery**: < 15 minutes
- **Change failure rate**: < 5%

This matches GitHub’s 2025 data showing developers shipping constantly with smaller, safer changes.

-----

## 🆘 Troubleshooting

### Deployment Fails

```bash
# Check GitHub Actions logs
# Look for these common issues:

# 1. Missing secrets
Error: DENO_DEPLOY_TOKEN not found
→ Add secret in GitHub Settings

# 2. Health check timeout
Error: Health check failed
→ Verify /health endpoint exists in service

# 3. Test failures
Error: deno test failed
→ Fix tests before deploying
```

### Slack Notifications Not Arriving

```bash
# Test webhook manually
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test message"}'

# If this fails:
→ Regenerate webhook in Slack
→ Update GitHub secret
```

-----

## 📚 Next Steps

Once basic CI/CD is working:

1. **Add more metrics** to Grafana
1. **Implement A/B testing** for new features
1. **Set up staging environment** for pre-production testing
1. **Add chaos engineering** to test resilience
1. **Create deployment calendar** to track releases

-----

## 🎯 MBTQ Ecosystem Benefits

This CI/CD setup transforms your vision into reality:

- **Intent → Identity → Infrastructure**: Every commit automatically flows through the system
- **Deaf-first empowerment**: Accessibility fixes deploy in minutes, not months
- **Trust, reputation, DAO integrity**: Every deployment is logged and traceable via Fibonrose
- **AI-powered execution**: 360 Magicians (GitHub Actions) do the heavy lifting
- **You as root-of-truth**: Your Git commits control the entire deployment flow

The nervous system is now operational. Every push is a signal. Every deployment is a response. The MBTQ Universe is alive. 🌊✨