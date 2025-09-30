"""
Main entry point for Railway deployment - Debug Mode
Temporarily using debug API to check environment variables
"""

from debug_api import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)