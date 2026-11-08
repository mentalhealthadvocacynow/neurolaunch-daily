FIELDS = {"title", "summary", "category", "short_version", "why_it_matters", "actions", "limitations"}

def validate(data):
    if not isinstance(data, dict) or set(data)!=FIELDS: raise ValueError("Unexpected output fields")
    for key in FIELDS - {"actions"}:
        if not isinstance(data[key], str) or not data[key].strip(): raise ValueError(f"Invalid {key}")
        if len(data[key])>6000: raise ValueError(f"Oversized {key}")
    if not isinstance(data["actions"], list) or not 1<=len(data["actions"])<=3: raise ValueError("Expected 1–3 actions")
    if any(not isinstance(x,str) or not x.strip() or len(x)>1200 for x in data["actions"]): raise ValueError("Invalid action")
    return data
