# GenBuilder - Complete Setup Guide

This guide walks you through everything needed to run GenBuilder locally or deploy it to production.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Local Development](#local-development)
3. [Cloud Deployment](#cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## System Requirements

### For Local Development

| Component | Version | Download |
|-----------|---------|----------|
| Python | 3.9+ | [python.org](https://www.python.org) |
| Node.js | 16+ | [nodejs.org](https://nodejs.org) |
| Docker (optional) | Latest | [docker.com](https://www.docker.com) |
| Git | Latest | [git-scm.com](https://git-scm.com) |

### For Cloud Deployment

- GitHub account (for repository)
- Credit card (for free tier verification, no charges)
- Choice of cloud provider:
  - Railway, Render, or Fly.io (backend)
  - Vercel (frontend)

---

## Local Development

### Option 1: Quick Start with Docker Compose (Recommended)

**Prerequisites:**
- Docker Desktop installed and running

**Steps:**

```bash
# Clone the repository
git clone <your-repo-url>
cd genbuilder

# Start both backend and frontend
docker-compose up --build

# Wait for initialization (takes ~30 seconds)
# Then visit:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

**Stopping:**
```bash
docker-compose down
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server runs at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

#### Frontend Setup (in a new terminal)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# Frontend runs at http://localhost:3000
```

#### Running Tests

```bash
# In the root directory (with venv activated)
pytest tests/ -v
```

---

## Cloud Deployment

### Quickest Method: Interactive Script

```bash
# On macOS/Linux:
chmod +x deploy.sh
./deploy.sh

# On Windows:
deploy.bat
```

This interactive script guides you through:
1. Choosing a deployment platform
2. Setting up necessary accounts
3. Configuring environment variables
4. Deploying both frontend and backend

### Manual Deployment Steps

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions on:

- **Railway + Vercel** (Recommended)
- **Render + Vercel**
- **Fly.io + Vercel**

---

## Environment Configuration

### Backend Environment Variables

Create `.env` file in root directory:

```bash
# Application
APP_NAME=GenBuilder
APP_VERSION=1.0.0
DEBUG=false

# API
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# OpenAI (for CrewAI mode)
OPENAI_API_KEY=sk-...  # Get from https://platform.openai.com/api-keys
OPENAI_MODEL_NAME=gpt-4o

# Storage
GENBUILDER_OUTPUT_DIR=./outputs
```

### Frontend Environment Variables

Create `.env` in `frontend/` directory:

```bash
# API Connection
VITE_API_URL=http://localhost:8000  # Change for production

# App Configuration
VITE_APP_NAME=GenBuilder
```

### For Production Deployment

Update `.env` variables:

**Backend:**
```bash
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.com
OPENAI_API_KEY=sk-...  # Your actual API key
```

**Frontend:**
```bash
VITE_API_URL=https://your-backend-api-domain.com
```

---

## Features & Usage

### Web Interface

1. **Enter Project Details**
   - Project name
   - Design constraints (natural language)
   - Solver type (if applicable)

2. **Choose Processing Mode**
   - **Heuristic** (instant, no API key needed)
   - **CrewAI** (smart, requires OpenAI API key)

3. **View & Download Results**
   - Real-time JSON viewer
   - Download as JSON file
   - Copy to clipboard
   - Browse result history

### API Endpoints

**Generate Parameters:**
```bash
POST /api/generate-parameters?mode=heuristic
Content-Type: application/json

{
  "description": "Design a lightweight aluminum bracket...",
  "project_name": "bracket-v1",
  "solver_type": "default"
}
```

**View Results:**
```bash
GET /api/results
GET /api/results/{request_id}
DELETE /api/results/{request_id}
```

**Health Check:**
```bash
GET /api/health
```

---

## Performance Optimization

### Local Development
- Frontend hot reload enabled by default
- Backend auto-reload when code changes
- No optimization needed

### Production

For better performance:

**Backend:**
```bash
# Use gunicorn instead of uvicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

**Frontend:**
- Vercel automatically optimizes builds
- Use production build: `npm run build`
- Enable Edge Caching in Vercel dashboard

---

## Troubleshooting

### Frontend Can't Connect to Backend

**Problem:** `Error connecting to API` in browser console

**Solutions:**
1. Check backend is running: `http://localhost:8000/api/health`
2. Verify `VITE_API_URL` is correct
3. Check CORS settings in backend `.env`
4. For production: ensure backend URL matches `CORS_ORIGINS`

### Backend Won't Start

**Problem:** `ModuleNotFoundError` or import errors

**Solutions:**
```bash
# Verify virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Docker Issues

**Problem:** Ports already in use

**Solutions:**
```bash
# Stop all containers
docker-compose down

# Or use different ports in docker-compose.yml
# Change port mapping: "8001:8000"
```

**Problem:** Container won't start

**Solutions:**
```bash
# Check logs
docker-compose logs -f

# Rebuild without cache
docker-compose build --no-cache
docker-compose up
```

### Missing Dependencies

**Problem:** `npm ERR! ERESOLVE unable to resolve dependency tree`

**Solution:**
```bash
cd frontend
npm install --legacy-peer-deps
```

### API Key Issues

**Problem:** CrewAI mode returns errors

**Solutions:**
1. Verify OpenAI API key is valid: https://platform.openai.com/account/api-keys
2. Check key is set in `.env`: `OPENAI_API_KEY=sk-...`
3. Ensure account has sufficient credits
4. For production, use environment variables not .env files

---

## Next Steps

1. **Local Testing**
   - [ ] Start with heuristic mode (no API key needed)
   - [ ] Test with sample design constraints
   - [ ] Download and review generated parameters

2. **Production Setup**
   - [ ] Create GitHub repository
   - [ ] Run `deploy.sh` or follow DEPLOYMENT.md
   - [ ] Set up OpenAI API key (if using CrewAI)
   - [ ] Configure custom domain (optional)

3. **Integration**
   - [ ] Connect to your CAE solver
   - [ ] Validate generated parameters
   - [ ] Implement feedback loop

---

## Getting Help

| Issue | Resource |
|-------|----------|
| GenBuilder | GitHub Issues or README |
| Railway | https://docs.railway.app |
| Render | https://render.com/docs |
| Vercel | https://vercel.com/docs |
| OpenAI API | https://platform.openai.com/docs |

---

## Additional Resources

- [API Documentation](./README.md#api-endpoints)
- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture Overview](./README.md#architecture)
- [Processing Modes](./README.md#processing-modes)

---

**Ready to deploy?** Run:
```bash
./deploy.sh  # macOS/Linux
deploy.bat   # Windows
```
