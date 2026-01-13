# 🧠 HealthProtocol

> **Advanced Healthcare Platform** — Evidence-based treatment protocols for Depression, PTSD, Anxiety, and beyond.

A platform connecting patients with breakthrough therapies through clinically validated treatment protocols. Built for therapists, patients, and healthcare administrators.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-309%20passing-brightgreen)](tests/)

---

## 📺 Platform Demo

### Landing Page & Neural Network Effect
https://github.com/user-attachments/assets/landing-page-demo.webp

*Interactive neural network background responds to mouse movement, symbolizing the rewiring of neural pathways through therapy.*

### Patient Experience
https://github.com/user-attachments/assets/patient-flow-demo.webp

*Browse evidence-based protocols, view detailed treatment plans, and track your healing journey.*

### Therapist Dashboard
https://github.com/user-attachments/assets/therapist-dashboard-demo.webp

*Manage patients, document sessions, and access AI-powered clinical decision support.*

---

## 🎯 What is PsyProtocol?

PsyProtocol is a **mental healthcare platform** that bridges the gap between cutting-edge clinical research and real-world patient care. We provide:

- **🔬 Evidence-Based Protocols** — Treatment plans derived directly from Phase 3 clinical trials
- **🤝 Patient-Therapist Connection** — Seamless care coordination and communication
- **🛡️ Safety-First Approach** — Comprehensive medical screening and continuous monitoring
- **📊 Outcome Tracking** — Measure progress with validated clinical scales (MADRS, CAPS-5, PHQ-9)
- **🤖 AI-Powered Support** — Clinical decision support and patient education generation

### Who Is This For?

**Patients** seeking lasting relief from:
- Treatment-Resistant Depression
- PTSD and Complex Trauma
- Anxiety Disorders
- Addiction and Substance Use Disorders

**Therapists** who want to:
- Access evidence-based treatment protocols
- Streamline session documentation
- Receive AI-powered clinical decision support
- Track patient outcomes systematically

**Healthcare Organizations** looking to:
- Implement novel therapies safely and effectively
- Ensure regulatory compliance (HIPAA, FDA)
- Scale evidence-based care delivery
- Maintain comprehensive audit trails

---

## ✨ Key Features

### 🌈 For Patients

| Feature | Description |
|---------|-------------|
| **Protocol Browser** | Explore 8+ evidence-based treatment protocols with detailed information |
| **Pre-Screening** | Complete medical screening questionnaires to determine eligibility |
| **Treatment Plans** | View your personalized treatment journey with progress tracking |
| **Educational Resources** | AI-generated guides explaining what to expect at each step |
| **Secure Messaging** | Communicate with your care team (coming soon) |

### 👨‍⚕️ For Therapists

| Feature | Description |
|---------|-------------|
| **Modern Dashboard** | See today's sessions, upcoming appointments, and patient alerts at a glance |
| **Session Documentation** | Log vitals, clinical notes, and outcomes in a streamlined interface |
| **Protocol Engine** | Step-by-step guidance through complex treatment workflows |
| **Safety Monitoring** | Real-time contraindication checking against patient history |
| **AI Decision Support** | Get evidence-based recommendations during critical decision points |

### 🔧 For Administrators

| Feature | Description |
|---------|-------------|
| **Protocol Builder** | Create and edit treatment protocols with a visual step-by-step wizard |
| **AI Extraction** | Upload research papers and automatically extract protocol structure |
| **Safety Configuration** | Define contraindications, warnings, and risk factors |
| **Publishing Workflow** | Review and approve protocols before making them available |
| **Audit Logs** | HIPAA-compliant tracking of all system activities |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Node.js 18+** (for local frontend development)
- **Python 3.11+** (for local backend development)

### 1. Clone & Start

```bash
# Clone the repository
git clone <your-repo-url>
cd health-tech-protocol-app

# Start all services with Docker
docker-compose up -d

# Wait 10 seconds for services to initialize
# Backend automatically runs migrations

# Install frontend dependencies and start dev server
cd frontend
npm install
npm run dev
```

### 2. Seed Demo Data

```bash
# Load example protocols and demo users
docker-compose exec backend python seed_database.py
```

### 3. Access the Platform

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 4. Login with Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Patient** | patient1@psyprotocol.com | Patient123! |
| **Therapist** | therapist1@psyprotocol.com | Therapist123! |
| **Admin** | admin@psyprotocol.com | Admin123! |

---

## 🧬 Included Treatment Protocols

The platform comes pre-loaded with **8 complete, evidence-based protocols**:

### Psychedelic Therapies

1. **Psilocybin-Assisted Therapy for Treatment-Resistant Depression**
   - 15 steps, 12 weeks
   - Based on COMP360 Phase 3 trials & Johns Hopkins protocols
   - Includes preparation, dosing sessions, and integration

2. **MDMA-Assisted Therapy for PTSD**
   - 16 steps, 18 weeks
   - MAPS Phase 3 protocol (FDA Breakthrough Therapy designation)
   - Manualized therapy with co-therapist model

3. **Ketamine Infusion Therapy for Depression**
   - 11 steps, 6 sessions
   - Standard 0.5 mg/kg IV protocol
   - Continuous vitals monitoring

4. **LSD Microdosing Protocol**
   - 9 steps, 12 weeks
   - Fadiman protocol with dose calibration
   - Daily mood and productivity tracking

### Other Therapies

5. **Testosterone Optimization for Men's Health**
   - 12 steps, 26 weeks
   - Age-related optimization (35+)
   - Lifestyle + hormone therapy

6. **Testosterone Replacement Therapy (TRT)**
   - 10 steps, 24 weeks
   - Medical TRT for hypogonadism
   - Multiple delivery methods

7. **FOLFOX Chemotherapy for Colorectal Cancer**
   - 12 cycles, 24 weeks
   - Complete chemotherapy protocol
   - Toxicity management

8. **Autologous Stem Cell Therapy for Osteoarthritis**
   - 12 steps, 52 weeks
   - Bone marrow harvest to rehabilitation
   - One-year follow-up

All protocol files are located in `/backend/examples/` and can be imported via the admin interface.

---

## 🏗️ Technology Stack

### Backend
- **FastAPI** (Python 3.11) — High-performance async API framework
- **PostgreSQL 15** — Robust relational database
- **Redis 7** — Session management and caching
- **SQLAlchemy 2.0** — Modern Python ORM
- **Alembic** — Database migrations
- **Anthropic Claude 4.5** — AI-powered features
- **JWT Authentication** — Secure token-based auth
- **Stripe** — Payment processing (configured)

### Frontend
- **React 19** — Modern UI library
- **TypeScript** — Type-safe JavaScript
- **React Router v7** — Client-side routing
- **Redux Toolkit** — Predictable state management
- **Tailwind CSS v4** — Utility-first styling
- **Vite** — Lightning-fast build tool
- **Axios** — HTTP client

### Infrastructure
- **Docker** — Containerization
- **Docker Compose** — Multi-container orchestration
- **Nginx** — Reverse proxy (production)
- **Let's Encrypt** — SSL certificates (production)

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────┐
│    Frontend (React + TypeScript)            │
│    http://localhost:3000                    │
│                                             │
│  Landing | Patient | Therapist | Admin     │
└────────────────────┬────────────────────────┘
                     │
                     ▼ REST API (JWT Auth)
┌─────────────────────────────────────────────┐
│    Backend (FastAPI + Python)               │
│    http://localhost:8000                    │
│                                             │
│  Auth | Protocols | Sessions | AI Services │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┐
    ▼                 ▼              ▼
┌──────────┐    ┌──────────┐   ┌─────────┐
│PostgreSQL│    │  Redis   │   │ Claude  │
│Port 5433 │    │Port 6380 │   │   API   │
└──────────┘    └──────────┘   └─────────┘
```

---

## 🔐 Security & Compliance

### HIPAA Compliance Features

- ✅ **Audit Logging** — All actions tracked with timestamps, user IDs, IP addresses
- ✅ **PHI Access Tracking** — Specialized logging for protected health information
- ✅ **Data Encryption** — TLS for data in transit, encrypted database connections
- ✅ **Access Controls** — Role-based access, session timeouts, automatic logoff
- ✅ **Business Associate Agreements** — Ready for Anthropic Claude, Stripe

### Authentication & Authorization

- **JWT Tokens** — 15-minute access tokens, 7-day refresh tokens
- **Password Hashing** — Argon2 (OWASP recommended)
- **Role-Based Access Control** — 5 roles (patient, therapist, clinic_admin, medical_director, platform_admin)
- **Resource-Level Permissions** — Therapists can only access their own patients

---

## 🤖 AI Integration

### Powered by Anthropic Claude 4.5

The platform includes three AI-powered features:

#### 1. Protocol Extraction
Upload research papers (PDF or text) and automatically extract:
- Treatment steps and timelines
- Dosing protocols
- Contraindications and warnings
- Evidence sources and citations

#### 2. Patient Education Generation
Create personalized "what to expect" guides:
- Adapts tone based on patient anxiety level
- Evidence-based, compassionate explanations
- Markdown formatted for easy reading

#### 3. Clinical Decision Support
Real-time analysis during therapy sessions:
- Risk level assessment (low/moderate/high/critical)
- Evidence-based recommendations
- Flags cases requiring immediate attention
- Conservative, safety-first approach

### Enable AI Features

```bash
# 1. Get API key from https://console.anthropic.com/
# 2. Add to backend/.env
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 3. Restart backend
docker-compose restart backend
```

---

## 📚 API Documentation

### Interactive Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### API Endpoints (34 Total)

<details>
<summary><b>Authentication (5 endpoints)</b></summary>

- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/auth/login` — Get JWT tokens
- `POST /api/v1/auth/refresh` — Refresh access token
- `POST /api/v1/auth/logout` — Logout
- `GET /api/v1/auth/me` — Get current user

</details>

<details>
<summary><b>Protocols - Public (4 endpoints)</b></summary>

- `GET /api/v1/protocols` — List protocols (with filters & search)
- `GET /api/v1/protocols/{id}` — Protocol details
- `GET /api/v1/protocols/{id}/steps` — Protocol steps
- `GET /api/v1/protocols/search` — Search protocols

</details>

<details>
<summary><b>Admin - Protocol Management (8 endpoints)</b></summary>

- `POST /api/v1/admin/protocols` — Create protocol
- `PUT /api/v1/admin/protocols/{id}` — Update protocol
- `DELETE /api/v1/admin/protocols/{id}` — Archive protocol
- `POST /api/v1/admin/protocols/{id}/steps` — Add step
- `PUT /api/v1/admin/protocols/{id}/steps/{step_id}` — Update step
- `DELETE /api/v1/admin/protocols/{id}/steps/{step_id}` — Delete step
- `POST /api/v1/admin/protocols/{id}/steps/{step_id}/safety-checks` — Add safety check
- `POST /api/v1/admin/protocols/{id}/publish` — Publish protocol

</details>

<details>
<summary><b>Patient Journey (6 endpoints)</b></summary>

- `GET /api/v1/patients/providers/search` — Find providers
- `POST /api/v1/patients/protocols/{id}/pre-screen` — Pre-screening quiz
- `POST /api/v1/patients/consultation-request` — Request consultation
- `GET /api/v1/patients/treatment-plans` — My treatment plans
- `GET /api/v1/patients/treatment-plans/{id}` — Treatment plan details
- `POST /api/v1/patients/consent/{plan_id}` — Sign consent

</details>

<details>
<summary><b>Therapist Workflow (8 endpoints)</b></summary>

- `GET /api/v1/therapist/dashboard` — Dashboard data
- `GET /api/v1/therapist/patients` — My patients
- `POST /api/v1/therapist/treatment-plans` — Create treatment plan
- `GET /api/v1/therapist/sessions/{id}` — Session details
- `POST /api/v1/therapist/sessions/{id}/vitals` — Log vitals
- `POST /api/v1/therapist/sessions/{id}/documentation` — Save notes
- `POST /api/v1/therapist/sessions/{id}/complete` — Complete session
- `POST /api/v1/therapist/decision-points/{id}/evaluate` — Evaluate decision

</details>

<details>
<summary><b>AI Services (3 endpoints)</b></summary>

- `POST /api/v1/ai/extract-protocol` — Extract from research paper
- `POST /api/v1/ai/generate-patient-education` — Generate patient guide
- `POST /api/v1/ai/decision-support` — Clinical decision support

</details>

---

## 🧪 Testing

### Test Coverage

- **Backend:** 216 tests (models, services, API, end-to-end)
- **Frontend:** 93 tests (components, services, Redux, pages)
- **Total:** 309 tests — all passing ✅

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# With coverage
pytest --cov=app --cov-report=html  # Backend
npm run test:coverage               # Frontend
```

---

## 🚀 Deployment

### Production Deployment Options

**Option 1: Single VM (GCP/AWS/Azure)**
```bash
# Use included deployment script
./deploy.sh

# Includes:
# - Nginx reverse proxy with SSL
# - Let's Encrypt certificates
# - Docker Compose orchestration
# - Automated migrations
```

**Option 2: Platform-as-a-Service**
- Frontend: Vercel, Netlify, Cloudflare Pages
- Backend: Heroku, Render, Railway, Fly.io
- Database: AWS RDS, GCP Cloud SQL, Supabase
- Redis: ElastiCache, Redis Cloud

**Option 3: Kubernetes**
- Container images ready
- Helm charts (to be created)
- Horizontal pod autoscaling
- Load balancer with SSL termination

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 📁 Project Structure

```
health-tech-protocol-app/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # 34 API endpoints
│   │   ├── models/           # 11 SQLAlchemy models
│   │   ├── schemas/          # Pydantic validation
│   │   ├── services/         # Business logic (Protocol Engine, AI)
│   │   ├── core/             # Security, config
│   │   └── utils/            # AI prompts, helpers
│   ├── alembic/              # Database migrations
│   ├── tests/                # 216 tests
│   ├── examples/             # 8 protocol JSON files
│   └── seed_database.py      # Demo data loader
├── frontend/
│   ├── src/
│   │   ├── components/       # 11 reusable components
│   │   ├── pages/            # Landing, Patient, Therapist, Admin
│   │   ├── services/         # API client
│   │   ├── store/            # Redux state management
│   │   └── types/            # TypeScript definitions
│   ├── tests/                # 93 tests
│   └── package.json
├── docs/                     # Design & implementation docs
├── docker-compose.yml        # Multi-container orchestration
├── deploy.sh                 # Production deployment script
├── DEPLOYMENT.md             # Deployment guide
└── README.md                 # This file
```

---

## 🤝 Contributing

This is a production-ready codebase with:
- ✅ Clean architecture (separation of concerns)
- ✅ Comprehensive testing (309 tests)
- ✅ TypeScript for type safety
- ✅ API documentation
- ✅ Code quality tools (ESLint, Black, Ruff)

**Development workflow:**
1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Run tests locally
5. Commit with conventional commits format
6. Create pull request

---

## 📄 License

[Add your license here]

---

## 🙋 Support & Resources

- **Documentation:** See `/docs/` folder
- **API Docs:** http://localhost:8000/docs
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Protocol Workflow System:** [PROTOCOL_WORKFLOW_SYSTEM.md](PROTOCOL_WORKFLOW_SYSTEM.md)
- **Issues:** [Your GitHub issues URL]
- **Email:** [Your support email]

---

## ⭐ Project Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | ~18,000 |
| **Tests** | 309 (all passing) |
| **API Endpoints** | 34 |
| **Database Models** | 11 |
| **Pre-loaded Protocols** | 8 |
| **Supported Therapy Types** | 20+ |
| **AI Services** | 3 (Claude-powered) |
| **Status** | Production-ready ✅ |

---

<div align="center">

**Built with ❤️ for advancing mental healthcare**

[Get Started](#-quick-start) • [View Demo](#-platform-demo) • [Read Docs](docs/)

</div>
