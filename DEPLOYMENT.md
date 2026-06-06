# GenBuilder - Deployment Guide

Complete guide to deploy GenBuilder (frontend + backend) to free hosting services.

## Quick Summary

| Component | Service | Free Tier | Cold Starts | Link |
|-----------|---------|-----------|-------------|------|
| **Frontend** | Vercel | ✅ Unlimited | ❌ No | [vercel.com](https://vercel.com) |
| **Backend** | Fly.io | ✅ Genuine Free | ✅ No | [fly.io](https://fly.io) |
| **Backend Alt** | Render | ✅ Free | ⚠️ 15min | [render.com](https://render.com) |

## Option 1: Fly.io + Vercel (Recommended ⭐)

### Why this option?
- **Fly.io**: Best free tier, no cold starts, stays warm, good performance
- **Vercel**: Industry standard for React/Next.js, seamless deployment
- **Cost**: Completely free, no surprise charges
- **Performance**: Best experience for users (no cold starts)

### Prerequisites
1. GitHub account (for deploying from repo)
2. No credit card needed

### Step 1: Prepare Your Repository

```bash
# Ensure your repo is on GitHub
git add .
git commit -m "Add GenBuilder with UI"
git push origin main
```

### Step 2: Deploy Backend to Fly.io

1. Install Fly CLI: https://fly.io/docs/hands-on/install/
   
2. Login and launch:
   ```bash
   flyctl auth login
   cd genbuilder
   flyctl launch
   ```
   
3. When prompted:
   - **App name**: `genbuilder` (or your preferred name)
   - **Region**: Pick closest to you (e.g., `sjc` for US West)
   - **Postgres**: No
   - **Redis**: No
   
4. Set environment variables:
   ```bash
   flyctl secrets set DEBUG=false
   flyctl secrets set OPENAI_API_KEY=your_key_here  # Optional, for CrewAI mode
   ```

5. Deploy:
   ```bash
   flyctl deploy
   ```

6. Get your backend URL:
   ```bash
   flyctl info
   ```
   Look for the HTTPS URL (e.g., `https://genbuilder.fly.dev`)

### Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"** → Select your GitHub repo
3. Configure the project:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add environment variables:
   ```
   VITE_API_URL=https://genbuilder.fly.dev
   ```
   (Replace with your actual Fly.io URL from Step 2.6)

5. Click **Deploy**!

### Step 4: Update Fly.io CORS

Back in terminal, update CORS for your Vercel frontend URL:
```bash
flyctl secrets set CORS_ORIGINS=https://your-frontend.vercel.app
flyctl deploy
```

### ✅ Done!
- **Frontend**: `https://your-frontend.vercel.app`
- **Backend**: `https://genbuilder.fly.dev`
- **API Docs**: `https://genbuilder.fly.dev/docs`
- **Cost**: $0 forever (genuine free tier)

---

## Option 2: Render + Vercel (Simpler Alternative)

### Why this option?
- **Easier setup** than Fly.io
- Still completely free
- GitHub integration built-in

### Why NOT this?
- ⚠️ Free tier spins down after 15 min of inactivity = cold starts
- First request after inactivity takes ~15 seconds

### Deploy Backend to Render

1. Go to [render.com](https://render.com)
2. Click **Sign Up** → Use GitHub for fastest setup
3. Click **New +** → **Web Service**
4. Select your GenBuilder repository
5. Configure:
   - **Name**: `genbuilder-backend`
   - **Environment**: `Python 3`
   - **Region**: `Oregon`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Select **Free**

6. Add environment variables:
   ```
   DEBUG=false
   OPENAI_API_KEY=your_key_here  # Optional
   CORS_ORIGINS=(leave blank for now, update later)
   ```

7. Click **Create Web Service** (takes 2-3 min)
8. Copy your URL (e.g., `https://genbuilder-backend.onrender.com`)

### Deploy Frontend to Vercel (same as Fly.io Option Step 3)

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"** → Select your GitHub repo
3. Configure:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add environment variables:
   ```
   VITE_API_URL=https://genbuilder-backend.onrender.com
   ```

5. Deploy!

### Update Render CORS

1. Go back to Render dashboard
2. Select **genbuilder-backend** service
3. Go to **Environment**
4. Update `CORS_ORIGINS` to: `https://your-frontend.vercel.app`
5. Service auto-redeploys

---

## Option 3: Railway + Vercel (If you get credits working)

### Deploy Backend to Railway

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `flyctl auth login`
3. Launch app: `flyctl launch`
4. Deploy: `flyctl deploy`

---

## Local Development

### Run Full Stack Locally

```bash
# Option 1: Docker Compose (easiest)
docker-compose up --build

# Option 2: Manual setup
# Terminal 1 - Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` (frontend automatically proxies to backend)

---

## Environment Variables

### Backend (.env in root)
```
APP_NAME=GenBuilder
APP_VERSION=1.0.0
DEBUG=false
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.vercel.app
OPENAI_API_KEY=sk-...  # For CrewAI mode
OPENAI_MODEL_NAME=gpt-4o
```

### Frontend (.env in frontend/)
```
VITE_API_URL=https://your-backend-url
VITE_APP_NAME=GenBuilder
```

---

## Monitoring & Troubleshooting

### Check Backend Logs

**Fly.io:**
```bash
flyctl logs
```

**Render:**
- Dashboard → Service → Logs tab

**Railway:**
```bash
railway logs  # In project directory
```

### Common Issues

| Issue | Solution |
|-------|----------|
| **CORS errors** | Update `CORS_ORIGINS` in backend environment variables, then deploy |
| **Frontend can't reach API** | Check `VITE_API_URL` matches deployed backend URL exactly |
| **Cold starts taking too long** | Use Fly.io instead of Render (stays warm, better performance) |
| **OpenAI API errors** | Verify `OPENAI_API_KEY` is set correctly, account has credits |
| **Fly.io deploy fails** | Run `flyctl logs` to see error details |
| **502 Bad Gateway** | Backend may still be deploying, wait 2-3 minutes and refresh |

---

## Performance Optimization

For production, add these configurations:

### Backend (Fly.io)
- Set `DEBUG=false` (included in fly.toml)
- Fly.io auto-scales, no configuration needed
- Connection pooling handled automatically

### Backend (Render)
- Set `DEBUG=false`
- Use `gunicorn` wrapper (optional):
  ```bash
  pip install gunicorn
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
  ```

### Frontend (Vercel)
- Vercel automatically optimizes React builds
- Edge Caching enabled by default

---

## Scaling Beyond Free Tier

| Service | Free Tier | Next Step | Cost |
|---------|-----------|-----------|------|
| Fly.io | Genuine | Auto-scale capacity | $0.15/vCPU-month |
| Render | Limited | Paid instance | $7+/month |
| Vercel | Unlimited | Pro features | $20/month |

---

## Backup & Data Persistence

Generated parameters are stored in `./outputs/` directory.

**For production persistence:**
- Fly.io: Use persistent volumes (paid feature)
- Render: Mount volumes or integrate S3
- AWS S3: Free tier eligible for small storage

---

## Support & Troubleshooting

### Documentation
- **Fly.io**: https://fly.io/docs/
- **Render**: https://render.com/docs/
- **Vercel**: https://vercel.com/docs/
- **GenBuilder**: [GitHub Issues](https://github.com/Varun-hoard/GenBuilder/issues)

### Common Commands

**Fly.io:**
```bash
flyctl logs              # View logs
flyctl status           # Check deployment status
flyctl deploy           # Redeploy
flyctl ssh console      # SSH into the app
```

**Render:**
```bash
# All management through web dashboard
```

---

## Quick Links

| Service | Link | Purpose |
|---------|------|---------|
| Fly.io | https://fly.io | Backend deployment |
| Vercel | https://vercel.com | Frontend deployment |
| Render | https://render.com | Backend alternative |
| GenBuilder GitHub | https://github.com/Varun-hoard/GenBuilder | Source code |
| Your Frontend | `https://your-app.vercel.app` | Live app |
| Your API | `https://genbuilder.fly.dev` | Live API |
