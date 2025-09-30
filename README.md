# Property Maintenance Tracker

A full-stack property maintenance tracking system with Google Sheets integration, SMS commands, and cost analytics.

## 🚀 Features

- **Real-time Task Management**: Add, complete, and track maintenance tasks
- **Google Sheets Integration**: All data persists to Google Sheets
- **SMS Commands**: Text "DONE [task]" to complete tasks
- **Cost Analytics**: Track emergency costs vs preventive maintenance
- **Email Notifications**: Automated reminders and confirmations
- **Modern UI**: React frontend with professional dashboard

## 📁 Project Structure

- `maintenance_tracker.py` - Core Python backend logic
- `api_server.py` - FastAPI REST API wrapper
- `frontend/maintenance_tracker_app.jsx` - React frontend component
- `frontend/package.json` - Node.js dependencies for frontend
- `requirements.txt` - Python dependencies for backend
- `nixpacks.toml` - Railway deployment configuration
- `runtime.txt` - Python runtime specification

## 🛠️ Local Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for React frontend)
- Google Cloud Service Account credentials

### Backend Setup
```bash
# Clone and navigate to project
git clone <your-repo-url>
cd property-maintenance-tracker

# Install Python dependencies
pip install -r requirements.txt

# Start API server
python api_server.py
```

The API will be available at http://localhost:8000

### Frontend Setup
```bash
# Install React dependencies
npm install

# Start development server
npm start
```

The frontend will be available at http://localhost:3000

## 🔧 Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account in IAM & Admin
5. Download the JSON key file as `credentials.json`
6. Share your Google Sheet with the service account email

## 📱 SMS Integration

The system supports SMS commands via Zapier/IFTTT integration:

- `DONE [task description]` - Mark task as complete
- `LIST [property name]` - Get pending tasks
- `ADD [property] [task] [date]` - Add new task

## 🌐 Deployment Options

### Option 1: Railway (Backend) + Vercel (Frontend)
- Deploy Python API to Railway
- Deploy React app to Vercel
- Connect via environment variables

### Option 2: Heroku
- Deploy full-stack to Heroku
- Add Google Sheets credentials via config vars

### Option 3: DigitalOcean App Platform
- Deploy both frontend and backend
- Managed database and scaling

## 🔑 Environment Variables

```bash
# For production deployment
GOOGLE_CREDENTIALS_JSON=<your-service-account-json>
SPREADSHEET_NAME="Property Management Tracker"
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## 🎯 Cost Savings Analytics

The system tracks:
- Preventive maintenance costs
- Emergency repair estimates
- 6x cost multiplier for emergency vs preventive
- ROI calculations and reporting

## 📊 API Endpoints

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}/complete` - Mark task complete
- `POST /api/sms/command` - Process SMS commands
- `GET /api/stats` - Dashboard statistics
- `POST /api/emergency` - Log emergency maintenance

Full API documentation available at `/docs` when running locally.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For questions or issues:
1. Check the `/docs` API documentation
2. Review Google Sheets setup steps
3. Verify credentials file placement
4. Check server logs for errors

Built with ❤️ for property managers who want to prevent expensive emergency repairs.