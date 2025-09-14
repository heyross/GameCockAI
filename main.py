import sys
import os
import subprocess
from ui import gamecock_ascii, gamecat_ascii
from data_sources import cftc, sec
from company_manager import get_company_map, find_company
from company_data import TARGET_COMPANIES, save_target_companies
from rag import query_swapbot
from processor import (process_zip_files, process_sec_insider_data, process_form13f_data, 
                      process_exchange_metrics_data, process_ncen_data, process_nport_data)
from processor_8k import process_8k_filings
from config import (
    CFTC_CREDIT_SOURCE_DIR, CFTC_RATES_SOURCE_DIR, CFTC_EQUITY_SOURCE_DIR, 
    CFTC_COMMODITIES_SOURCE_DIR, CFTC_FOREX_SOURCE_DIR, INSIDER_SOURCE_DIR, THRTNF_SOURCE_DIR,
    EXCHANGE_SOURCE_DIR, SEC_8K_SOURCE_DIR, NCEN_SOURCE_DIR, NPORT_SOURCE_DIR
)
from database import create_db_and_tables, get_db_stats, export_db_to_csv, reset_database
from startup import check_dependencies, check_ollama_service
from worker import start_worker, stop_worker

def main_menu():
    gamecock_ascii()
    while True:
        print("\n--- Main Menu ---")
        print("1. Select Target Companies")
        print("2. Download Data")
        print("3. Process Downloaded Data")
        print("4. Query with SwapBot")
        print("5. Database Menu")
        print("Q. Quit")

        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            select_target_companies_menu()
        elif choice == '2':
            download_data_menu()
        elif choice == '3':
            process_data_menu()
        elif choice == '4':
            query_swapbot_menu()
        elif choice == '5':
            database_menu()
        elif choice == 'q':
            print("Stopping background worker and exiting...")
            stop_worker()
            sys.exit()
        else:
            print("Invalid choice. Please try again.")

def select_target_companies_menu():
    print("\n--- Select Target Companies ---")
    company_map = get_company_map()
    if company_map is None:
        print("Could not retrieve company data. Please check your internet connection.")
        return

    while True:
        print("\n1. Search for a company")
        print("2. View target companies")
        print("3. Clear target companies")
        print("B. Back to Main Menu")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            search_term = input("Enter company name or ticker: ").strip()
            if not search_term:
                continue
            
            results = find_company(company_map, search_term)
            if not results:
                print("No companies found.")
                continue

            print("\nSearch Results:")
            for i, company in enumerate(results):
                print(f"{i+1}. {company['title']} ({company['ticker']}) - CIK: {company['cik_str']}")
            
            try:
                selection = int(input("Select a company to add to targets (or 0 to cancel): ").strip())-1
                if 0 <= selection < len(results):
                    selected_company = results[selection]
                    if any(c['cik_str'] == selected_company['cik_str'] for c in TARGET_COMPANIES):
                        print(f"{selected_company['title']} is already in the target list.")
                    else:
                        TARGET_COMPANIES.append(selected_company)
                        save_target_companies(TARGET_COMPANIES)
                        print(f"Added {selected_company['title']} to target list.")
            except ValueError:
                print("Invalid selection.")

        elif choice == '2':
            if not TARGET_COMPANIES:
                print("\nTarget list is empty.")
            else:
                print("\n--- Target Companies ---")
                for company in TARGET_COMPANIES:
                    print(f"- {company['title']} ({company['ticker']}) - CIK: {company['cik_str']}")

        elif choice == '3':
            if not TARGET_COMPANIES:
                print("\nTarget list is already empty.")
            else:
                confirm = input(f"Are you sure you want to clear all {len(TARGET_COMPANIES)} target companies? (y/n): ").strip().lower()
                if confirm == 'y':
                    TARGET_COMPANIES.clear()
                    save_target_companies(TARGET_COMPANIES)
                    print("Target companies list cleared.")
                else:
                    print("Clear operation cancelled.")

        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def download_data_menu():
    while True:
        print("\n--- Download Data Menu ---")
        print("1. Download CFTC Data")
        print("2. Download SEC Data")
        print("B. Back to Main Menu")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            cftc_download_submenu()
        elif choice == '2':
            sec_download_submenu()
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def cftc_download_submenu():
    while True:
        print("\n--- CFTC Download Menu ---")
        print("1. Credit")
        print("2. Commodities")
        print("3. Rates")
        print("4. Equity")
        print("5. Forex")
        print("A. All CFTC Data")
        print("B. Back")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            cftc.download_cftc_credit_archives()
        elif choice == '2':
            cftc.download_cftc_commodities_archives()
        elif choice == '3':
            cftc.download_cftc_rates_archives()
        elif choice == '4':
            cftc.download_cftc_equities_archives()
        elif choice == '5':
            cftc.download_cftc_forex_archives()
        elif choice == 'a':
            print("Downloading all CFTC data...")
            cftc.download_cftc_credit_archives()
            cftc.download_cftc_commodities_archives()
            cftc.download_cftc_rates_archives()
            cftc.download_cftc_equities_archives()
            cftc.download_cftc_forex_archives()
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def sec_download_submenu():
    while True:
        print("\n--- SEC Download Menu ---")
        print("1. Insider Transactions")
        print("2. Exchange Metrics")
        print("3. EDGAR Filings")
        print("4. 13F Holdings")
        print("5. N-MFP Filings")
        print("6. Form D Filings")
        print("7. N-CEN Filings")
        print("8. N-PORT Filings")
        print("A. All SEC Data")
        print("B. Back")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            sec.download_insider_archives()
        elif choice == '2':
            sec.download_exchange_archives()
        elif choice == '3':
            sec.allyourbasearebelongtous()
        elif choice == '4':
            sec.download_13F_archives()
        elif choice == '5':
            sec.download_nmfp_archives()
        elif choice == '6':
            sec.download_formd_archives()
        elif choice == '7':
            sec.download_ncen_archives()
        elif choice == '8':
            sec.download_nport_archives()
        elif choice == 'a':
            print("Downloading all SEC data...")
            sec.download_insider_archives()
            sec.download_exchange_archives()
            sec.allyourbasearebelongtous()
            sec.download_13F_archives()
            sec.download_nmfp_archives()
            sec.download_formd_archives()
            sec.download_ncen_archives()
            sec.download_nport_archives()
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def process_data_menu():
    gamecat_ascii()
    if not TARGET_COMPANIES:
        print("\nWarning: No target companies selected. Processing may be slow and include all data.")
        print("It is recommended to select target companies first from the main menu.")

    while True:
        print("\n--- Process and Load Data Menu ---")
        print("1. Process CFTC Data")
        print("2. Process SEC Data")
        print("B. Back to Main Menu")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            process_cftc_submenu()
        elif choice == '2':
            process_sec_submenu()
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def process_cftc_submenu():
    while True:
        print("\n--- Process CFTC Data ---")
        print("1. Credit")
        print("2. Commodities")
        print("3. Rates")
        print("4. Equity")
        print("5. Forex")
        print("A. All CFTC Data")
        print("B. Back")
        choice = input("Enter your choice: ").strip().lower()

        source_dirs = []
        if choice == '1':
            source_dirs.append(CFTC_CREDIT_SOURCE_DIR)
        elif choice == '2':
            source_dirs.append(CFTC_COMMODITIES_SOURCE_DIR)
        elif choice == '3':
            source_dirs.append(CFTC_RATES_SOURCE_DIR)
        elif choice == '4':
            source_dirs.append(CFTC_EQUITY_SOURCE_DIR)
        elif choice == '5':
            source_dirs.append(CFTC_FOREX_SOURCE_DIR)
        elif choice == 'a':
            print("Processing all CFTC data...")
            source_dirs.extend([
                CFTC_CREDIT_SOURCE_DIR, CFTC_COMMODITIES_SOURCE_DIR, 
                CFTC_RATES_SOURCE_DIR, CFTC_EQUITY_SOURCE_DIR, CFTC_FOREX_SOURCE_DIR
            ])
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")
            continue

        for source_dir in source_dirs:
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(source_dir))}...")
            process_zip_files(source_dir, TARGET_COMPANIES)

def process_sec_submenu():
    while True:
        print("\n--- Process SEC Data ---")
        print("1. Insider Transactions")
        print("2. 13F Holdings")
        print("3. Exchange Metrics")
        print("4. 8-K Filings")
        print("5. N-CEN Filings")
        print("6. N-PORT Filings")
        print("B. Back")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(INSIDER_SOURCE_DIR))}...")
            process_sec_insider_data(INSIDER_SOURCE_DIR)
            print("Processing complete.")
        elif choice == '2':
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(THRTNF_SOURCE_DIR))}...")
            process_form13f_data(THRTNF_SOURCE_DIR)
            print("Processing complete.")
        elif choice == '3':
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(EXCHANGE_SOURCE_DIR))}...")
            process_exchange_metrics_data(EXCHANGE_SOURCE_DIR)
            print("Processing complete.")
        elif choice == '4':
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(SEC_8K_SOURCE_DIR))}...")
            process_8k_filings(SEC_8K_SOURCE_DIR)
            print("Processing complete.")
        elif choice == '5':
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(NCEN_SOURCE_DIR))}...")
            process_ncen_data(NCEN_SOURCE_DIR)
            print("Processing complete.")
        elif choice == '6':
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(NPORT_SOURCE_DIR))}...")
            process_nport_data(NPORT_SOURCE_DIR)
            print("Processing complete.")
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def query_swapbot_menu():
    print("\n--- Chat with SwapBot ---")
    print("SwapBot is now in agent mode. You can ask it to perform actions.")
    print("Type 'back' to return to the main menu.")

    # Initialize the conversation history with a system prompt
    messages = [{
        'role': 'system',
        'content': 'You are SwapBot, an expert financial data assistant. Your goal is to help users by answering questions and performing tasks. When a user\'s request is ambiguous, ask clarifying questions to understand their intent before using your tools. Be conversational and guide the user if they seem unsure. You can use tools to find companies, manage watchlists, download data, and check on background tasks.'

    }]

    while True:
        user_query = input("\nYou: ").strip()
        if user_query.lower() == 'back':
            break
        if not user_query:
            continue

        response = query_swapbot(user_query, messages)
        print(f"\nSwapBot: {response}")

def database_menu():
    while True:
        print("\n--- Database Menu ---")
        print("1. View Database Statistics")
        print("2. Export Database to CSV")
        print("3. Reset Database")
        print("B. Back to Main Menu")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            stats = get_db_stats()
            print("\nDatabase Statistics:")
            for table, count in stats.items():
                print(f"- {table}: {count} records")
        elif choice == '2':
            output_path = input("Enter output path for CSV (e.g., export.csv): ").strip()
            if output_path:
                export_db_to_csv(output_path)
        elif choice == '3':
            confirm = input("Are you sure you want to reset the database? This will delete all data. (y/n): ").strip().lower()
            if confirm == 'y':
                reset_database()
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")




def run_startup_checks():
    """Performs all startup checks and handles missing dependencies."""
    missing = check_dependencies()
    if missing:
        print("\nThe following required packages are missing:")
        for pkg in missing:
            print(f"- {pkg}")
        
        print("\nAttempting to install missing packages...")
        try:
            install_command = [sys.executable, '-m', 'pip', 'install'] + missing
            # Run the installation command, showing output to the user
            subprocess.run(install_command, check=True)
            print("Dependencies installed successfully. Please wait for the application to restart.")
            # Exit with a special code to signal the launcher to restart
            sys.exit(10)
        except subprocess.CalledProcessError as e:
            print("\nError installing dependencies:")
            print(e.stderr)
            print("Please try running the following command manually:")
            print(f"    pip install {' '.join(missing)}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    check_ollama_service()

def initialize_database():
    """Initialize database tables if they don't exist."""
    try:
        from database import create_db_and_tables
        success = create_db_and_tables()
        if success:
            print("Database tables verified/created successfully.")
        else:
            print("Warning: Database table initialization failed.")
    except Exception as e:
        print(f"Warning: Could not initialize database tables: {e}")

if __name__ == "__main__":
    run_startup_checks()
    initialize_database()
    start_worker()
    main_menu()
