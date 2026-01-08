#!/bin/bash
# API Test Script for EcoImmo France 2026
# Tests all major endpoints to verify the platform is working

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🧪 EcoImmo France 2026 - API Test Suite               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

API_URL="${API_URL:-http://localhost:8000}"
RESULTS_FILE="test-results.json"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_status="$4"
    local data="$5"

    echo -n "Testing: $name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_URL$endpoint" 2>&1)
    fi

    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (HTTP $status_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Expected HTTP $expected_status, got $status_code)"
        echo "   Response: $body"
        ((FAILED++))
        return 1
    fi
}

# Start tests
echo "🔍 Testing API availability..."
echo ""

# 1. Health Check
test_endpoint \
    "Health Check" \
    "GET" \
    "/health" \
    "200"

# 2. API Root
test_endpoint \
    "API Root" \
    "GET" \
    "/api/v1" \
    "200"

# 3. Property Search (will fail if no data, but should not error)
test_endpoint \
    "Property Search" \
    "GET" \
    "/api/v1/properties/search?code_postal=75015&limit=10" \
    "200"

# 4. DPE 2026 Analysis
test_endpoint \
    "DPE 2026 Calculator" \
    "POST" \
    "/api/v1/properties/analyze-dpe-2026" \
    "200" \
    '{
        "original_dpe_class": "F",
        "original_primary_energy": 621.0,
        "heating_kwh": 200.0,
        "hot_water_kwh": 40.0,
        "cooling_kwh": 5.0,
        "lighting_kwh": 10.0,
        "auxiliary_kwh": 15.0,
        "electricity_percentage": 0.95,
        "other_energy_sources": {"gas": 0.05},
        "surface_m2": 65.0,
        "is_rental_property": true
    }'

# 5. AI Property Doctor Demo Endpoint
test_endpoint \
    "AI Property Doctor Demo" \
    "GET" \
    "/api/v1/ai-doctor/demo" \
    "200"

# 6. GDPR Privacy Notice
test_endpoint \
    "GDPR Privacy Notice" \
    "GET" \
    "/api/v1/gdpr/privacy-notice" \
    "200"

# 7. Passoire Thermique Map
test_endpoint \
    "Passoire Thermique Map" \
    "GET" \
    "/api/v1/properties/passoire-thermique-map?code_postal=75015" \
    "200"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUMMARY                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Total tests:  $((PASSED + FAILED))"
echo -e "${GREEN}Passed:       $PASSED${NC}"
echo -e "${RED}Failed:       $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! API is working correctly.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start the frontend: cd apps/web && pnpm dev:turbo"
    echo "  2. Visit http://localhost:3000/ai-doctor"
    echo "  3. Try uploading a property photo!"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please check the API configuration.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Ensure the API is running: cd apps/api && uvicorn app.main:app --reload"
    echo "  - Check PostgreSQL is running: docker-compose up postgres -d"
    echo "  - Check Redis is running: docker-compose up redis -d"
    echo "  - Verify .env file has correct settings"
    exit 1
fi
