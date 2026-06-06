@echo off
REM GenBuilder Quick Deploy Script for Windows

echo.
echo 🚀 GenBuilder Deployment Setup
echo ================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Git is not installed. Please install Git first.
    exit /b 1
)

echo Choose your deployment option:
echo 1) Railway (Backend) + Vercel (Frontend) - Recommended
echo 2) Render (Backend) + Vercel (Frontend)
echo 3) Fly.io (Backend) + Vercel (Frontend)
echo 4) Local Development with Docker
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo 📋 Railway + Vercel Setup Instructions
    echo =======================================
    echo.
    echo 1️⃣  Create a GitHub repository (if you haven't already):
    echo    git remote add origin https://github.com/YOUR_USERNAME/genbuilder.git
    echo    git push -u origin main
    echo.
    echo 2️⃣  Deploy Backend to Railway:
    echo    • Go to https://railway.app
    echo    • Click 'New Project' → 'Deploy from GitHub repo'
    echo    • Select your genbuilder repo
    echo    • Configure environment variables (see DEPLOYMENT.md)
    echo    • Note the deployed URL
    echo.
    echo 3️⃣  Deploy Frontend to Vercel:
    echo    • Go to https://vercel.com
    echo    • Click 'Add New Project'
    echo    • Select your genbuilder repo
    echo    • Root Directory: 'frontend'
    echo    • Set VITE_API_URL to your Railway backend URL
    echo    • Deploy!
) else if "%choice%"=="2" (
    echo.
    echo 📋 Render + Vercel Setup Instructions
    echo ====================================
    echo.
    echo See deploy.sh for similar instructions
) else if "%choice%"=="3" (
    echo.
    echo 📋 Fly.io + Vercel Setup Instructions
    echo ===================================
    echo.
    echo 1️⃣  Install Fly CLI:
    echo    • Download from https://fly.io/docs/hands-on/install/
    echo.
    echo 2️⃣  Deploy Backend:
    echo    flyctl auth login
    echo    flyctl launch
    echo    flyctl deploy
) else if "%choice%"=="4" (
    echo.
    echo 🐳 Local Development with Docker
    echo =================================
    echo.
    echo Make sure Docker Desktop is installed:
    echo   https://www.docker.com/products/docker-desktop
    echo.
    echo Start the full stack:
    echo   docker-compose up --build
    echo.
    echo Then open:
    echo   • Frontend: http://localhost:3000
    echo   • Backend API: http://localhost:8000
    echo   • API Docs: http://localhost:8000/docs
) else (
    echo ❌ Invalid choice
    exit /b 1
)

echo.
echo 📚 For more details, see DEPLOYMENT.md
echo.
