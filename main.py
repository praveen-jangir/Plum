from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import ocr_service
import llm_service
import json

app = FastAPI(title="Health Risk Profiler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SurveyResponse(BaseModel):
    answers: Dict[str, Any]

@app.get("/")
def health_check():
    return {"status": "running", "service": "Health Risk Profiler"}

@app.post("/analyze-json")
def analyze_json(payload: Dict[str, Any]):
   
    data = payload
    if "answers" in payload:
        data = payload["answers"]
    elif "additionalProp1" in payload:
        data = payload["additionalProp1"]

   
    expected_fields = ["age", "smoker", "exercise", "diet"]
    matches = [k for k in expected_fields if k in data]
    
    if len(matches) < len(expected_fields) / 2:
        return {
            "status": "incomplete_profile",
            "reason": ">50% fields missing"
        }

    llm_result = llm_service.analyze_health_profile(data)
    
    return {
        "answers": data,
        "missing_fields": [],
        "confidence": 1.0, 
        "factors": llm_result.get("risk_factors", []),
        "risk_level": llm_result.get("risk_level", "Unknown").lower(),
        "score": llm_result.get("score", 0),
        "rationale": llm_result.get("rationale", ""),
        "recommendations": llm_result.get("recommendations", []),
        "status": "ok"
    }

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Step 1 (Image Input) -> Step 2,3,4
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    
    ocr_result = ocr_service.extract_info_from_image(image_bytes)
    
    if ocr_result.get("status") == "incomplete_profile":
        return {
            "status": "incomplete_profile",
            "reason": ">50% fields missing",
            "answers": ocr_result.get("answers", {})
        }
    
    user_answers = ocr_result.get("answers", {})
    
    llm_result = llm_service.analyze_health_profile(user_answers)
    
    return {
        "answers": user_answers,
        "missing_fields": ocr_result.get("missing_fields", []),
        "confidence": ocr_result.get("confidence", 0.0),
        "factors": llm_result.get("risk_factors", []),
        "risk_level": llm_result.get("risk_level", "Unknown").lower(),
        "score": llm_result.get("score", 0),
        "rationale": llm_result.get("rationale", ""),
        "recommendations": llm_result.get("recommendations", []),
        "status": "ok"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
