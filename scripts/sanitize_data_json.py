import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from models.schemas import QuestionModel

with open("data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned_data = []
for item in data:
    opts = item.get("options", {})
    clean_opts = {k: str(v) for k, v in opts.items() if k in ("A", "B", "C", "D") and v is not None}
    item["options"] = clean_opts
    
    if not item.get("source"):
        item["source"] = {"name": "DDCET Question Bank", "page": 1}
        
    try:
        validated = QuestionModel(**item)
        cleaned_data.append(validated.model_dump())
    except Exception as e:
        print(f"Skipping invalid item {item.get('id')}: {e}")

print(f"Total valid MCQs ready: {len(cleaned_data)} / {len(data)}")

with open("data/data.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("data/data.json successfully sanitized and saved!")
