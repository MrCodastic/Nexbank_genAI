import chromadb
from chromadb.utils import embedding_functions

# --- 1. SETUP THE DATABASE ---
# We use a local persistent storage (a folder named 'bank_memory')
client = chromadb.PersistentClient(path="./bank_memory")

# Use a free, high-quality embedding model (MiniLM)
# This turns text into a list of numbers (vectors)
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create (or get) the collection
collection = client.get_or_create_collection(name="policy_docs", embedding_function=embed_fn)

# --- 2. THE DATA (Simulated Policy Document) ---
# In a real app, you would read this from a PDF.
documents = [
    "POLICY-101: Unsecured Personal Loans. Max limit is $50,000. Min credit score 680. Interest rate 12%.",
    "POLICY-102: Small Business Loans. Requires 2 years of tax returns. Max limit $500,000. Excludes crypto businesses.",
    "POLICY-103: KYC Updates 2025. All passports must be valid for at least 6 months beyond application date.",
    "POLICY-104: Remote Work Security. Employees must use VPN 'NexusSecure'. Personal devices are strictly prohibited."
]

ids = ["doc1", "doc2", "doc3", "doc4"]
metadatas = [{"source": "Lending_Manual"}, {"source": "Lending_Manual"}, {"source": "Compliance_Guide"}, {"source": "HR_Handbook"}]

# --- 3. STORE IT ---
print("--- 📚 INGESTING DOCUMENTS INTO VECTOR DB ---")
collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
print(f"✅ Successfully stored {len(documents)} policy chunks in 'bank_memory'.")