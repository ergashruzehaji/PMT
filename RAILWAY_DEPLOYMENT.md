# 🚀 Railway Deployment Guide - Property Maintenance Tracker

## APIs Used in This Application

### 1. **FastAPI Backend API**
- **Purpose**: Main REST API server for the Property Maintenance Tracker
- **Port**: 8000 (configurable via PORT environment variable)
- **Endpoints**:
  - `GET /` - Health check
  - `POST /api/tasks` - Create new maintenance task
  - `GET /api/tasks` - Get all tasks
  - `PUT /api/tasks/{task_id}` - Update task
  - `DELETE /api/tasks/{task_id}` - Delete task

### 2. **Google Sheets API**
- **Purpose**: Data storage and synchronization
- **Library**: gspread with oauth2client
- **Spreadsheet**: "Property Management Tracker"
- **Authentication**: Service Account JSON credentials

### 3. **Railway Platform API**
- **Purpose**: Cloud deployment and hosting
- **Domain**: `*.up.railway.app`

## FIXED ISSUES ✅

1. **Duplicate Import Error** - Removed duplicate maintenance_tracker import in api_server.py
2. **Duplicate Main Block** - Fixed main.py to have single entry point
3. **CORS Configuration** - Added Railway URLs to CORS allow list
4. **Port Configuration** - Fixed port handling for Railway environment
5. **Path Issues** - Fixed hardcoded local paths to use relative paths
6. **Frontend Configuration** - Updated config.js to auto-detect production vs development

## Quick Railway Deployment

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