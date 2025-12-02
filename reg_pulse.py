import chromadb
from chromadb.utils import embedding_functions
from llm_engine import BankingLLM # Re-using your existing engine

# --- 1. CONNECT TO MEMORY ---
client = chromadb.PersistentClient(path="./bank_memory")
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name="policy_docs", embedding_function=embed_fn)

# --- 2. CONNECT TO BRAIN ---
ai_engine = BankingLLM(provider="ollama") 

def consult_policy(user_question):
    print(f"\n❓ QUESTION: {user_question}")
    
    # A. RETRIEVAL (The Search)
    # Ask the DB: "What documents are semantically closest to this question?"
    results = collection.query(query_texts=[user_question], n_results=1)
    
    # Extract the best matching text
    best_match_text = results['documents'][0][0]
    best_match_source = results['metadatas'][0][0]['source']
    
    print(f"📖 FOUND EVIDENCE (from {best_match_source}): '{best_match_text}'")
    
    # B. GENERATION (The Answer)
    # We feed the evidence to the LLM so it doesn't hallucinate.
    system_prompt = f"""
    You are a Regulatory Assistant. Answer the user strictly based on the context provided.
    
    CONTEXT RULE: {best_match_text}
    
    If the answer is not in the context, say "I cannot find a policy for that."
    """
    
    answer = ai_engine.generate_response(system_prompt, user_question)
    return answer, best_match_source

# --- 3. SIMULATION LOOP ---
if __name__ == "__main__":
    print("--- 🏛️ STARTING REGPULSE (RAG ENGINE) 🏛️ ---")
    
    questions = [
        "What is the maximum limit for a personal loan?",
        "Can a crypto startup get a business loan?",
        "Can I use my personal iPad for work?"
    ]
    
    for q in questions:
        ai_ans, source = consult_policy(q)
        print(f"🤖 AI ANSWER: {ai_ans}")
        print(f"✅ CITATION: Verified against {source}\n" + "-"*40)