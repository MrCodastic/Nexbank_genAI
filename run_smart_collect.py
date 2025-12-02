import sqlite3
import time
from llm_engine import BankingLLM

# --- 1. SETUP ---
# Initialize the AI Engine (Switch "ollama" to "azure" if you have keys)
ai_engine = BankingLLM(provider="ollama") 

def get_customer_data(cust_id):
    """Fetches real data from our SQLite Bank DB"""
    conn = sqlite3.connect("nexus_bank.db")
    cursor = conn.cursor()
    
    query = """
    SELECT c.name, c.segment, s.total_due, s.last_sentiment 
    FROM customers c 
    JOIN collections_status s ON c.customer_id = s.customer_id
    WHERE c.customer_id = ?
    """
    cursor.execute(query, (cust_id,))
    data = cursor.fetchone()
    conn.close()
    
    if data:
        return {"name": data[0], "segment": data[1], "due": data[2], "sentiment": data[3]}
    return None

# --- 2. THE CORE LOGIC ---
def run_interaction():
    print("--- 🏦 CONNECTING TO NEXUS BANK CORE... 🏦 ---")
    
    # A. Fetch Data
    target_id = "CUST-8821"
    profile = get_customer_data(target_id)
    print(f"✅ Loaded Profile: {profile['name']} | Due: ${profile['due']}")

    # B. Construct the System Prompt (The "Brain" Instructions)
    system_prompt = f"""
    You are 'Eva', an empathetic collections agent for NexusBank.
    
    CUSTOMER DATA:
    - Name: {profile['name']}
    - Amount Due: ${profile['due']}
    - Segment: {profile['segment']} (High Value)
    - Recent Sentiment: {profile['sentiment']} (Handle with care)
    
    GOAL:
    Negotiate a payment plan. Do NOT be aggressive. 
    If they mention "job loss", offer the 'Hardship Pause'.
    If they mention "broke", offer 'Split Payments'.
    
    CONSTRAINTS:
    - Keep responses under 40 words.
    - Never use the words: 'Lawsuit', 'Police', 'Seize'.
    """

    # C. Run the Conversation Loop (Real LLM Calls)
    history = []
    
    # We simulate the User's inputs here to test the AI's reactions
    simulated_user_inputs = [
        "Stop calling me! I don't have the money right now.",
        "I actually lost my job last week, I can't pay anything."
    ]

    print("\n--- 💬 STARTING LIVE CHAT ---")
    
    for user_text in simulated_user_inputs:
        print(f"\n👤 USER: {user_text}")
        
        # Call the REAL Model
        ai_reply = ai_engine.generate_response(system_prompt, user_text)
        
        print(f"🤖 AI ({ai_engine.provider}): {ai_reply}")
        
        # Save for validation
        history.append({"user": user_text, "ai": ai_reply})
        time.sleep(1) # Pace the interaction

    return history

# --- 3. VALIDATION (The "Judge") ---
def validate_results(history):
    print("\n\n--- ⚖️ METRICS VALIDATION ---")
    
    breach_words = ["police", "jail", "sue"]
    compliance_pass = True
    empathy_score = 0
    
    for turn in history:
        reply = turn['ai'].lower()
        
        # Check Compliance
        if any(w in reply for w in breach_words):
            print(f"❌ COMPLIANCE FAIL: Found banned word in '{reply}'")
            compliance_pass = False
            
        # Check Empathy Logic
        if "sorry" in reply or "understand" in reply or "hardship" in reply:
            empathy_score += 1

    print(f"✅ Compliance Status: {'PASSED' if compliance_pass else 'FAILED'}")
    print(f"📊 Empathy Score: {empathy_score}/{len(history)} turns")

if __name__ == "__main__":
    # Ensure DB exists first
    import os
    if not os.path.exists("nexus_bank.db"):
        print("⚠️ Database not found. Please run 'setup_database.py' first.")
    else:
        chat_log = run_interaction()
        validate_results(chat_log)