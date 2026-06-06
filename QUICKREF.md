# GenBuilder - Quick Reference

## Start Local Dev (Docker - Easiest)
```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## Start Local Dev (Manual)
```bash
# Terminal 1 - Backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

## Deploy to Production (Free)

**Best option - Fly.io + Vercel:**
```bash
# Install Fly CLI first: https://fly.io/docs/hands-on/install/

flyctl auth login
flyctl launch
flyctl deploy

# Get your backend URL
flyctl info
```

Then deploy frontend to Vercel with `VITE_API_URL=https://genbuilder.fly.dev`

**Alternative - Render + Vercel:**
- Go to https://render.com
- Connect GitHub, deploy Python app
- Follow [DEPLOYMENT.md](./DEPLOYMENT.md) for details

**Quick script (choose for you):**
```bash
./deploy.sh  # or: deploy.bat on Windows
```

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | Backend API entry point |
| `frontend/src/App.jsx` | Frontend React app |
| `docker-compose.yml` | Local full-stack |
| `DEPLOYMENT.md` | Detailed deployment guide |
| `SETUP.md` | Complete setup guide |

## Environment Variables

**Backend (.env):**
```
CORS_ORIGINS=http://localhost:3000
OPENAI_API_KEY=sk-...  (optional, for CrewAI mode)
```

**Frontend (frontend/.env):**
```
VITE_API_URL=http://localhost:8000
```

## API Endpoints

- `POST /api/generate-parameters?mode=heuristic` - Generate parameters
- `GET /api/results` - List results
- `GET /api/health` - Health check
- `GET /docs` - Interactive API docs

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Frontend can't reach backend | Check `VITE_API_URL` and CORS settings |
| Port already in use | Change port in docker-compose.yml or kill process |
| Missing npm packages | `npm install --legacy-peer-deps` |
| Backend won't start | Activate venv and run `pip install -r requirements.txt` |

## UI Features

✨ Modern React interface
⚡ Two processing modes (Heuristic & CrewAI)
📊 Real-time results viewer
💾 Download & delete results
📱 Fully responsive design
🎨 Clean Tailwind CSS styling

## Cost for Production

- **Railway**: $0 (5/month free credits, sufficient for small projects)
- **Vercel**: $0 (free tier)
- **OpenAI API**: Pay-as-you-go (~$0.01-0.10 per request)

## Documentation

- [SETUP.md](./SETUP.md) - Complete setup guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Cloud deployment guide
- [README.md](./README.md) - Full documentation
- [API Docs](http://localhost:8000/docs) - When running locally

## Support

1. Check documentation files above
2. Run locally first to test
3. Check CORS_ORIGINS and API URLs
4. Review logs with `docker-compose logs`
