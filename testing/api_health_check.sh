#!/bin/bash

HOST_IP="localhost"
TOKEN=$(curl -u wazuh-wui:"$WAZUH_API_PASSWORD"-k -X POST "https://localhost:55000/security/user/authenticate?raw=true")
HTTP_CODE=$(curl -k -s -o response.json -w "%{http_code}" \
  -X GET "https://$HOST_IP:55000/" \
  -H "Authorization: Bearer $TOKEN")

if [ "$HTTP_CODE" -ne 200 ]; then
  echo "❌ API not reachable, HTTP $HTTP_CODE"
  exit 1
fi

# Check that required JSON fields exist
REQUIRED_FIELDS=("title" "api_version" "revision" "license_name" "hostname" "timestamp")
for field in "${REQUIRED_FIELDS[@]}"; do
  if ! jq -e ".data.$field" response.json >/dev/null; then
    echo "❌ Field '$field' missing in API response"
    exit 1
  fi
done

echo "✅ API health check passed"
