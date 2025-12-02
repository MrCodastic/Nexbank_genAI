import sys
import time
# Import our modules
import setup_database
import run_smart_collect
import run_kyc_extraction
import run_regpulse

def clear_screen():
    print("\033[H\033[J", end="")

def print_header():
    clear_screen()
    print("=====================================================")
    print("      🏦  NEXUS BANK GEN-AI SUITE (v1.0)  🏦      ")
    print("=====================================================")
    print("Powered by: TinyLlama (Local) | Vector DB: Chroma")
    print("=====================================================\n")

def main_menu():
    while True:
        print_header()
        print("Select a GenAI Use Case to Demo:")
        print("1. [SmartCollect]   Empathy-driven Debt Collections")
        print("2. [KYC-X]          ID Extraction & Fraud Check")
        print("3. [RegPulse]       Policy Research Assistant (RAG)")
        print("4. [Setup]          Reset Database & Memory")
        print("Q. Quit")
        
        choice = input("\nEnter Choice (1-4/Q): ").upper()
        
        if choice == "1":
            print("\n🚀 Launching SmartCollect Simulation...")
            time.sleep(1)
            # Check DB
            try:
                run_smart_collect.run_interaction()
            except Exception as e:
                print(f"Error: {e}")
                print("Try running Option 4 (Setup) first.")
            input("\n[Press Enter to return to menu]")

        elif choice == "2":
            print("\n🚀 Launching KYC-X Extraction...")
            time.sleep(1)
            # Run the extraction demo from the module
            messy_scan = """
            PASSPORT STATE
            Name: SARAH J. CONNOR
            DOB: 12 May 1984
            ID: 881209X
            Exp: 14 Aug 2024
            """
            data, duration = run_kyc_extraction.extract_and_validate(messy_scan)
            print(f"\nTime Taken: {round(duration, 2)}s")
            print(f"Result: {data}")
            input("\n[Press Enter to return to menu]")

        elif choice == "3":
            print("\n🚀 Launching RegPulse (Policy Search)...")
            question = input("Enter a policy question (e.g., 'What is the max personal loan?'): ")
            if not question: question = "What is the max personal loan?"
            
            answer, source = run_regpulse.consult_policy(question)
            print(f"\n🤖 AI Answer: {answer}")
            print(f"✅ Source: {source}")
            input("\n[Press Enter to return to menu]")

        elif choice == "4":
            print("\n⚙️  Resetting System...")
            setup_database.init_db()
            # Re-ingest documents logic could go here too
            print("Database reset complete.")
            time.sleep(1)

        elif choice == "Q":
            print("Exiting NexusBank Suite. Goodbye!")
            sys.exit()

if __name__ == "__main__":
    # Ensure DB exists
    setup_database.init_db()
    main_menu()