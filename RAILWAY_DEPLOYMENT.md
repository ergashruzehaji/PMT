# 🚀 Railway Deployment Guide

## Project Structure

This repository contains:
- **Backend API** (Python FastAPI) - Root directory
- **Frontend** (React) - `frontend/` directory

Railway will automatically deploy the Python API from the root directory.

## Quick Deploy to Railway

### Step 1: Deploy from GitHub

1. **Go to [railway.app](https://railway.app)**
2. **Sign up/Login** with your GitHub account
3. **Click "Deploy from GitHub repo"**
4. **Select `ergashruzehaji/PMT`**
5. **Railway will automatically detect Python and start building!**

### Step 2: Set Environment Variables

After deployment starts, add these environment variables in Railway:

#### Required Variables:
- `GOOGLE_CREDENTIALS_JSON` = `{paste your entire credentials.json content here}`
- `SPREADSHEET_NAME` = `Property Management Tracker`

#### Optional Variables:
- `EMAIL_HOST` = `smtp.gmail.com`
- `EMAIL_USER` = `your-email@gmail.com`
- `EMAIL_PASSWORD` = `your-app-password`

### Step 3: Your App URLs

Once deployed, Railway will give you:
- **API Base URL**: `https://your-app-name.railway.app`
- **API Documentation**: `https://your-app-name.railway.app/docs`
- **Health Check**: `https://your-app-name.railway.app/health`

### Step 4: Test Your Deployment

1. Visit your API docs URL
2. Try the `/health` endpoint
3. Test creating a task via the API
4. Check your Google Sheet for the new data!

## 🔧 Environment Variables Setup

### Getting Google Credentials JSON:
1. Follow the `GOOGLE_SHEETS_SETUP.md` guide
2. Download your service account JSON file
3. Copy the ENTIRE contents (it's a large JSON object)
4. Paste it as the value for `GOOGLE_CREDENTIALS_JSON` in Railway

### Example Environment Variables in Railway:
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-123456",...}
SPREADSHEET_NAME=Property Management Tracker
```

## 🎯 After Deployment

Your Property Maintenance Tracker API will be live and ready to:
- ✅ Accept REST API calls
- ✅ Save data to Google Sheets
- ✅ Process SMS commands
- ✅ Send email notifications
- ✅ Generate cost analytics

## 🔗 Connect Frontend

Update your React app's `API_BASE_URL` to point to your Railway deployment:
```javascript
const API_BASE_URL = 'https://your-app-name.railway.app/api';
```

## 📊 Monitoring

Railway provides:
- Real-time logs
- Metrics and usage
- Automatic HTTPS
- Custom domains (if needed)

Your maintenance tracker is now live and scalable! 🎉