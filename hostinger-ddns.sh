#!/bin/bash

# --- CONFIGURE THESE ---
# PASTE THE EXACT TOKEN HERE, ENSURE NO EXTRA SPACES INSIDE THE QUOTES
API_TOKEN="1P71h0oyANpWiNUkiUkSVNhxxp9afC7kfCMt5EYfa458142b" 

DOMAIN="ashwath.space"
SUBDOMAIN="vpn"
TEST_IP="1.1.1.1" # IP for testing update
TTL=60
# --- END CONFIGURATION ---

curl -v -X PUT "https://api.hostinger.com/api/dns/v1/zones/$DOMAIN" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: PostmanRuntime/7.32.3" \
  -d "$JSON_PAYLOAD"

# API URL for the PUT request (v1 endpoint)
API_URL_PUT="https://api.hostinger.com/api/dns/v1/zones/$DOMAIN" 

# JSON Payload - Using direct string construction to avoid jq dependency for this test
JSON_PAYLOAD='{
  "overwrite": true,
  "zone": [
    {
      "name": "'"$SUBDOMAIN"'",
      "records": [
        {
          "content": "'"$TEST_IP"'"
        }
      ],
      "ttl": '$TTL',
      "type": "A"
    }
  ]
}'

echo "--- Debugging API Call ---"
echo "URL: $API_URL_PUT"
echo "Token (first 5 / last 5 chars): ${API_TOKEN:0:5}...${API_TOKEN: -5}" # Verify start/end
echo "Payload being sent:"
echo "$JSON_PAYLOAD"
echo "--------------------------"
echo "Executing curl command with verbose output (-v)..."
echo "" # Add a blank line for clarity

# Execute curl with verbose output (-v)
# Ensure Authorization header is formatted correctly
curl -v -X PUT "$API_URL_PUT" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$JSON_PAYLOAD"

# Capture exit status if needed (optional)
CURL_EXIT_STATUS=$? 

echo "" # Add a blank line for clarity
echo "--------------------------"
echo "Curl command finished with exit status: $CURL_EXIT_STATUS"
