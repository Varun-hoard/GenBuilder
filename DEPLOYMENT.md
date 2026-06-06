# GenBuilder - Deployment Guide

Complete guide to deploy GenBuilder (frontend + backend) to free hosting services.

## Quick Summary

| Component | Service | Free Tier | Link |
|-----------|---------|-----------|------|
| **Frontend** | Vercel | ✅ Unlimited | [vercel.com](https://vercel.com) |
| **Backend** | Railway | ✅ $5/month credits | [railway.app](https://railway.app) |
| **Backend Alternative** | Render | ✅ Free instance | [render.com](https://render.com) |

## Option 1: Railway + Vercel (Recommended ⭐)

### Why this option?
- **Railway**: Best free tier ($5/month credits sufficient for testing), easy Docker support
- **Vercel**: Industry standard for React/Next.js, seamless deployment
- **Cost**: Completely free for small projects

### Prerequisites
1. GitHub account (for deploying from repo)
2. Credit card (verification, no charge for free tier)

### Step 1: Prepare Your Repository

```bash
# Ensure your repo is on GitHub
git add .
git commit -m "Add GenBuilder with UI"
git push origin main
```

### Step 2: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your GenBuilder repository
4. Configure the deployment:
   - **Root Directory**: `.` (root of repo)
   - **Dockerfile**: Select the existing `Dockerfile` in root
   - **Port**: 8000
   - **Build Command**: (leave empty)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Add environment variables in Railway dashboard:
   ```
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   OPENAI_API_KEY=your_api_key_here  (if using CrewAI mode)
   DEBUG=false
   ```

6. Deploy and get your backend URL (e.g., `https://genbuilder-api-prod.railway.app`)

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
   VITE_API_URL=https://your-backend-url.railway.app
   ```

5. Deploy!

### Step 4: Connect Frontend to Backend

After deployment, update Vercel environment variable with the actual deployed backend URL if needed.

---

## Option 2: Render (Free Tier Alternative)

### Deploy Backend to Render

1. Go to [render.com](https://render.com)
2. Create account and connect GitHub
3. New → **Web Service**
4. Select your repo
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

6. Add environment variables
7. Deploy

**Note**: Free tier on Render spins down after 15 minutes of inactivity (cold start).

---

## Option 3: Fly.io (Free Tier)

### Deploy Backend to Fly.io

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

**Railway:**
```
railway logs  # In project directory
```

**Render:**
- Dashboard → Service → Logs tab

**Fly.io:**
```
flyctl logs
```

### Common Issues

| Issue | Solution |
|-------|----------|
| **CORS errors** | Update `CORS_ORIGINS` in backend environment variables |
| **Frontend can't reach API** | Check `VITE_API_URL` matches deployed backend URL |
| **Cold starts taking too long** | Switch from Render free tier to Railway (stays warm) |
| **OpenAI API errors** | Verify `OPENAI_API_KEY` is set correctly |

---

## Performance Optimization

For production, add these configurations:

### Backend (Render/Railway)
- Set `DEBUG=false`
- Use `gunicorn` instead of `uvicorn`:
  ```bash
  pip install gunicorn
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
  ```

### Frontend (Vercel)
- Vercel automatically optimizes React builds
- Enable Edge Caching in Vercel dashboard

---

## Scaling Beyond Free Tier

| Service | Next Step | Cost |
|---------|-----------|------|
| Railway | Auto-scales as needed | $5→$20/month depending on usage |
| Render | Paid instance | $7+/month |
| Vercel | Pro plan | $20/month |

---

## Backup & Data Persistence

Generated parameters are stored in `./outputs/` directory. For persistence:

**Railway/Render:**
- Mount volumes for permanent storage
- Or integrate S3 (AWS free tier eligible)

---

## Support

- **GenBuilder Issues**: Check GitHub issues
- **Railway**: Support dashboard on railway.app
- **Render**: Support docs at render.com/docs
- **Vercel**: Support docs at vercel.com/docs

---

## Quick Links

- GenBuilder GitHub: [Your repo URL]
- Railway Pricing: https://railway.app/pricing
- Render Pricing: https://render.com/pricing
- Vercel Pricing: https://vercel.com/pricing
