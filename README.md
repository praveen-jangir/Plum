# Medical Document Amount Detector

A FastAPI-based backend service for extracting and classifying financial amounts from medical documents (invoices, receipts, prescriptions).

## 🚀 Live Demo
[https://plum-eta.vercel.app/docs](https://plum-eta.vercel.app/docs)

## Features

-   **Extraction**: Identifies monetary values using regex patterns with position tracking.
-   **Normalization**: Converts text (e.g., "1,200", "l200") into standard numeric values.
-   **Classification**: Classifies amounts (Total, Paid, Due, Tax) based on surrounding context mapping.
-   **OCR Support**: Endpoint accepts base64-encoded images (currently uses a mock implementation, ready for Tesseract/PaddleOCR integration).
-   **Validation**: Rule-based guardrails to ensure high-confidence output.

## Architecture

The pipeline follows a modular 4-step process:
1.  **Extract**: Regex-based tokenization capturing value and position.
2.  **Normalize**: Cleaning and correcting OCR errors (e.g., 'S' -> '5').
3.  **Classify**: Context-aware mapping using keyword proximity matching.
4.  **Format**: Structured JSON response with raw source traceability.

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/praveen-jangir/Plum.git
cd Plum
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Service
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
The API will be available at `http://localhost:8080`.

## API Usage

### Endpoint: `POST /api/detect`

#### 1. Analyze Text
Input:
```json
{
  "text": "The Grand Total is Rs. 1,500\nAmount Paid: 500"
}
```

Response:
```json
{
  "step1": { ... },
  "step2": { ... },
  "step3": { ... },
  "final": {
    "currency": "INR",
    "amounts": [
        {
            "type": "total_bill",
            "value": 1500,
            "source": "1,500"
        },
        {
            "type": "paid",
            "value": 500,
            "source": "500"
        }
    ],
    "status": "ok"
  }
}
```

#### 2. Analyze Image (Base64)
Input:
```json
{
  "image": "base64_encoded_string_here..."
}
```

## Testing

You can use the provided bash script to test the endpoints:
```bash
bash test_api.sh
```

## Project Structure
- `main.py`: Core application logic and API routes.
- `requirements.txt`: Python project dependencies.

## Screenshots

### API Documentation
![API Docs](snapshot/api_docs.png)

### Sample Output
![API Output](snapshot/api_output.png)
```json
{
  "final": {
    "currency": "INR",
    "amounts": [
        {
            "type": "total_bill",
            "value": 1200,
            "source": "1,200"
        }
    ],
    "status": "ok"
  }
}
```
