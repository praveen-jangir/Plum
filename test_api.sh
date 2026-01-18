#!/bin/bash
# test_api.sh - Verify the API endpoints

echo "Starting API Tests..."

echo "1. Testing /health..."
curl -s http://localhost:8080/health | grep "healthy" && echo "PASS" || echo "FAIL"

echo -e "\n2. Testing Text Detection (Basic)..."
response=$(curl -s -X POST "http://localhost:8080/api/detect" \
     -H "Content-Type: application/json" \
     -d '{"text": "Total bill amount is Rs 1,200. Paid 200."}')
echo "$response"

echo -e "\n3. Testing Text Detection (OCR Correction)..."
curl -s -X POST "http://localhost:8080/api/detect" \
     -H "Content-Type: application/json" \
     -d '{"text": "Total: l200. Discount: S00"}' | grep "1200" && echo "PASS" || echo "FAIL"
echo -e "\n4. Testing Image Detection (Mock)..."
curl -s -X POST "http://localhost:8080/api/detect" \
     -H "Content-Type: application/json" \
     -d '{"image": "dGVzdA=="}' # base64 for "test"

echo -e "\n\nTests Completed."
