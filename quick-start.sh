#!/bin/bash
# Quick Start Script for EcoImmo France 2026

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🏥 EcoImmo France 2026 - AI Property Doctor          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18.17+"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "⚠️  pnpm not found. Installing pnpm..."
    npm install -g pnpm
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.13+"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Some features may not work."
fi

echo "✅ Prerequisites check complete!"
echo ""

# Setup environment
echo "🔧 Setting up environment..."
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Mistral API key!"
fi

# Install dependencies
echo "📦 Installing dependencies..."
echo "   This may take a few minutes..."

# Frontend
echo "   → Installing frontend dependencies (pnpm)..."
pnpm install --silent

# Backend
echo "   → Installing backend dependencies (pip)..."
cd apps/api
python3 -m pip install -r requirements.txt --quiet
cd ../..

echo "✅ Dependencies installed!"
echo ""

# Generate demo images
echo "🎨 Generating demo images..."
python3 apps/api/scripts/generate_demo_images.py

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🚀 READY TO LAUNCH!                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Choose how to start:"
echo ""
echo "Option 1: Docker (Recommended)"
echo "  $ docker-compose up -d"
echo "  Frontend: http://localhost:3000"
echo "  API:      http://localhost:8000/docs"
echo ""
echo "Option 2: Manual"
echo "  Terminal 1: cd apps/api && uvicorn app.main:app --reload"
echo "  Terminal 2: cd apps/web && pnpm dev:turbo"
echo ""
echo "🏥 AI Property Doctor: http://localhost:3000/ai-doctor"
echo "📚 API Docs:           http://localhost:8000/docs"
echo ""
echo "✨ Enjoy the IMPOSSIBLE feature!"
echo ""
