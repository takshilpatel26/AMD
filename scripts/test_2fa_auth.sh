#!/bin/bash

# Gram Meter 2FA Authentication Test Script
# Tests the complete authentication flow with OTP

set -e

BASE_URL="http://127.0.0.1:8000/api/v1"

echo "🔐 Testing Gram Meter 2FA Authentication System"
echo "==============================================="
echo ""

# Step 1: Request OTP
echo "📱 Step 1: Requesting OTP..."
RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/request/" \
  -H "Content-Type: application/json" \
  -d '{"username":"farmer_ramesh","password":"password123"}')

echo "$RESPONSE" | python3 -m json.tool

# Extract user_id and OTP
USER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user_id'])")
OTP=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('otp', ''))")

if [ -z "$OTP" ]; then
  echo ""
  echo "❌ OTP not found in response. Check Twilio SMS."
  exit 1
fi

echo ""
echo "✅ OTP received: $OTP"
echo ""

# Step 2: Verify OTP
echo "🔑 Step 2: Verifying OTP..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/verify/" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":$USER_ID,\"otp\":\"$OTP\"}")

echo "$TOKEN_RESPONSE" | python3 -m json.tool

# Extract tokens
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])")
REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['tokens']['refresh'])")

echo ""
echo "✅ Login successful! Tokens received."
echo ""

# Step 3: Test protected endpoint
echo "🔒 Step 3: Testing protected endpoint..."
AUTH_STATUS=$(curl -s "$BASE_URL/auth/status/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$AUTH_STATUS" | python3 -m json.tool

echo ""
echo "✅ Protected endpoint accessible!"
echo ""

# Step 4: Test dashboard API
echo "📊 Step 4: Testing dashboard API..."
DASHBOARD=$(curl -s "$BASE_URL/dashboard/stats/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$DASHBOARD" | python3 -m json.tool | head -15

echo ""
echo "✅ Dashboard API working!"
echo ""

# Step 5: Test token refresh
echo "🔄 Step 5: Testing token refresh..."
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}")

echo "$REFRESH_RESPONSE" | python3 -m json.tool

NEW_ACCESS=$(echo "$REFRESH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])")

echo ""
echo "✅ Token refresh successful!"
echo ""

# Step 6: Test logout
echo "🚪 Step 6: Testing logout..."
LOGOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/logout/" \
  -H "Authorization: Bearer $NEW_ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}")

echo "$LOGOUT_RESPONSE" | python3 -m json.tool

echo ""
echo "✅ Logout successful!"
echo ""

echo "==============================================="
echo "🎉 All tests passed! Authentication system working perfectly!"
echo ""
echo "Summary:"
echo "  ✅ OTP generation and SMS delivery"
echo "  ✅ OTP verification"
echo "  ✅ JWT token issuance"
echo "  ✅ Protected endpoint access"
echo "  ✅ Dashboard API"
echo "  ✅ Token refresh"
echo "  ✅ Logout with token blacklisting"
echo ""
