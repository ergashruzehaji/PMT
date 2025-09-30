#!/bin/bash
echo "🚀 Starting Property Maintenance Tracker..."
echo "📦 Installing dependencies..."

# Install Python dependencies
pip install -r requirements.txt

echo "🌐 Starting FastAPI server..."
if [ "$PORT" ]; then
    uvicorn api_server:app --host=0.0.0.0 --port=$PORT
else
    uvicorn api_server:app --host=0.0.0.0 --port=8000
fi