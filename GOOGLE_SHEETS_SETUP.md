# Google Sheets Setup Guide

## 📋 Prerequisites
You need a Google account and access to Google Cloud Console.

## 🔧 Step-by-Step Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Project name: `property-maintenance-tracker`
4. Click "Create"

### 2. Enable Required APIs
1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for and enable these APIs:
   - **Google Sheets API**
   - **Google Drive API**

### 3. Create Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Service account name: `maintenance-tracker-service`
4. Click "Create and Continue"
5. Grant role: "Editor" (for full access)
6. Click "Done"

### 4. Generate Credentials File
1. In "Credentials", find your service account
2. Click on the service account name
3. Go to "Keys" tab
4. Click "Add Key" → "Create new key"
5. Choose "JSON" format
6. Click "Create" - this downloads your credentials file

### 5. Set Up Google Sheet
1. Create a new Google Sheet
2. Name it: "Property Management Tracker"
3. Create a worksheet named: "Maintenance Tasks"
4. Add these column headers in row 1:
   - A1: Property
   - B1: Task Description
   - C1: Due Date
   - D1: Priority
   - E1: Status
   - F1: Reporter Email
   - G1: Estimated Cost
   - H1: Actual Cost

### 6. Share Sheet with Service Account
1. In your Google Sheet, click "Share"
2. Add the service account email (found in your credentials JSON)
3. Give "Editor" permissions
4. Click "Send"

## 🚀 For Local Development
1. Save the downloaded JSON file as `credentials.json` in your project root
2. Make sure `credentials.json` is in your `.gitignore` (it already is!)

## ☁️ For Railway Deployment
1. Copy the entire contents of your `credentials.json` file
2. In Railway, add it as an environment variable named `GOOGLE_CREDENTIALS_JSON`
3. Add `SPREADSHEET_NAME` environment variable with value: `Property Management Tracker`

## 🔐 Security Note
- Never commit `credentials.json` to Git
- Use environment variables for production
- The service account has limited access (only to shared sheets)

## ✅ Test Your Setup
Run your API server locally and check if the Google Sheets connection works!