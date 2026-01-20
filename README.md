# AI-Powered Health Risk Profiler

## Overview
This service analyzes lifestyle survey responses to generate a structured health risk profile. It uses **PaddleOCR** for extracting text from images and **Mistral-7B** (via Hugging Face API) for intelligent risk assessment and recommendation generation.

## Features
- **OCR Implementation**: Extracts text from scanned forms/images.
- **Factor Extraction**: Identifies key risk factors from unstructured text.
- **Risk Classification**: Determines Low/Medium/High risk levels.
- **Recommendations**: Generates actionable health advice.
- **Guardrails**: Rejects incomplete profiles (>50% missing fields).

## Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create a `.env` file in the root directory and add your Hugging Face API Key:
   ```env
   HF_API_KEY=hf_your_key_here
   ```

## Running the Server
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

## API Usage

### 1. Optimize Text/JSON Input
**Endpoint**: `POST /analyze-json`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/analyze-json" \
     -H "Content-Type: application/json" \
     -d '{"age": 42, "smoker": "yes", "exercise": "rarely", "diet": "high sugar"}'
```

**Response:**
```json
{
  "status": "ok",
  "risk_level": "High",
  "factors": ["Age", "Smoker", "Poor Diet", "Sedentary"],
  "recommendations": ["Quit smoking", "Consult a nutritionist"],
  "rationale": "Combination of smoking and high sugar diet..."
}
```

### 2. Optimize Image Input
**Endpoint**: `POST /analyze-image`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/analyze-image" \
     -F "file=@/path/to/sample_receipt.png"
```

## Architecture
- **OCR Service**: `ocr_service.py` uses PaddleOCR to convert images to text.
- **LLM Service**: `llm_service.py` formats prompts and calls the Hugging Face Inference API.
- **Main API**: `main.py` handles routing, guardrails, and orchestration.

## Testing
Run the included test script:
```bash
python test_app.py
```
