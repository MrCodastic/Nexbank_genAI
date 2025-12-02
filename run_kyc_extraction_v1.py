import json
import time
from llm_engine import BankingLLM  # Re-using the engine we built earlier

# --- 1. SETUP THE ENGINE ---
ai_engine = BankingLLM(provider="ollama") 

def clean_kyc_document(raw_ocr_text):
    """
    Takes messy raw text and forces it into a strict JSON Schema.
    """
    print(f"\n📄 INPUT: Received raw OCR text ({len(raw_ocr_text)} chars)...")

    # A. The Strict Schema (The "Guardrails")
    # We tell the LLM exactly what format we need.
    target_schema = {
        "full_name": "String (Capitalized)",
        "date_of_birth": "DD-MM-YYYY",
        "document_type": "Passport | Driver License",
        "id_number": "String",
        "expiry_date": "DD-MM-YYYY",
        "risk_flags": ["List specific issues: 'Expired', 'Blurry', 'Mismatch' or empty list"]
    }

    # B. The Prompt Engineering
    system_prompt = f"""
    You are a Bank Compliance AI. 
    Task: Extract entities from the messy OCR text below into valid JSON.
    
    STRICT RULES:
    1. Output ONLY valid JSON. No markdown, no conversational text.
    2. Format all dates as DD-MM-YYYY.
    3. If the document is expired (compare to today's date: 2025-12-02), add "Expired" to risk_flags.
    4. Schema to follow: {json.dumps(target_schema)}
    """

    # C. Execute
    start_time = time.time()
    response_text = ai_engine.generate_response(system_prompt, f"RAW TEXT: {raw_ocr_text}")
    duration = time.time() - start_time
    
    return response_text, duration

# --- 2. THE SIMULATION DATA ---
# In a real bank, this string comes from Tesseract/AWS Textract.
# Here, we simulate a messy scan of a Passport.
messy_passport_scan = """
PASSPORT
Unied States of Amerca
P4SSPORT# 881209X
Surname: CONNOR
Given Names: SARAH J.
DOB: May 12, 1994
Sex: F
Place of Birth: Los Angeles
Date of Expiration: 14 Aug 2024
"""

# --- 3. RUN THE EXTRACTION ---
if __name__ == "__main__":
    print("--- 🕵️ STARTING KYC-X EXTRACTION MODULE 🕵️ ---")
    
    # Run the AI
    raw_json_output, time_taken = clean_kyc_document(messy_passport_scan)
    
    print("\n--- 🤖 AI OUTPUT (Raw) ---")
    print(raw_json_output)

    # --- 4. VALIDATION LOGIC ---
    print("\n--- ⚖️ VALIDATION REPORT ---")
    
    # Metric 1: Speed
    print(f"⏱️  Processing Time: {round(time_taken, 2)} seconds (Benchmark: <30s)")
    
    try:
        # Parse JSON to check structure
        data = json.loads(raw_json_output)
        
        # Metric 2: Field Accuracy
        if data['full_name'] == "Sarah J. Connor" or "Connor" in data['full_name']:
             print("✅ Name Extraction: PASS")
        else:
             print("❌ Name Extraction: FAIL")
             
        # Metric 3: Risk Logic (Did it catch the expiration?)
        if "Expired" in str(data['risk_flags']):
             print("✅ Fraud Detection: PASS (Correctly flagged expired document)")
        else:
             print("❌ Fraud Detection: FAIL (Missed expiration date)")
             
    except json.JSONDecodeError:
        print("❌ CRITICAL FAIL: Model did not output valid JSON.")