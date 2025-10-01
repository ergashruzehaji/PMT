#!/bin/bash
# Railway Deployment Script for Property Maintenance Tracker

echo "🚀 Starting Railway deployment process..."

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway whoami || railway login

# Set environment variables for Railway
echo "⚙️  Setting environment variables..."

# You'll need to replace this with your actual Google Sheets credentials JSON
echo "📋 Please set your Google Sheets credentials in Railway dashboard:"
echo "   Variable name: GOOGLE_CREDENTIALS_JSON"
echo "   Value: Your Google Sheets service account JSON (as a string)"

echo "🌐 Setting SPREADSHEET_NAME..."
railway variables set SPREADSHEET_NAME="Property Management Tracker"

echo "🔧 Setting PORT..."
railway variables set PORT=8000

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at your Railway URL"
echo "📝 Don't forget to set GOOGLE_CREDENTIALS_JSON in the Railway dashboard!"