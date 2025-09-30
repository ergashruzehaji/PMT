"""
Main entry point for Railway deployment - Google Sheets Integration
Uses pursuit.org Google Sheets setup with Railway
"""

from api_server import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)