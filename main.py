"""
AI-Powered Amount Detection in Medical Documents
FastAPI service with OCR, normalization, and context classification
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import base64
from typing import Optional, List, Dict, Any

app = FastAPI(
    title="Medical Document Amount Detection API",
    version="1.0",
    description="Detect and classify monetary amounts from medical documents"
)

# -----------------------------
# Request Models
# -----------------------------

class TextRequest(BaseModel):
    text: Optional[str] = None
    image: Optional[str] = None


# -----------------------------
# Core Detector
# -----------------------------

class AmountDetector:
    """Core logic for amount detection and classification"""

    OCR_CORRECTIONS = {
        'O': '0', 'o': '0', 'l': '1', 'I': '1',
        'Z': '2', 'S': '5', 'B': '8',
        'G': '6', 'T': '7', 'D': '0'
    }

    CURRENCY_PATTERNS = {
        'INR': r'(?:INR|Rs\.?|₹|Rupees?)',
        'USD': r'(?:USD|\$|Dollars?)',
        'EUR': r'(?:EUR|€|Euros?)',
        'GBP': r'(?:GBP|£|Pounds?)'
    }

    CONTEXT_PATTERNS = {
        'total_bill': r'(?:total|grand total|bill amount|amount payable)',
        'paid': r'(?:paid|payment|amount paid|received)',
        'due': r'(?:due|balance|outstanding|remaining|payable)',
        'discount': r'(?:discount|off|reduction|rebate)',
        'tax': r'(?:tax|gst|vat|cgst|sgst)',
        'consultation': r'(?:consultation|doctor fee|consultation fee)',
        'medicine': r'(?:medicine|medication|drugs|pharmacy)',
        'lab_test': r'(?:lab|test|investigation|diagnostic)'
    }

    # -------- Step 1 --------
    def step1_extract(self, text: str) -> Dict[str, Any]:
        """Extracts number tokens with their position in text"""
        currency_hint = "INR"
        for curr, pattern in self.CURRENCY_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                currency_hint = curr
                break

        # Pattern covers:
        # 1. Standard numbers: 1,200.50
        # 2. OCR confusion starts: l200, S500, I00
        # 3. OCR confusion mixed: 10O, 1O0
        number_pattern = r'\b(?:\d+(?:,\d{3})*(?:\.\d{1,2})?|\d+|[lIOS]\d+|\d+[lIOS]\d*|[lIOS]{2,})\b'
        
        # Use finditer to get match objects with indices
        matches = list(re.finditer(number_pattern, text))
        
        if not matches:
            return {"status": "no_amounts_found", "reason": "document too noisy"}

        confidence = min(0.95, 0.6 + len(matches) * 0.05)

        raw_tokens = []
        for m in matches:
            raw_tokens.append({
                "text": m.group().strip(),
                "start": m.start(),
                "end": m.end()
            })

        return {
            "raw_tokens": raw_tokens,
            "currency_hint": currency_hint,
            "confidence": round(confidence, 2)
        }

    # -------- Step 2 --------
    def step2_normalize(self, raw_tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Normalizes tokens to float/int values"""
        normalized = []

        for token_obj in raw_tokens:
            token_str = token_obj["text"]
            
            if '%' in token_str:
                continue

            cleaned = token_str.replace(',', '')
            value = None

            try:
                val_float = float(cleaned)
                if val_float > 0:
                    value = int(val_float) if val_float.is_integer() else val_float
            except ValueError:
                # Attempt OCR correction
                corrected = ''.join(
                    self.OCR_CORRECTIONS.get(c, c) for c in cleaned
                )
                try:
                    val_float = float(corrected)
                    if val_float > 0:
                        value = int(val_float) if val_float.is_integer() else val_float
                except ValueError:
                    pass
            
            if value is not None:
                new_obj = token_obj.copy()
                new_obj["value"] = value
                normalized.append(new_obj)

        return {
            "normalized_amounts": normalized,
            "normalization_confidence": 0.82 if normalized else 0.3
        }

    # -------- Step 3 --------
    def step3_classify(self, text: str, amounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Classifies amounts based on surrounding context in original text"""
        if not amounts:
            return {"amounts": [], "confidence": 0.0}

        results = []
        text_lower = text.lower()

        for item in amounts:
            start_idx = item["start"]
            
            # Look at context around the ORIGINAL token position
            # 50 chars before, 20 chars after (including the token itself)
            context_start = max(0, start_idx - 50)
            context_end = min(len(text), item["end"] + 20)
            context = text_lower[context_start:context_end]

            matched = "unclassified"
            for k, pattern in self.CONTEXT_PATTERNS.items():
                if re.search(pattern, context):
                    matched = k
                    break

            # Create a clean result object, keeping the metadata needed for Step 4
            results.append({
                "type": matched,
                "value": item["value"],
                "start": item["start"],
                "end": item["end"],
                "text": item["text"]
            })

        return {"amounts": results, "confidence": 0.8}

    # -------- Step 4 --------
    def step4_final_output(self, text: str, currency: str, classified: List[Dict]) -> Dict:
        """Formats the final output using original source text"""
        final = []
        for item in classified:
            # Extract strict source from original text using indices
            source_text = text[item["start"]:item["end"]].strip()
            
            final.append({
                "type": item["type"],
                "value": item["value"],
                "source": source_text
            })

        return {"currency": currency, "amounts": final, "status": "ok"}

    def process_text(self, text: str) -> Dict[str, Any]:
        step1 = self.step1_extract(text)
        if step1.get("status") == "no_amounts_found":
            return step1

        step2 = self.step2_normalize(step1["raw_tokens"])
        step3 = self.step3_classify(text, step2["normalized_amounts"])
        final = self.step4_final_output(text, step1["currency_hint"], step3["amounts"])

        return {"step1": step1, "step2": step2, "step3": step3, "final": final}

    def simple_ocr(self, image_data: str) -> str:
        """
        Mock OCR implementation. 
        In a real scenario, this would use pytesseract or paddleocr.
        """
        base64.b64decode(image_data)
        return "T0tal: Rs l200\nPald: 1000\nDue: 200"


detector = AmountDetector()

# -----------------------------
# API Routes
# -----------------------------

@app.post("/api/detect")
def detect_amounts(payload: TextRequest):
    if payload.text:
        return detector.process_text(payload.text)

    if payload.image:
        text = detector.simple_ocr(payload.image)
        return detector.process_text(text)

    raise HTTPException(status_code=400, detail="Provide either text or image")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "medical-amount-detector"}


@app.get("/")
def root():
    return {
        "service": "Medical Document Amount Detection API",
        "docs": "/docs",
        "endpoint": "/api/detect"
    }
