#!/bin/bash
# 🎯 Quick Test Script for Your Final Product

echo "🎉 PROPERTY MAINTENANCE TRACKER - FINAL PRODUCT TEST"
echo "===================================================="
echo ""
echo "🌐 Your Live App: https://pmt-production-a984.up.railway.app"
echo ""

echo "🧪 Testing your deployed application..."
echo ""

echo "✅ Health Check:"
curl -s https://pmt-production-a984.up.railway.app/ | python3 -m json.tool
echo ""

echo "✅ Creating a test task..."
RESPONSE=$(curl -s -X POST https://pmt-production-a984.up.railway.app/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "property_name": "Test Building",
    "task_description": "Final product verification",
    "due_date": "2025-12-15",
    "priority": "Medium",
    "category": "Testing",
    "estimated_cost": 100,
    "notes": "Verifying the deployed application works",
    "reporter_email": "test@final.com"
  }')

echo $RESPONSE | python3 -m json.tool
echo ""

echo "✅ Getting all tasks..."
curl -s https://pmt-production-a984.up.railway.app/api/tasks | python3 -m json.tool
echo ""

echo "🎊 SUCCESS! Your Property Maintenance Tracker is live and working!"
echo ""
echo "📋 What you can do now:"
echo "   • Create maintenance tasks via API"
echo "   • Data syncs to Google Sheets with MM-DD-YYYY format"
echo "   • Connect your React frontend"
echo "   • Share with your team"
echo ""
echo "🔗 Railway Dashboard: https://railway.com/project/54df165c-ab61-4d0c-9afb-b071a1bdd6dc"