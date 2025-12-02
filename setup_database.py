import sqlite3

def init_db():
    conn = sqlite3.connect("nexus_bank.db")
    cursor = conn.cursor()

    # 1. Create Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        segment TEXT,
        risk_score FLOAT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS collections_status (
        customer_id TEXT,
        days_past_due INTEGER,
        total_due REAL,
        last_sentiment TEXT,
        preferred_channel TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    )''')

    # 2. Insert "John Doe" (The Test Case)
    # We use UPSERT or REPLACE to avoid errors if you run this twice
    cursor.execute("INSERT OR REPLACE INTO customers VALUES ('CUST-8821', 'John Doe', 'Mass Affluent', 0.85)")
    cursor.execute("INSERT OR REPLACE INTO collections_status VALUES ('CUST-8821', 45, 4500.00, 'Anxious', 'WhatsApp')")

    conn.commit()
    conn.close()
    print("✅ Database 'nexus_bank.db' created and seeded successfully.")

if __name__ == "__main__":
    init_db()