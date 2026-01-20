import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HF_API_KEY", "hf_Placeholder")
base_url = "https://router.huggingface.co/v1"

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

def analyze_health_profile(user_profile: dict):
    if "PLACEHOLDER" in api_key:
        return {
            "risk_factors": ["Configuration Error"],
            "risk_level": "Config Missing",
            "rationale": "Please update .env with a valid HF_API_KEY",
            "recommendations": ["Open .env file", "Paste your Hugging Face API Token"]
        }
    
    profile_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in user_profile.items()])
    
    system_prompt = (
        "You are a health risk profiler. Analyze the input data. "
        "1. Identify risk factors. "
        "2. Classify the overall risk level (Low, Medium, or High). "
        "3. Provide actionable recommendations. "
        "Return strictly valid JSON with the following schema: "
        "{"
        "  \"risk_factors\": [\"factor1\", \"factor2\"], "
        "  \"risk_level\": \"High/Medium/Low\", "
        "  \"score\": 75, "
        "  \"rationale\": \"Short explanation for the risk level\", "
        "  \"recommendations\": [\"rec1\", \"rec2\"] "
        "}"
    )

    try:
        completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": profile_str
                }
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        content = completion.choices[0].message.content
        
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        else:
            raise ValueError("No JSON found in response")

    except Exception as e:
        print(f"LLM Error: {e}")
        return {
            "risk_factors": ["Error processing profile"],
            "risk_level": "Unknown",
            "rationale": f"LLM Service Unreachable or Error: {str(e)}",
            "recommendations": ["Consult a real doctor."]
        }
