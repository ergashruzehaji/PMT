#!/bin/bash

# Force Railway redeploy by updating timestamp
echo "# Force Railway redeploy $(date)" >> railway_redeploy.txt

# Add and commit
git add .
git commit -m "Force Railway redeploy $(date)"

# Push to trigger deployment
git push origin main

echo "Redeploy triggered. Check Railway dashboard for deployment status."
echo "Railway URL: https://pmt-production-a984.up.railway.app"