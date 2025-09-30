#!/bin/bash
echo "Testing Railway URLs..."

URLS=(
  "https://pmt-production-8f79794d.up.railway.app"
  "https://web-production-8f79794d.up.railway.app"
  "https://lavish-presence-production.up.railway.app"
  "https://pmt-production.up.railway.app"
  "https://web-production.up.railway.app"
)

for url in "${URLS[@]}"; do
  echo "Testing: $url"
  response=$(curl -s -w "%{http_code}" "$url/health" -o /dev/null)
  if [ "$response" = "200" ]; then
    echo "✅ FOUND: $url"
    echo "Your Railway URL is: $url"
    break
  else
    echo "❌ Not found (HTTP $response)"
  fi
done
