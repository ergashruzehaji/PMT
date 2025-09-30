"""
Debug version of API server to see what's happening on Railway
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json

app = FastAPI(title="Debug Property Maintenance Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/debug")
async def debug_environment():
    """Debug endpoint to see Railway environment"""
    debug_info = {
        "environment_variables": {
            "GOOGLE_CREDENTIALS_JSON_exists": bool(os.getenv('GOOGLE_CREDENTIALS_JSON')),
            "SPREADSHEET_NAME": os.getenv('SPREADSHEET_NAME', 'NOT_SET'),
            "PORT": os.getenv('PORT', 'NOT_SET'),
        },
        "google_libs_available": False,
        "maintenance_tracker_status": "unknown"
    }
    
    # Check if Google libraries are available
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        debug_info["google_libs_available"] = True
    except ImportError as e:
        debug_info["google_import_error"] = str(e)
    
    # Try to initialize tracker
    try:
        google_creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if google_creds_json:
            debug_info["google_creds_length"] = len(google_creds_json)
            debug_info["google_creds_starts_with"] = google_creds_json[:50] + "..."
            
            # Try to parse JSON
            try:
                creds_dict = json.loads(google_creds_json)
                debug_info["google_creds_valid_json"] = True
                debug_info["google_creds_type"] = creds_dict.get("type", "unknown")
                debug_info["google_creds_project_id"] = creds_dict.get("project_id", "unknown")
            except json.JSONDecodeError as e:
                debug_info["google_creds_json_error"] = str(e)
                debug_info["google_creds_valid_json"] = False
        else:
            debug_info["google_creds_status"] = "NOT_FOUND"
    
    except Exception as e:
        debug_info["tracker_init_error"] = str(e)
    
    return debug_info

@app.get("/")
async def root():
    return {"message": "Debug Property Maintenance Tracker API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "tracker_available": False, "debug_mode": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))