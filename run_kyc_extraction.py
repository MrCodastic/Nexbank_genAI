import json
import re
import time
from datetime import datetime
from llm_engine import BankingLLM

# --- 1. ROBUST PARSER (The Fix) ---
def parse_json_garbage(text):
    """
    Scrub the LLM output to find the JSON object hidden inside conversational text.
    """
    # 1. Try to find content between ```json and ``` 
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1)
    
    # 2. Or try to find content between the first { and last }
    else:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

    # 3. Clean up generic JSON errors
    text = text.strip()
    return json.loads(text)

# --- 2. THE EXTRACTION ENGINE ---
ai_engine = BankingLLM(provider="ollama") 

def extract_and_validate(raw_ocr_text):
    print(f"\n📄 INPUT: Received raw OCR text ({len(raw_ocr_text)} chars)...")
    
    # A. The Prompt (Simplified to just extraction)
    # We moved the 'Expiration Logic' OUT of the prompt. We just want the raw data.
    system_prompt = """
    You are a Data Extraction API. 
    Extract entities from the text below. 
    
    OUTPUT RULES:
    1. Return ONLY valid JSON.
    2. Convert all dates to standard ISO format: YYYY-MM-DD.
    3. If a field is missing, use null.
    
    JSON SCHEMA:
    {
        "full_name": "String",
        "dob_iso": "YYYY-MM-DD",
        "id_number": "String",
        "expiry_date_iso": "YYYY-MM-DD",
        "document_type": "String"
    }
    """

    start_time = time.time()
    # Call Model
    raw_response = ai_engine.generate_response(system_prompt, f"RAW TEXT: {raw_ocr_text}")
    duration = time.time() - start_time

    # B. The Parsing Layer (Fixes the "Chatty" LLM)
    try:
        clean_data = parse_json_garbage(raw_response)
    except Exception as e:
        print(f"❌ PARSING FAILED. Raw Output was:\n{raw_response}")
        return None, 0

    # C. The Validation Layer (Python Logic)
    # THIS is where real banking apps do the checks, not inside the LLM.
    risk_flags = []
    
    # Check Expiry
    if clean_data.get('expiry_date_iso'):
        try:
            exp_date = datetime.strptime(clean_data['expiry_date_iso'], "%Y-%m-%d")
            today = datetime.now() # Uses your computer's real clock
            
            if exp_date < today:
                risk_flags.append(f"DOCUMENT_EXPIRED (Expired on {clean_data['expiry_date_iso']})")
        except ValueError:
            risk_flags.append("INVALID_DATE_FORMAT")
            
    # Check ID Format (Simple regex example)
    if clean_data.get('id_number'):
        if "X" in clean_data['id_number']: # Example: Detect placeholder chars
            risk_flags.append("POTENTIAL_OCR_ERROR_IN_ID")

    # Attach computed flags to the object
    clean_data['risk_flags'] = risk_flags
    
    return clean_data, duration

# --- 3. RUN SIMULATION ---
if __name__ == "__main__":
    print("--- 🕵️ STARTING ROBUST KYC EXTRACTION 🕵️ ---")
    
    # Simulating a messy/expired passport scan
    messy_scan = """
    PASSPORT STATE
    Name: SARAH J. CONNOR
    DOB: 12 May 1984
    ID: 881209X
    Exp: 14 Aug 2024
    """
    
    data, time_taken = extract_and_validate(messy_scan)
    
    if data:
        print("\n--- ✅ VALIDATED OUTPUT ---")
        print(json.dumps(data, indent=2))
        
        print("\n--- ⚖️ REPORT CARD ---")
        print(f"⏱️ Time: {round(time_taken, 2)}s")
        if len(data['risk_flags']) > 0:
            print(f"🚩 RISKS DETECTED: {data['risk_flags']}")
        else:
            print("🟢 CLEAN: No risks found.")
            