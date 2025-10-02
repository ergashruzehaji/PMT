# 🚀 Production Environment Setup Guide

## ✅ Current Status: localhost:3000 is working perfectly

Your localhost setup is now fully functional with:

- **Frontend**: http://localhost:3000/PMT  
- **API**: http://localhost:8000
- **Google Sheets**: Full sync with MM-DD-YYYY formatting
- **Credentials**: Working from local file

## 🎯 Goal: Make Production Work Like localhost:3000

### Option 1: Railway Environment Variables (Recommended for API)

**Steps to set up Railway:**

1. **Go to your Railway project**: https://railway.app/dashboard
1. **Select your PMT service**
1. **Click "Variables" tab**
1. **Add these environment variables:**

```bash
# Variable Name: GOOGLE_CREDENTIALS_JSON
# Variable Value: (Run ./setup_railway_env.sh to get the exact value)

# Variable Name: SPREADSHEET_NAME  
# Variable Value:
Property Management Tracker
```

1. **Click "Deploy" to redeploy with new environment variables**

### Option 2: GitHub Actions (Automatic Deployment)

**Already set up!** The `.github/workflows/deploy.yml` file will automatically:

- Deploy your frontend to GitHub Pages when you push to main branch
- Keep GitHub Pages synchronized with your code

### Option 3: Easy Copy-Paste Setup

**Run this command for exact values:**

```bash
cd /Users/eruzehaji/Desktop/PMT && ./setup_railway_env.sh
```

## 🎯 What This Achieves

**After setting Railway environment variables:**

1. **Railway API**: Will work exactly like your localhost:8000
   - ✅ Google Sheets sync with MM-DD-YYYY formatting
   - ✅ All CRUD operations (create, read, update, delete)
   - ✅ Same functionality as localhost

1. **GitHub Pages**: Already working at https://ergashruzehaji.github.io/PMT/
   - ✅ Same React app as localhost:3000/PMT
   - ✅ Automatically connects to Railway API in production
   - ✅ Smart API detection (localhost in dev, Railway in production)

## 🚀 Quick Test After Setup

**Test Railway API:**

```bash
curl https://pmt-production-a984.up.railway.app/api/stats
```

**Test task creation:**

```bash
curl -X POST https://pmt-production-a984.up.railway.app/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"property_name":"Test Production","task_description":"Testing Railway deployment","due_date":"2025-11-01","priority":"High","category":"Testing","estimated_cost":100}'
```

## ✅ Result: Perfect Production Parity

Once Railway environment variables are set:

- **localhost:3000/PMT** ↔️ **GitHub Pages** (same frontend)
- **localhost:8000** ↔️ **Railway API** (same backend + Google Sheets)
- **Same Google Sheets** (shared across all environments)
- **Same MM-DD-YYYY formatting** everywhere

**Your production will work exactly like localhost:3000** 🎉