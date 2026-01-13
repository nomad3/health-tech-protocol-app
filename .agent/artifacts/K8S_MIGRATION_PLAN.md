# Health Protocol - Kubernetes Migration Plan

## Overview

This document outlines the lift-and-shift migration from GCP VM deployment to GKE Autopilot cluster.

**Target Platform**: `healthprotocol.agentprovision.com`
**Target Namespace**: `prod`
**Target Cluster**: `gke-autopilot-cluster` (us-central1)
**Project**: `ai-agency-479516`

---

## Infrastructure Summary

### Current GKE Resources
- **Cluster**: `gke_ai-agency-479516_us-central1_gke-autopilot-cluster`
- **Cloud SQL**: `dev-postgres-instance` (PostgreSQL 15, Private IP: 172.30.0.3)
- **Shared Gateway**: `prod-external-gateway` (IP: 35.244.185.117)
- **Secret Store**: `gcpsm-secret-store` (GCP Secret Manager)

### Microservice Naming Convention
Following the DentalERP pattern with normalized names:

| Service | K8s Name | Container Port | Notes |
|---------|----------|----------------|-------|
| Frontend | `healthprotocol-frontend` | 80 (nginx) | Static SPA served by Nginx |
| Backend API | `healthprotocol-backend` | 8000 (uvicorn) | FastAPI Python backend |
| Redis | `healthprotocol-redis` | 6379 | Session cache (optional, can use managed) |

---

## Phase 1: Infrastructure Setup

### 1.1 Create Database in Cloud SQL
```bash
# Connect to Cloud SQL and create healthprotocol database
gcloud sql connect dev-postgres-instance --user=postgres --project=ai-agency-479516

# Inside psql:
CREATE DATABASE healthprotocol;
CREATE USER healthprotocol_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE healthprotocol TO healthprotocol_user;
```

### 1.2 Create GCP Secrets
Store in GCP Secret Manager with prefix `healthprotocol-`:

| Secret Name | Description |
|-------------|-------------|
| `healthprotocol-database-url` | PostgreSQL connection string |
| `healthprotocol-jwt-secret` | JWT signing secret (min 32 chars) |
| `healthprotocol-gemini-api-key` | Google Gemini API key |
| `healthprotocol-stripe-secret-key` | Stripe API key (optional) |

### 1.3 Create Managed Certificate
Add `healthprotocol.agentprovision.com` to the existing certificate map or create new:

```yaml
# kubernetes/certificates/healthprotocol-managed-cert.yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: healthprotocol-managed-cert
  namespace: prod
spec:
  domains:
    - healthprotocol.agentprovision.com
```

---

## Phase 2: Helm Chart Setup

### 2.1 Directory Structure
```
helm/
├── charts/
│   └── microservice/          # Reuse from dentalerp (symlink or copy)
├── values/
│   ├── healthprotocol-backend.yaml
│   └── healthprotocol-frontend.yaml
└── README.md
```

### 2.2 Backend Values (`helm/values/healthprotocol-backend.yaml`)
```yaml
# Health Protocol Backend - Production
serviceName: healthprotocol-backend
namespace: prod
environment: production

# Migration
migrationJob:
  enabled: true
  command: ["alembic", "upgrade", "head"]

seedJob:
  enabled: true
  command: ["python", "seed_database.py"]

# Gateway Configuration (attach to shared gateway)
gateway:
  enabled: true
  createGateway: false  # Use existing prod-external-gateway
  gatewayName: prod-external-gateway
  gatewayNamespace: gateway-system
  hostnames:
    - healthprotocol.agentprovision.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api/
      backendRefs:
        - name: healthprotocol-backend
          port: 80
    - matches:
        - path:
            type: PathPrefix
            value: /docs
      backendRefs:
        - name: healthprotocol-backend
          port: 80
    - matches:
        - path:
            type: PathPrefix
            value: /health
      backendRefs:
        - name: healthprotocol-backend
          port: 80

# Image
image:
  repository: gcr.io/ai-agency-479516/healthprotocol-backend
  tag: "latest"
  pullPolicy: Always

# Container
command: ["sh", "-c"]
args: ["alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

# Service Account (Workload Identity)
serviceAccount:
  create: true
  annotations:
    iam.gke.io/gcp-service-account: "dev-backend-app@ai-agency-479516.iam.gserviceaccount.com"

# Resources
replicaCount: 1
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 1Gi

# Service
service:
  type: ClusterIP
  port: 80
  targetPort: 8000

# Secrets (External Secrets Operator)
secret:
  enabled: true
  externalSecret:
    enabled: true
    secretStoreName: gcpsm-secret-store
    refreshInterval: 1m
    data:
      - secretKey: DATABASE_URL
        remoteRef:
          key: healthprotocol-database-url
      - secretKey: JWT_SECRET
        remoteRef:
          key: healthprotocol-jwt-secret
      - secretKey: GEMINI_API_KEY
        remoteRef:
          key: healthprotocol-gemini-api-key

# ConfigMap
configMap:
  enabled: true
  data:
    ENVIRONMENT: production
    CORS_ORIGINS: "https://healthprotocol.agentprovision.com"
    REDIS_URL: "redis://healthprotocol-redis:6379"

# Probes
probes:
  liveness:
    path: /health
    port: 8000
    initialDelaySeconds: 30
  readiness:
    path: /health
    port: 8000
    initialDelaySeconds: 10
```

### 2.3 Frontend Values (`helm/values/healthprotocol-frontend.yaml`)
```yaml
# Health Protocol Frontend - Production
serviceName: healthprotocol-frontend
namespace: prod
environment: production

# Gateway (attach to shared gateway for root path)
gateway:
  enabled: true
  createGateway: false
  gatewayName: prod-external-gateway
  gatewayNamespace: gateway-system
  hostnames:
    - healthprotocol.agentprovision.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: healthprotocol-frontend
          port: 80

# Image
image:
  repository: gcr.io/ai-agency-479516/healthprotocol-frontend
  tag: "latest"
  pullPolicy: Always

# Service Account
serviceAccount:
  create: true
  annotations:
    iam.gke.io/gcp-service-account: "dev-backend-app@ai-agency-479516.iam.gserviceaccount.com"

# Resources
replicaCount: 1
resources:
  requests:
    cpu: 50m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi

# Service
service:
  type: ClusterIP
  port: 80
  targetPort: 80

# ConfigMap
configMap:
  enabled: true
  data:
    NGINX_HOST: healthprotocol.agentprovision.com

# Probes
probes:
  liveness:
    path: /
    port: 80
    initialDelaySeconds: 10
  readiness:
    path: /
    port: 80
    initialDelaySeconds: 5
```

---

## Phase 3: Docker Configuration Updates

### 3.1 Backend Dockerfile Updates
Update `backend/Dockerfile` to:
- Build for production
- Include Cloud SQL Proxy sidecar support
- Use environment-based configuration

### 3.2 Frontend Dockerfile Updates
Update `frontend/Dockerfile` to:
- Build static assets with production API URL as build arg
- Use nginx alpine for serving
- Configure nginx for SPA routing

---

## Phase 4: GitHub Actions CI/CD

### 4.1 Backend Workflow (`.github/workflows/healthprotocol-backend-prod.yaml`)
```yaml
name: Health Protocol - Backend Prod

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - 'helm/values/healthprotocol-backend.yaml'
      - '.github/workflows/healthprotocol-backend-prod.yaml'
  workflow_dispatch:

env:
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GKE_CLUSTER: gke-autopilot-cluster
  GKE_REGION: us-central1
  IMAGE_REGISTRY: gcr.io
  SERVICE_NAME: healthprotocol-backend

jobs:
  build-push:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.sha_short }}
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY_DEV }}
      - run: gcloud auth configure-docker
      - id: meta
        run: echo "sha_short=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ env.IMAGE_REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ steps.meta.outputs.sha_short }}
            ${{ env.IMAGE_REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.SERVICE_NAME }}:latest

  deploy:
    needs: build-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY_DEV }}
      - uses: google-github-actions/setup-gcloud@v2
      - uses: google-github-actions/get-gke-credentials@v2
        with:
          cluster_name: ${{ env.GKE_CLUSTER }}
          location: ${{ env.GKE_REGION }}
      - name: Deploy with Helm
        run: |
          helm upgrade --install healthprotocol-backend ./helm/charts/microservice \
            -f ./helm/values/healthprotocol-backend.yaml \
            -n prod \
            --set image.tag=${{ needs.build-push.outputs.image_tag }}
```

### 4.2 Frontend Workflow (`.github/workflows/healthprotocol-frontend-prod.yaml`)
Similar structure with frontend build args for API URL.

---

## Phase 5: Migration Steps

### Step 1: Prepare Code Changes
1. [ ] Fix `ai_service.py` to use Gemini instead of Anthropic
2. [ ] Update `config.py` to include `GEMINI_API_KEY`
3. [ ] Update `requirements.txt` (remove anthropic, add google-generativeai)
4. [ ] Create Helm chart structure
5. [ ] Create GitHub Actions workflows

### Step 2: Create GCP Resources
1. [ ] Create `healthprotocol` database in Cloud SQL
2. [ ] Create secrets in GCP Secret Manager
3. [ ] Add domain to certificate map (or create ManagedCertificate)

### Step 3: Initial Deployment
```bash
# Build and push images manually first time
docker build -t gcr.io/ai-agency-479516/healthprotocol-backend:latest ./backend
docker push gcr.io/ai-agency-479516/healthprotocol-backend:latest

docker build -t gcr.io/ai-agency-479516/healthprotocol-frontend:latest ./frontend
docker push gcr.io/ai-agency-479516/healthprotocol-frontend:latest

# Deploy with Helm
helm upgrade --install healthprotocol-backend ./helm/charts/microservice \
  -f ./helm/values/healthprotocol-backend.yaml \
  -n prod

helm upgrade --install healthprotocol-frontend ./helm/charts/microservice \
  -f ./helm/values/healthprotocol-frontend.yaml \
  -n prod

# Run migrations
kubectl exec -it deployment/healthprotocol-backend -n prod -- alembic upgrade head

# Seed database
kubectl exec -it deployment/healthprotocol-backend -n prod -- python seed_database.py
```

### Step 4: DNS Configuration
Add DNS A record:
```
healthprotocol.agentprovision.com -> 35.244.185.117 (prod-external-gateway IP)
```

### Step 5: Verify Deployment
```bash
# Check pods
kubectl get pods -n prod -l app=healthprotocol-backend
kubectl get pods -n prod -l app=healthprotocol-frontend

# Check services
kubectl get svc -n prod | grep healthprotocol

# Check HTTPRoute
kubectl get httproute -n prod | grep healthprotocol

# Test endpoints
curl https://healthprotocol.agentprovision.com/health
curl https://healthprotocol.agentprovision.com/
```

---

## Phase 6: Documentation Updates

### Files to Update
1. [ ] `CLAUDE.md` - Add K8s deployment information
2. [ ] `README.md` - Update deployment instructions
3. [ ] Create `docs/deployment/kubernetes.md` - Detailed K8s docs
4. [ ] Create `docs/deployment/architecture.md` - System architecture
5. [ ] Update `.gitignore` - Add Helm-related patterns

---

## Rollback Plan

If deployment fails:
1. Keep VM deployment active until K8s is verified
2. DNS can be switched back to VM IP
3. Database is separate, so no data loss risk

---

## Cost Comparison

| Resource | VM Cost | K8s Cost |
|----------|---------|----------|
| Compute | e2-medium: ~$25/mo | Autopilot pods: ~$15-30/mo |
| Load Balancer | N/A (Nginx) | Shared Gateway: ~$18/mo (split) |
| Database | Same Cloud SQL | Same Cloud SQL |
| **Total** | ~$25/mo | ~$15-25/mo (shared infra) |

---

## Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| 1. Infrastructure Setup | 1 hour | Database, secrets, certs |
| 2. Helm Charts | 2 hours | Create values files, test locally |
| 3. Docker Updates | 1 hour | Optimize Dockerfiles |
| 4. GitHub Actions | 1 hour | Create CI/CD workflows |
| 5. Migration | 2 hours | Deploy, test, DNS switch |
| 6. Documentation | 1 hour | Update docs |
| **Total** | ~8 hours | |

---

## Success Criteria

- [ ] Frontend accessible at `https://healthprotocol.agentprovision.com`
- [ ] Backend API responds at `https://healthprotocol.agentprovision.com/api/`
- [ ] API docs at `https://healthprotocol.agentprovision.com/docs`
- [ ] All demo users can log in
- [ ] AI pre-screening agent works with Gemini
- [ ] CI/CD pipeline deploys on push to main
- [ ] Health checks pass
