<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/TensorFlow-2.15+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

# 🛡️ StegoHunter — AI-Powered Steganography Detection Platform

**StegoHunter** is a production-grade, microservices-based cybersecurity platform that detects hidden payloads embedded inside images using a combination of classical statistical analysis and deep learning. It features real-time WebSocket notifications, automated payload extraction, and a threat neutralization engine.

> 🔗 **Live Demo**: [stegohunter.vercel.app](https://stegohunter.vercel.app)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Running Locally](#-running-locally)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Ensemble Detection Engine** | 5 statistical + 1 deep learning engine working in parallel |
| **Chi-Square Analysis** | Detects non-uniform LSB distributions indicative of steganography |
| **RS Analysis** | Regular-Singular group analysis for LSB embedding detection |
| **SPA Analysis** | Sample Pair Analysis for precise payload length estimation |
| **DCT Analysis** | Frequency-domain analysis for JPEG stego detection |
| **Visual Attack** | LSB plane visualization for manual forensic inspection |
| **CNN Classifier** | Custom TensorFlow deep learning model for learned pattern detection |
| **Payload Extraction** | Automatic LSB payload extraction using `stegano` library + raw bit scraper |
| **Threat Neutralization** | Strip detected payloads and sanitize images |
| **Real-Time Progress** | WebSocket-powered live scan progress via Redis Pub/Sub |
| **PDF Reports** | Generate downloadable forensic analysis reports |
| **Google OAuth** | Secure authentication via Supabase Auth |
| **Admin Dashboard** | Service health monitoring, user management, scan analytics |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│                     Hosted on Vercel (FREE)                     │
│          Dashboard │ Scanner │ Reports │ Admin Panel            │
└─────────────┬───────────────────────────────────┬───────────────┘
              │ REST API                          │ WebSocket
              ▼                                   ▼
┌─────────────────────────┐       ┌──────────────────────────────┐
│    Gateway Service      │       │   Notification Service       │
│    (FastAPI - Port 8000)│       │   (FastAPI/WS - Port 8005)   │
│    • Auth Middleware     │       │   • WebSocket Manager        │
│    • Request Routing    │       │   • Redis PubSub Listener    │
│    • CORS / Rate Limit  │       │   • Live Progress Events     │
└──┬────────┬─────────┬───┘       └──────────────┬───────────────┘
   │        │         │                           │
   ▼        ▼         ▼                           │
┌──────┐ ┌──────┐ ┌──────────┐              ┌────▼────┐
│Image │ │Neutr.│ │DNN       │              │  Redis  │
│Analy.│ │Serv. │ │Defense   │              │  7-Alp  │
│:8001 │ │:8003 │ │:8002     │              │  :6379  │
└──┬───┘ └──┬───┘ └──────────┘              └─────────┘
   │        │
   ▼        ▼
┌─────────────────┐    ┌─────────────────────┐
│     MinIO       │    │     Supabase        │
│  Object Storage │    │  Auth + PostgreSQL  │
│  :9000 / :9001  │    │  (Cloud-hosted)     │
└─────────────────┘    └─────────────────────┘
```

### Service Communication Flow

```
User Upload → Gateway → Image Analysis Service → Ensemble Pipeline
                │                                        │
                │ (publishes progress to Redis)          │
                ▼                                        ▼
        Notification Service ←── Redis PubSub ←── Progress Events
                │
                ▼
        WebSocket → Browser (real-time progress bar)
```

---

## 🛠 Tech Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (async, high-performance)
- **AI/ML**: TensorFlow 2.15+ (CNN classifier), NumPy, SciPy, OpenCV
- **Database**: Supabase (PostgreSQL + Auth + RLS)
- **Object Storage**: MinIO (S3-compatible)
- **Message Broker**: Redis 7 (Pub/Sub for real-time events)
- **Containerization**: Docker Compose

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **UI Library**: shadcn/ui + Radix UI primitives
- **Styling**: Tailwind CSS 3
- **State Management**: Zustand + React Query
- **Charts**: Recharts
- **Auth**: Supabase Auth (Google OAuth)

### Infrastructure
- **Frontend Hosting**: Vercel (free tier)
- **Backend**: Docker Compose (local or VPS)
- **CI/CD**: GitHub Actions
- **Tunneling**: Cloudflare Tunnel (for local backend exposure)

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v24+)
- [Node.js](https://nodejs.org/) (v20+)
- [Git](https://git-scm.com/)
- A [Supabase](https://supabase.com/) project (free tier)

### 1. Clone the repository

```bash
git clone https://github.com/nik1740/Stegohunter.git
cd Stegohunter
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. Set up the database

Run the SQL schema in your Supabase SQL Editor:

```bash
# Copy contents of supabase_schema.sql into Supabase SQL Editor and execute
```

### 4. Start the backend services

```bash
# Start infrastructure first
docker compose up -d redis minio

# Start application services
docker compose up -d --build gateway-service image-analysis-service neutralization-service notification-service
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:8080`.

---

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_KEY` | Supabase anon/public key | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (server-side only) | ✅ |
| `REDIS_URL` | Redis connection URL | Auto-configured by Docker |
| `MINIO_URL` | MinIO endpoint | Auto-configured by Docker |
| `MINIO_ACCESS_KEY` | MinIO access key | Auto-configured by Docker |
| `MINIO_SECRET_KEY` | MinIO secret key | Auto-configured by Docker |

### Frontend Environment (`.env.local` in `/frontend`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_SUPABASE_URL` | Supabase project URL | — |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key | — |
| `VITE_API_URL` | Gateway API base URL | `http://localhost:8000/api/v1` |
| `VITE_WS_URL` | WebSocket notification URL | `ws://localhost:8005` |

---

## 🏃 Running Locally

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Gateway | `8000` | Main API endpoint |
| Image Analysis | `8001` | AI detection engine |
| DNN Defense | `8002` | Neural network model scanner |
| Neutralization | `8003` | Threat payload remover |
| Orchestration | `8004` | Task queue manager |
| Notification | `8005` | WebSocket real-time events |
| MinIO Console | `9001` | Object storage dashboard |
| Redis | `6379` | Message broker |
| Frontend | `8080` | React development server |

### Useful Commands

```bash
# View running containers
docker ps

# View logs for a specific service
docker logs -f stego_gateway

# Rebuild a single service
docker compose build gateway-service && docker compose up -d gateway-service

# Stop all services
docker compose down

# Clean up Docker disk space
docker system prune -a -f --volumes
docker builder prune -a -f
```

---

## 🌐 Deployment

### Frontend → Vercel (Free)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) → Import your repo
3. Set **Root Directory** to `frontend`
4. Set **Framework Preset** to `Vite`
5. Add environment variables (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_URL`, `VITE_WS_URL`)
6. Deploy — every `git push` auto-deploys

### Backend → Local via Cloudflare Tunnel

Expose your local Docker backend to the internet for free:

```bash
# Install Cloudflare Tunnel
winget install cloudflare.cloudflared

# Start the tunnel
cloudflared tunnel --url http://localhost:8000
```

This gives you a public HTTPS URL that tunnels to your local `localhost:8000`. Set this URL as `VITE_API_URL` in Vercel.

### Backend → VPS (Production)

For 24/7 uptime, deploy to a VPS:

| Provider | RAM | Price | Recommendation |
|----------|-----|-------|----------------|
| Oracle Cloud | 24 GB | **Free forever** | Best free option |
| Hetzner | 2 GB | €3.79/mo | Best budget option |
| DigitalOcean | 2 GB | $12/mo | Easiest setup |

```bash
# On your VPS:
git clone https://github.com/nik1740/Stegohunter.git
cd Stegohunter
cp .env.example .env
# Edit .env with your credentials
docker compose up -d --build
```

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login with email/password |
| `GET` | `/api/v1/auth/me` | Get current user profile |

### Scanning

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/scan` | Upload and scan an image |
| `GET` | `/api/v1/scan/jobs/{id}` | Get scan job details + results |
| `GET` | `/api/v1/scan/jobs` | List all user scan jobs |
| `GET` | `/api/v1/scan/extract/{job_id}` | Extract LSB payload from a previously scanned image |
| `POST` | `/api/v1/scan/extract` | Extract LSB payload (file upload) |
| `GET` | `/api/v1/scan/stats` | Get scan statistics |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/reports/scans` | Get paginated scan reports |
| `GET` | `/api/v1/reports/scans/{id}/pdf` | Download PDF forensic report |

### Neutralization

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/neutralize` | Neutralize and sanitize an image |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/admin/health` | Check all service health status |
| `GET` | `/api/v1/admin/users` | List all platform users |
| `GET` | `/api/v1/admin/stats` | Platform-wide analytics |

---

## 🗄 Database Schema

```sql
profiles          — User profiles linked to Supabase Auth
api_keys          — API key management
scan_jobs         — Image scan job tracking
scan_results      — Detection results per scan
scan_artifacts    — MinIO object references
neutralization_jobs — Threat neutralization tracking
reports           — Generated forensic reports
audit_logs        — Platform activity audit trail
```

The full schema is available in [`supabase_schema.sql`](./supabase_schema.sql).

---

## 📂 Project Structure

```
stego-hunter/
├── frontend/                    # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Route-level page components
│   │   ├── lib/                 # API client, Supabase, utilities
│   │   └── hooks/               # Custom React hooks
│   ├── vercel.json              # Vercel deployment config
│   └── package.json
│
├── gateway-service/             # API Gateway (FastAPI)
│   └── app/
│       ├── api/v1/              # Route handlers (auth, scan, admin, etc.)
│       ├── core/                # Config, Supabase client, MinIO client
│       └── main.py              # App entrypoint with CORS middleware
│
├── image-analysis-service/      # AI Detection Engine (FastAPI)
│   └── app/
│       ├── classifiers/         # Ensemble classifier orchestrator
│       ├── engines/             # Chi-Square, RS, SPA, DCT, Visual, LSB
│       ├── models/              # TensorFlow CNN model weights
│       └── api/                 # /analyze and /extract-lsb endpoints
│
├── neutralization-service/      # Threat Neutralization (FastAPI)
│   └── app/                     # LSB stripping and image sanitization
│
├── notification-service/        # WebSocket Server (FastAPI)
│   └── app/
│       ├── websockets.py        # ConnectionManager + Redis PubSub
│       └── main.py              # WebSocket router + background tasks
│
├── dnn-defense-service/         # DNN Model Scanner (FastAPI)
│   └── app/                     # Weight analysis, anomaly detection
│
├── orchestration-service/       # Task Queue Manager (Celery + Redis)
│
├── .github/workflows/ci.yml     # GitHub Actions CI pipeline
├── docker-compose.yml           # Full stack orchestration
├── supabase_schema.sql          # Database schema
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

---

## 🔬 Detection Pipeline

When an image is uploaded, the ensemble detection pipeline runs these engines in parallel:

| Engine | Weight | Technique | Best For |
|--------|--------|-----------|----------|
| Chi-Square | 30% | Statistical distribution analysis | LSB replacement detection |
| RS Analysis | 25% | Regular-Singular group flipping | Estimating embedding capacity |
| SPA | 25% | Sample pair likelihood ratio | Precise payload size estimation |
| DCT | 20% | Frequency coefficient analysis | JPEG steganography (JSteg, F5) |
| Visual Attack | — | LSB plane extraction | Manual forensic inspection |
| CNN Classifier | — | Deep learning pattern recognition | Learned stego signatures |

The **final score** uses a True-Positive Max Confidence strategy — instead of averaging (which dilutes strong signals), it takes the highest detection probability across all engines. A single engine hitting >65% flags the file.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/nik1740">Nikhil S</a>
</p>
