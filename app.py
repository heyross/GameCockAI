import sys
import os
import subprocess
from typing import List, Tuple
from pathlib import Path
from datetime import datetime

# Add current directory to path to ensure we import from the right modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add parent directory to path for unified RAG
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from ui import gamecock_ascii, gamecat_ascii
try:
    from src.data_sources import cftc, sec, fred
    print("✅ Data sources imported successfully")
except ImportError as e:
    print(f"⚠️ Data sources not available: {e}")
    # Create dummy modules to prevent crashes
    class DummyModule:
        def __getattr__(self, name):
            def dummy_function(*args, **kwargs):
                print(f"Function {name} not available - data sources import failed")
                return None
            return dummy_function
    
    cftc = sec = fred = DummyModule()
from company_manager import get_company_map, find_company
from company_data import TARGET_COMPANIES, save_target_companies

try:
    from src.rag_unified import query_raven
    print("✅ Using unified RAG system")
except ImportError as e:
    print(f"⚠️ Unified RAG not available: {e}")
    try:
        from rag import query_raven
        print("✅ Using basic RAG system")
    except ImportError as e2:
        print(f"⚠️ Basic RAG not available: {e2}")
        # Fallback function
        def query_raven(user_query: str, messages: list = None):
            return "RAG system not available. Please check your installation."

from src.processor import (process_zip_files, process_sec_insider_data, process_form13f_data, 
                      process_exchange_metrics_data, process_ncen_data, process_nport_data, process_formd_data)
from src.processor_8k import process_8k_filings
from config import (
    CFTC_CREDIT_SOURCE_DIR, CFTC_RATES_SOURCE_DIR, CFTC_EQUITY_SOURCE_DIR, 
    CFTC_COMMODITIES_SOURCE_DIR, CFTC_FOREX_SOURCE_DIR, INSIDER_SOURCE_DIR, THRTNF_SOURCE_DIR,
    EXCHANGE_SOURCE_DIR, SEC_8K_SOURCE_DIR, NCEN_SOURCE_DIR, NPORT_SOURCE_DIR, FORMD_SOURCE_DIR
)
# Import from the correct database module (GameCockAI/database.py)
try:
    from .database import create_db_and_tables, get_db_stats, export_db_to_csv, reset_database
except ImportError:
    # Fallback for when running from GameCockAI directory
    from database import create_db_and_tables, get_db_stats, export_db_to_csv, reset_database
from startup import check_dependencies, check_ollama_service, check_cuda_support
from worker import start_worker, stop_worker

def main_menu():
    # Clear screen before showing the main menu
    import subprocess
    subprocess.run(['powershell', '-Command', 'Clear-Host'], capture_output=True)
    gamecock_ascii()
    while True:
        print("\n--- Main Menu ---")
        print("1. Select Target Companies")
        print("2. Download Data")
        print("3. Process Downloaded Data")
        print("4. Query with Raven")
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
            query_raven_menu()
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
        print("3. Download FRED Swap Data")
        # Temporarily hiding DTCC Data until authentication is set up
        # print("4. Download DTCC Data")  # Requires API authentication
        print("\nB. Back to Main Menu")
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            cftc_download_submenu()
        elif choice == '2':
            sec_download_submenu()
        elif choice == '3':
            fred_download_menu()
        # Temporarily hiding DTCC Data until authentication is set up
        # elif choice == '4':
        #     dtcc_download_submenu()
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def fred_download_menu():
    """Menu for downloading FRED swap rate data."""
    from src.data_sources.fred import download_fred_swap_data
    import os
    
    print("\n--- FRED Swap Data Download ---")
    print("This will download swap rate data from the Federal Reserve Economic Data (FRED).")
    print("A FRED API key is required (get one at https://fred.stlouisfed.org/docs/api/api_key.html)")
    
    # Check if API key is set
    if not os.getenv('FRED_API_KEY'):
        print("\n⚠️  FRED_API_KEY not found in environment variables.")
        print("Please add it to your .env file or set it as an environment variable.")
        print("Example: FRED_API_KEY=your_api_key_here")
        input("\nPress Enter to return to the menu...")
        return
    
    try:
        print("\nDownloading swap rate data from FRED...")
        saved_files = download_fred_swap_data()
        
        if saved_files:
            print("\n✅ Successfully downloaded the following swap rate data:")
            for series_id, filepath in saved_files.items():
                print(f"- {series_id}: {filepath}")
            
            print("\nYou can now process this data using the 'Process Data' menu.")
        else:
            print("\n⚠️  No swap rate data was downloaded.")
            print("Please check your FRED API key and internet connection.")
            
    except Exception as e:
        print(f"\n❌ Error downloading FRED data: {e}")
        print("Please check your FRED API key and try again.")
    
    input("\nPress Enter to continue...")

def edgar_download_menu():
    """Menu for downloading EDGAR filings (8-K, 10-K, S-4, etc.)"""
    from src.data_sources.sec import download_edgar_filings
    
    print("\n--- EDGAR Filings Download ---")
    print("This will download SEC filings (8-K, 10-K, S-4, etc.) for your target companies.")
    
    if not TARGET_COMPANIES:
        print("\n⚠️  No target companies selected.")
        print("Please add companies to your target list first from the main menu.")
        input("\nPress Enter to return to the menu...")
        return
    
    print(f"\nTarget companies: {len(TARGET_COMPANIES)}")
    for company in TARGET_COMPANIES:
        print(f"  - {company.get('title', 'Unknown')} (CIK: {company.get('cik_str', 'N/A')})")
    
    # Filing type selection
    print("\nSelect filing types to download:")
    print("1. 8-K (Current Reports)")
    print("2. 10-K (Annual Reports)")
    print("3. 10-Q (Quarterly Reports)")
    print("4. S-4 (Registration Statements)")
    print("5. DEF 14A (Proxy Statements)")
    print("6. All of the above")
    print("7. Custom selection")
    
    filing_choice = input("\nEnter your choice (1-7): ").strip()
    
    filing_types = []
    if filing_choice == '1':
        filing_types = ['8-K']
    elif filing_choice == '2':
        filing_types = ['10-K']
    elif filing_choice == '3':
        filing_types = ['10-Q']
    elif filing_choice == '4':
        filing_types = ['S-4']
    elif filing_choice == '5':
        filing_types = ['DEF 14A']
    elif filing_choice == '6':
        filing_types = ['8-K', '10-K', '10-Q', 'S-4', 'DEF 14A']
    elif filing_choice == '7':
        print("\nEnter filing types separated by commas (e.g., 8-K,10-K,S-4):")
        custom_types = input("Filing types: ").strip()
        filing_types = [t.strip() for t in custom_types.split(',') if t.strip()]
    else:
        print("Invalid choice. Using default filing types.")
        filing_types = ['8-K', '10-K']
    
    # Year selection
    current_year = datetime.now().year
    print(f"\nSelect years to download (current year: {current_year}):")
    print("1. Last 2 years")
    print("2. Last 3 years")
    print("3. Custom years")
    
    year_choice = input("Enter your choice (1-3): ").strip()
    
    if year_choice == '1':
        years = [current_year - 1, current_year]
    elif year_choice == '2':
        years = [current_year - 2, current_year - 1, current_year]
    elif year_choice == '3':
        print(f"\nEnter years separated by commas (e.g., 2022,2023,{current_year}):")
        custom_years = input("Years: ").strip()
        try:
            years = [int(y.strip()) for y in custom_years.split(',') if y.strip()]
        except ValueError:
            print("Invalid years. Using last 2 years.")
            years = [current_year - 1, current_year]
    else:
        print("Invalid choice. Using last 2 years.")
        years = [current_year - 1, current_year]
    
    # Max files per company
    print(f"\nMaximum files per company (default: 50):")
    max_files_input = input("Max files: ").strip()
    try:
        max_files = int(max_files_input) if max_files_input else 50
    except ValueError:
        max_files = 50
    
    # Confirmation
    print(f"\n--- Download Summary ---")
    print(f"Companies: {len(TARGET_COMPANIES)}")
    print(f"Filing types: {', '.join(filing_types)}")
    print(f"Years: {', '.join(map(str, years))}")
    print(f"Max files per company: {max_files}")
    
    confirm = input("\nProceed with download? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Download cancelled.")
        input("\nPress Enter to continue...")
        return
    
    try:
        print("\nStarting EDGAR download...")
        download_edgar_filings(
            target_companies=TARGET_COMPANIES,
            filing_types=filing_types,
            years=years,
            max_files_per_company=max_files
        )
        print("\n✅ EDGAR download completed!")
        
    except Exception as e:
        print(f"\n❌ Error during EDGAR download: {e}")
        print("Please check your internet connection and try again.")
    
    input("\nPress Enter to continue...")

def download_all_edgar_filings():
    """Automatically download all EDGAR filings for target companies without user interaction."""
    from src.data_sources.sec import download_edgar_filings
    
    if not TARGET_COMPANIES:
        print("\n⚠️  No target companies selected. Skipping EDGAR downloads.")
        return
    
    print(f"\n--- Downloading All EDGAR Filings ---")
    print(f"Target companies: {len(TARGET_COMPANIES)}")
    
    # Default settings for comprehensive download
    filing_types = ['8-K', '10-K', '10-Q', 'S-4', 'DEF 14A']
    current_year = datetime.now().year
    years = [current_year - 2, current_year - 1, current_year]  # Last 3 years
    max_files_per_company = 100  # Higher limit for comprehensive download
    
    print(f"Filing types: {', '.join(filing_types)}")
    print(f"Years: {', '.join(map(str, years))}")
    print(f"Max files per company: {max_files_per_company}")
    
    try:
        print("\nStarting comprehensive EDGAR download...")
        download_edgar_filings(
            target_companies=TARGET_COMPANIES,
            filing_types=filing_types,
            years=years,
            max_files_per_company=max_files_per_company
        )
        print("\n✅ Comprehensive EDGAR download completed!")
        
    except Exception as e:
        print(f"\n❌ Error during EDGAR download: {e}")
        print("Please check your internet connection and try again.")

def cftc_download_submenu():
    while True:
        print("\n--- CFTC Download Menu ---")
        print("1. Credit")
        print("2. Commodities")
        print("3. Rates")
        print("4. Equity")
        print("5. Forex")
        print("6. Swaps (Dealers & Repositories)")
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
        elif choice == '6':
            print("\n--- CFTC Swaps Menu ---")
            print("1. Swap Dealers")
            print("2. Swap Execution Facilities")
            print("3. Swap Data Repositories")
            print("A. All Swap Data")
            print("B. Back to CFTC Menu")
            
            swap_choice = input("Enter your choice: ").strip().lower()
            
            if swap_choice == '1':
                cftc.download_swap_dealer_data()
            elif swap_choice == '2':
                cftc.download_swap_execution_facility_data()
            elif swap_choice == '3':
                cftc.download_swap_data_repository_data()
            elif swap_choice == 'a':
                cftc.download_all_swap_data()
            elif swap_choice != 'b':
                print("Invalid choice.")
                
        elif choice == 'a':
            print("Downloading all CFTC data...")
            cftc.download_cftc_credit_archives()
            cftc.download_cftc_commodities_archives()
            cftc.download_cftc_rates_archives()
            cftc.download_cftc_equities_archives()
            cftc.download_cftc_forex_archives()
            cftc.download_all_swap_data()
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
            edgar_download_menu()
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
            download_all_edgar_filings()
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
        print("7. Form D Filings")
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
        elif choice == '7':
            print(f"\nProcessing files in {os.path.basename(os.path.normpath(FORMD_SOURCE_DIR))}...")
            process_formd_data(FORMD_SOURCE_DIR)
            print("Processing complete.")
        elif choice == 'b':
            break
        else:
            print("Invalid choice.")

def query_raven_menu():
    """Launch the interactive chat interface."""
    from chat_interface import main as chat_main
    chat_main()

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
    print("\n🚀 Welcome to GameCock AI - Your Financial Data Intelligence Platform")
    print("=" * 70)
    print("🔧 Initializing system components...")
    
    # Check and install dependencies
    if not check_dependencies():
        print("❌ Failed to install required dependencies.")
        print("Please install missing packages manually and restart the application.")
        sys.exit(1)
    
    # Check the Ollama service after dependencies are confirmed
    check_ollama_service()
    
    print("\n✅ All systems operational! GameCock AI is ready to assist you.")
    print("=" * 70)

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

def download_dtcc_data(data_type):
    """Download DTCC data of the specified type"""
    from src.data_sources.dtcc import download_dtcc_swap_data
    from datetime import datetime, timedelta
    import os
    import sys
    
    try:
        print("\n--- DTCC Data Download Notice ---")
        print("The DTCC public API is currently unavailable (Error 503).")
        print("\nTo use DTCC data, you need to:")
        print("1. Download the data manually from DTCC's website")
        print("2. Place the files in the appropriate directory:")
        print(f"   - For Interest Rate Swaps: data/dtcc/irs/")
        print(f"   - For Credit Default Swaps: data/dtcc/cds/")
        print(f"   - For Equity Options: data/dtcc/equity_derivatives/")
        print("\nAfter placing the files, you can process them using the 'Process DTCC Data' option.")
        
        # Create the directory structure for manual file placement
        base_dir = os.path.join('data', 'dtcc')
        os.makedirs(os.path.join(base_dir, 'irs'), exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'cds'), exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'equity_derivatives'), exist_ok=True)
        
        print(f"\nDirectories created at: {os.path.abspath(base_dir)}")
        
    except Exception as e:
        print(f"\nError setting up DTCC data directories: {str(e)}")
        logger.error(f"Error setting up DTCC data directories: {str(e)}", exc_info=True)
    
    input("\nPress Enter to continue...")

def process_dtcc_data():
    """Process DTCC data files from a directory"""
    from src.processor_dtcc import DTCCProcessor
    from database import SessionLocal
    
    print("\n--- Process DTCC Data ---")
    print("This will process DTCC data files from the configured directory.")
    
    # Get source directory from user
    source_dir = input("Enter the path to the directory containing DTCC files (or press Enter for default): ").strip()
    if not source_dir:
        print("Please specify a source directory.")
        return
    
    if not os.path.isdir(source_dir):
        print(f"Error: Directory not found: {source_dir}")
        return
    
    # Get file type
    print("\nSelect file type:")
    print("1. Option Trades")
    print("2. Interest Rate Swaps")
    print("3. Credit Default Swaps")
    file_type_choice = input("Enter your choice (1-3): ").strip()
    
    file_types = {
        '1': 'OPTION_TRADE',
        '2': 'INTEREST_RATE_SWAP',
        '3': 'CREDIT_DEFAULT_SWAP'
    }
    
    file_type = file_types.get(file_type_choice)
    if not file_type:
        print("Invalid choice. Please try again.")
        return
    
    # Get source entity
    source_entity = input("Enter source entity (e.g., DTCC, BLOOMBERG): ").strip()
    if not source_entity:
        print("Source entity is required.")
        return
    
    # Process files
    db_session = SessionLocal()
    processor = DTCCProcessor(db_session)
    
    try:
        # Get all files in directory
        files = [f for f in os.listdir(source_dir) 
                if os.path.isfile(os.path.join(source_dir, f)) 
                and f.lower().endswith(('.csv', '.xls', '.xlsx'))]
        
        if not files:
            print(f"No CSV or Excel files found in {source_dir}")
            return
        
        print(f"\nFound {len(files)} files to process...")
        
        for i, filename in enumerate(files, 1):
            file_path = os.path.join(source_dir, filename)
            print(f"\nProcessing file {i} of {len(files)}: {filename}")
            
            try:
                result = processor.process_dtcc_file(
                    file_path=file_path,
                    file_type=file_type,
                    source_entity=source_entity
                )
                
                if result['status'] == 'completed':
                    print(f"  - Processed {result['records_processed']} records")
                    if result.get('errors'):
                        print(f"  - {len(result['errors'])} errors occurred")
                else:
                    print(f"  - Error: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  - Error processing {filename}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db_session.close()
    
    input("\nPress Enter to continue...")

def show_dtcc_statistics():
    """Display statistics about DTCC data in the database"""
    from sqlalchemy import func, and_
    from database import SessionLocal
    from dtcc_models import (
        DTCCOrganization, DTCCOptionTrade, DTCCInterestRateSwap,
        DTCCEquityOption, DTCCOptionExercise, DTCCOptionPosition, DTCCOptionSettlement
    )
    
    print("\n--- DTCC Database Statistics ---")
    
    db_session = SessionLocal()
    try:
        # Get organization statistics
        org_count = db_session.query(DTCCOrganization).count()
        print(f"\nOrganizations: {org_count}")
        
        # Option trades statistics
        opt_trade_count = db_session.query(DTCCOptionTrade).count()
        print(f"\nOption Trades: {opt_trade_count}")
        
        if opt_trade_count > 0:
            # Get trade counts by type
            trade_types = db_session.query(
                DTCCOptionTrade.option_type,
                func.count(DTCCOptionTrade.id)
            ).group_by(DTCCOptionTrade.option_type).all()
            
            print("\nOption Trades by Type:")
            for trade_type, count in trade_types:
                print(f"  - {trade_type or 'N/A'}: {count}")
            
            # Get most recent trade
            recent_trade = db_session.query(DTCCOptionTrade)\
                .order_by(DTCCOptionTrade.execution_timestamp.desc())\
                .first()
            
            if recent_trade:
                print(f"\nMost Recent Trade: {recent_trade.trade_id} on {recent_trade.execution_timestamp}")
        
        # Interest rate swaps statistics
        swap_count = db_session.query(DTCCInterestRateSwap).count()
        print(f"\nInterest Rate Swaps: {swap_count}")
        
        if swap_count > 0:
            # Get notional amounts summary
            stats = db_session.query(
                func.count(DTCCInterestRateSwap.id),
                func.sum(DTCCInterestRateSwap.notional_amount),
                func.avg(DTCCInterestRateSwap.notional_amount),
                func.min(DTCCInterestRateSwap.notional_amount),
                func.max(DTCCInterestRateSwap.notional_amount)
            ).first()
            
            if stats[1]:  # If we have notional amounts
                total_notional, avg_notional, min_notional, max_notional = stats[1:]
                print(f"Total Notional: ${total_notional:,.2f}")
                print(f"Average Notional: ${avg_notional:,.2f}")
                print(f"Min Notional: ${min_notional:,.2f}")
                print(f"Max Notional: ${max_notional:,.2f}")
            
            # Get most recent swap
            recent_swap = db_session.query(DTCCInterestRateSwap)\
                .order_by(DTCCInterestRateSwap.effective_date.desc())\
                .first()
            
            if recent_swap:
                print(f"\nMost Recent Swap: {recent_swap.trade_id} effective {recent_swap.effective_date}")
        
        # Equity options statistics
        equity_count = db_session.query(DTCCEquityOption).count()
        print(f"\nEquity Options: {equity_count}")
        
        # Option exercises
        exercise_count = db_session.query(DTCCOptionExercise).count()
        print(f"Option Exercises: {exercise_count}")
        
        # Option positions
        position_count = db_session.query(DTCCOptionPosition).count()
        print(f"Option Positions: {position_count}")
        
        # Option settlements
        settlement_count = db_session.query(DTCCOptionSettlement).count()
        print(f"Option Settlements: {settlement_count}")
        
    except Exception as e:
        print(f"\nError retrieving statistics: {str(e)}")
    finally:
        db_session.close()
    
    input("\nPress Enter to continue...")

def dtcc_download_submenu():
    """DTCC Data Operations Menu"""
    while True:
        print("\n--- DTCC Data Menu ---")
        print("1. Download Options")
        print("2. Process DTCC Data")
        print("3. View DTCC Statistics")
        print("B. Back to Download Menu")
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == '1':
            print("\n--- Download DTCC Data ---")
            print("1. Download All DTCC Data")
            print("2. Download Interest Rate Swaps")
            print("3. Download Equity Options")
            print("4. Download Credit Default Swaps")
            print("B. Back to DTCC Menu")
            
            sub_choice = input("\nEnter your choice: ").strip().lower()
            
            if sub_choice == '1':
                print("\nDownloading all DTCC data...")
                download_dtcc_data('all')
            elif sub_choice == '2':
                print("\nDownloading Interest Rate Swaps data...")
                download_dtcc_data('irs')
            elif sub_choice == '3':
                print("\nDownloading Equity Options data...")
                download_dtcc_data('equity_derivatives')
            elif sub_choice == '4':
                print("\nDownloading Credit Default Swaps data...")
                download_dtcc_data('cds')
            elif sub_choice != 'b':
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
                    
        elif choice == '2':
            process_dtcc_data()
            
        elif choice == '3':
            show_dtcc_statistics()
            
        elif choice == 'b':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    run_startup_checks()
    initialize_database()
    start_worker()
    main_menu()
