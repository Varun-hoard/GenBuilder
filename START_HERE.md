# 🚀 GenBuilder - Start Here!

Welcome to GenBuilder with a brand new **modern web UI**! 

## ⚡ Quick Start (Pick One)

### 1️⃣ Run Locally with Docker (EASIEST - 30 seconds)
```bash
docker-compose up --build
```
Then visit: **http://localhost:3000**

### 2️⃣ Deploy to Free Cloud (RECOMMENDED - 10 minutes)
```bash
./deploy.sh        # On macOS/Linux
# or
deploy.bat         # On Windows
```

### 3️⃣ Manual Local Setup
```bash
# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd frontend && npm install && npm run dev
```

## 📖 Documentation

| Guide | For | Time |
|-------|-----|------|
| **[QUICKREF.md](./QUICKREF.md)** | One-page cheat sheet | 2 min |
| **[SETUP.md](./SETUP.md)** | Complete local setup guide | 10 min |
| **[DEPLOYMENT.md](./DEPLOYMENT.md)** | Cloud deployment detailed guide | 15 min |
| **[WHATS_NEW.md](./WHATS_NEW.md)** | See all improvements | 5 min |
| **[README.md](./README.md)** | Full project documentation | 20 min |

## ✨ What's New

### 🎨 Beautiful Web UI
- Modern, responsive dashboard
- Form for design constraints
- Real-time results viewer
- Download/delete functionality
- Project statistics

### 🚀 Easy Deployment
Three free options included:
- **Railway** (backend) + **Vercel** (frontend) ⭐
- **Render** + **Vercel**
- **Fly.io** + **Vercel**

### 📦 Docker Support
- Full stack with one command
- Both frontend and backend configured
- Production-ready setup

## 🎯 Next Steps

### First Time?
1. Run `docker-compose up --build` (see above)
2. Visit http://localhost:3000
3. Try the heuristic mode (no API key needed)
4. Download a result as JSON

### Ready to Deploy?
1. Push to GitHub
2. Run `./deploy.sh`
3. Follow interactive setup
4. Share your live app!

### Want to Customize?
- Frontend: `frontend/src/App.jsx`
- Backend: `app/main.py`
- Docker: `docker-compose.yml`
- Styles: `frontend/src/index.css` (Tailwind CSS)

## 🆘 Help

| Problem | Solution |
|---------|----------|
| Can't connect to API | Check backend is running on 8000 |
| Port already in use | Change port in docker-compose.yml |
| Frontend won't load | Check VITE_API_URL in frontend/.env |
| Missing npm packages | Run `npm install --legacy-peer-deps` |
| Python errors | Activate venv first |

See [SETUP.md](./SETUP.md) for more troubleshooting.

## 💰 Cost

**Everything is FREE!**
- Railway: Free tier ($5/month credits)
- Vercel: Free tier (unlimited)
- OpenAI: Optional (pay only if using CrewAI mode)

## 🎓 Learn More

- [Architecture](./README.md#architecture) - How it works
- [API Endpoints](./README.md#api-endpoints) - Integration guide
- [Processing Modes](./README.md#processing-modes) - Fast vs Smart

## 🎉 Ready?

**Start now:**
```bash
docker-compose up --build
```

Or deploy:
```bash
./deploy.sh
```

**Questions?** Check the [QUICKREF.md](./QUICKREF.md) for common commands and troubleshooting.

---

**Current Status:**
✅ Full-stack app ready
✅ Cloud deployment ready  
✅ All documentation complete
✅ Production-ready setup

**Go build something amazing!** 🚀
