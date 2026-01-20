from paddleocr import PaddleOCR
import numpy as np
import cv2
import re

ocr = PaddleOCR(use_angle_cls=True, lang='en')

def extract_info_from_image(image_bytes: bytes):
    
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return {"error": "Invalid image format"}

    result = ocr.ocr(image)
    print(f"DEBUG: OCR Result Type: {type(result)}", flush=True)
    print(f"DEBUG: OCR Result: {result}", flush=True)
    
    if not result or result[0] is None:
        return {
            "answers": {},
            "missing_fields": ["all"],
            "confidence": 0.0,
            "status": "incomplete_profile",
            "reason": "No text detected"
        }

    raw_lines = []
    total_conf = 0
    count = 0
    
    if isinstance(result, dict):
        rec_texts = result.get('rec_texts', [])
        rec_scores = result.get('rec_scores', [])
        print(f"DEBUG: Found rec_texts: {rec_texts}", flush=True)
        
        for text, conf in zip(rec_texts, rec_scores):
            raw_lines.append(text)
            total_conf += conf
            count += 1
            
    elif isinstance(result, list):
        if not result or result[0] is None:
             pass 
        
        elif isinstance(result[0], dict):
             rec_texts = result[0].get('rec_texts', [])
             rec_scores = result[0].get('rec_scores', [])
             print(f"DEBUG: Found rec_texts in result[0]: {rec_texts}", flush=True)
             
             for text, conf in zip(rec_texts, rec_scores):
                raw_lines.append(text)
                total_conf += conf
                count += 1
        
        else:
             for line in result[0]:
                try:
                    if isinstance(line[1], tuple) or isinstance(line[1], list):
                        text = line[1][0]
                        conf = line[1][1]
                    else:
                        text = str(line[1])
                        conf = 0.0
                    raw_lines.append(text)
                    total_conf += conf
                    count += 1
                except Exception as e:
                    pass

    avg_confidence = total_conf / count if count > 0 else 0
    
    parsed_data = parse_lines_to_json(raw_lines)
    
    expected_keys = ["age", "smoker", "exercise", "diet"]
    found_keys = parsed_data.keys()
    missing_fields = [k for k in expected_keys if k not in found_keys]
    
    if len(missing_fields) > len(expected_keys) / 2:
        return {
            "status": "incomplete_profile",
            "reason": ">50% fields missing",
            "answers": parsed_data,
            "missing_fields": missing_fields,
            "confidence": round(avg_confidence, 2)
        }

    return {
        "answers": parsed_data,
        "missing_fields": missing_fields,
        "confidence": round(avg_confidence, 2)
    }

def parse_lines_to_json(lines):
    """
    Heuristic parser to convert lines into structured data.
    Handles "Key: Value" and ["Key:", "Value"].
    """
    data = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = re.match(r"([A-Za-z]+)\s*[:](.*)", line)
        if match:
            key = match.group(1).lower().strip()
            value = match.group(2).strip()
            
            if not value and i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if ":" not in next_line:
                    value = next_line
                    i += 1 
            
            if key == "age":
                try:
                    data[key] = int(re.search(r'\d+', value).group())
                except:
                    data[key] = value
            elif key == "smoker":
                if value.lower() in ["yes", "true", "y"]:
                    data[key] = True
                elif value.lower() in ["no", "false", "n"]:
                    data[key] = False
                else:
                    data[key] = value
            else:
                data[key] = value
        i += 1
    return data
