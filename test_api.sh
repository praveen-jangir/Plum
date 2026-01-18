#!/bin/bash
# test_api.sh - Verify the API endpoints

echo "Starting API Tests..."

# 1. Test Health Check
echo "1. Testing /health..."
curl -s http://localhost:8080/health | grep "healthy" && echo "PASS" || echo "FAIL"

# 2. Test Text Extraction (Formatted Numbers)
echo -e "\n2. Testing Text Detection (Basic)..."
response=$(curl -s -X POST "http://localhost:8080/api/detect" \
     -H "Content-Type: application/json" \
     -d '{"text": "Total bill amount is Rs 1,200. Paid 200."}')
echo "$response"

# 3. Test Text with OCR Errors
echo -e "\n3. Testing Text Detection (OCR Correction)..."
# 'l200' should be normalized to 1200, 'S00' to 500
curl -s -X POST "http://localhost:8080/api/detect" \
     -H "Content-Type: application/json" \
     -d '{"text": "Total: l200. Discount: S00"}' | grep "1200" && echo "PASS" || echo "FAIL"

# 4. Test Image Payload (Mock)
echo -e "\n4. Testing Image Detection (Mock)..."
curl -s -X POST "http://localhost:8080/api/detect" \
     -H "Content-Type: application/json" \
     -d '{"image": "dGVzdA=="}' # base64 for "test"

echo -e "\n\nTests Completed."
