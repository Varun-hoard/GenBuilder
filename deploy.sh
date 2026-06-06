#!/bin/bash

# GenBuilder Quick Deploy Script
# Automates deployment setup to Railway and Vercel

set -e

echo "🚀 GenBuilder Deployment Setup"
echo "================================"
echo ""

# Check prerequisites
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Get deployment choice
echo "Choose your deployment option:"
echo "1) Railway (Backend) + Vercel (Frontend) - Recommended"
echo "2) Render (Backend) + Vercel (Frontend)"
echo "3) Fly.io (Backend) + Vercel (Frontend)"
echo "4) Local Development with Docker"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📋 Railway + Vercel Setup Instructions"
        echo "======================================="
        echo ""
        echo "1️⃣  Create a GitHub repository (if you haven't already):"
        echo "   git remote add origin https://github.com/YOUR_USERNAME/genbuilder.git"
        echo "   git push -u origin main"
        echo ""
        echo "2️⃣  Deploy Backend to Railway:"
        echo "   • Go to https://railway.app"
        echo "   • Click 'New Project' → 'Deploy from GitHub repo'"
        echo "   • Select your genbuilder repo"
        echo "   • Configure environment variables (see DEPLOYMENT.md)"
        echo "   • Note the deployed URL (e.g., genbuilder-api-prod.railway.app)"
        echo ""
        echo "3️⃣  Deploy Frontend to Vercel:"
        echo "   • Go to https://vercel.com"
        echo "   • Click 'Add New Project'"
        echo "   • Select your genbuilder repo"
        echo "   • Root Directory: 'frontend'"
        echo "   • Set VITE_API_URL to your Railway backend URL"
        echo "   • Deploy!"
        echo ""
        echo "✅ Your app will be available at your Vercel URL"
        ;;
    2)
        echo ""
        echo "📋 Render + Vercel Setup Instructions"
        echo "====================================="
        echo ""
        echo "1️⃣  Push to GitHub (if not done)"
        echo ""
        echo "2️⃣  Deploy Backend to Render:"
        echo "   • Go to https://render.com"
        echo "   • Click 'New+' → 'Web Service'"
        echo "   • Connect your GitHub account"
        echo "   • Select genbuilder repo"
        echo "   • Configure according to render.yaml"
        echo "   • Deploy!"
        echo ""
        echo "3️⃣  Deploy Frontend to Vercel (same as Railway option)"
        echo ""
        echo "⚠️  Note: Free tier on Render will spin down after 15 min inactivity"
        ;;
    3)
        echo ""
        echo "📋 Fly.io + Vercel Setup Instructions"
        echo "====================================="
        echo ""
        echo "1️⃣  Install Fly CLI:"
        echo "   curl -L https://fly.io/install.sh | sh"
        echo ""
        echo "2️⃣  Deploy Backend:"
        echo "   flyctl auth login"
        echo "   flyctl launch"
        echo "   flyctl deploy"
        echo ""
        echo "3️⃣  Deploy Frontend to Vercel (same as Railway option)"
        ;;
    4)
        echo ""
        echo "🐳 Local Development with Docker"
        echo "=================================="
        echo ""
        echo "Make sure Docker and Docker Compose are installed:"
        echo "  • Download Docker Desktop: https://www.docker.com/products/docker-desktop"
        echo ""
        echo "Start the full stack:"
        echo "  docker-compose up --build"
        echo ""
        echo "Then open:"
        echo "  • Frontend: http://localhost:3000"
        echo "  • Backend API: http://localhost:8000"
        echo "  • API Docs: http://localhost:8000/docs"
        echo ""
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📚 For more details, see DEPLOYMENT.md"
echo ""
