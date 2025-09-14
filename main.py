import sys
import os
import subprocess
from typing import List, Tuple
from pathlib import Path
from ui import gamecock_ascii, gamecat_ascii
from data_sources import cftc, sec, fred
from company_manager import get_company_map, find_company
from company_data import TARGET_COMPANIES, save_target_companies
try:
    import sys
    import os
    # Add parent directory to path for unified RAG
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    
    from rag_unified import query_raven
    print("✅ Using unified RAG system")
except ImportError as e:
    print(f"⚠️ Unified RAG not available: {e}")
    from rag import query_raven
from processor import (process_zip_files, process_sec_insider_data, process_form13f_data, 
                      process_exchange_metrics_data, process_ncen_data, process_nport_data, process_formd_data)
from processor_8k import process_8k_filings
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
from startup import check_dependencies, check_ollama_service
from worker import start_worker, stop_worker

def main_menu():
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
    from data_sources.fred import download_fred_swap_data
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
    print("\n=== Checking Dependencies ===")
    
    # Core required packages - only check for existence, not versions
    required_packages = [
        'sentence_transformers',
        'sklearn',
        'numpy',
        'pandas',
        'requests',
        'bs4',
        'tqdm',
        'sqlalchemy',
        'ollama',
        'python_dotenv',
        'rich',
        'fredapi'
    ]
    
    # Map of import names to pip package names
    package_map = {
        'sklearn': 'scikit-learn',
        'bs4': 'beautifulsoup4',
        'python_dotenv': 'python-dotenv'
    }
    
    missing_packages = []
    import importlib
    
    # Check each required package
    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            # Use the mapped package name if it exists, otherwise use the import name
            pip_name = package_map.get(pkg, pkg)
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("\nThe following packages need to be installed:")
        for pkg in missing_packages:
            print(f"- {pkg}")
        
        print("\nAttempting to install missing packages...")
        
        try:
            import subprocess
            import sys
            
            # Install each package one by one to avoid issues with failed installations
            for pkg in missing_packages:
                print(f"\nInstalling {pkg}...")
                try:
                    # First try with the exact package name
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", pkg],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        # If that fails, try with --user flag
                        result = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "--user", "--upgrade", pkg],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully installed {pkg}")
                    else:
                        print(f"❌ Failed to install {pkg}")
                        print(f"Error: {result.stderr if result.stderr else 'Unknown error'}")
                        print(f"\nPlease try installing it manually with:")
                        print(f"    pip install --user --upgrade {pkg}")
                        input("\nPress Enter to continue...")
                        
                    # Add a small delay to ensure the environment is updated
                    import time
                    time.sleep(1)
                        
                except Exception as e:
                    print(f"❌ Error installing {pkg}: {str(e)}")
                    print(f"\nPlease try installing it manually with:")
                    print(f"    pip install --user --upgrade {pkg}")
                    input("\nPress Enter to continue...")
            
            # Verify all packages were installed by checking both pip list and import
            still_missing = []
            import subprocess
            
            # Get list of installed packages from pip
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=freeze"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                print("\n❌ Failed to check installed packages. Will try direct imports instead.")
                installed_packages = []
            else:
                installed_packages = [pkg.split('==')[0].lower() for pkg in result.stdout.split('\n') if pkg.strip()]
            
            # Check each package
            for pkg in missing_packages:
                pip_name = pkg.lower()
                import_name = next((k for k, v in package_map.items() if v.lower() == pip_name), pip_name)
                
                # First check if pip thinks it's installed
                pip_installed = pip_name in installed_packages if installed_packages else False
                
                # Then try to import it
                try:
                    importlib.invalidate_caches()
                    importlib.import_module(import_name)
                    import_success = True
                except ImportError:
                    import_success = False
                
                # If both checks fail, mark as missing
                if not (pip_installed or import_success):
                    still_missing.append(pkg)
            
            if still_missing:
                print("\n❌ The following packages could not be installed:")
                for pkg in still_missing:
                    print(f"  - {pkg}")
                print("\nPlease try installing them manually with:")
                for pkg in still_missing:
                    print(f"    pip install --upgrade {pkg}")
                input("\nPress Enter to exit...")
                sys.exit(1)
            else:
                print("\n✅ All packages installed successfully!")
                
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {str(e)}")
            print("\nPlease try installing the required packages manually:")
            for pkg in missing_packages:
                print(f"    pip install --upgrade {pkg}")
            input("\nPress Enter to exit...")
            sys.exit(1)
    else:
        print("✅ All dependencies are installed and up to date.")
    
    # Check Ollama service
    print("\n=== Checking Ollama Service ===")
    try:
        import ollama
        ollama.list()
        print("✅ Ollama service is running.")
    except Exception as e:
        print(f"\n❌ Error checking Ollama service: {e}")
        print("\nPlease ensure Ollama is installed and running.")
        print("You can download it from: https://ollama.ai/")
        print("After installation, run 'ollama serve' in a terminal.")
        input("\nPress Enter to exit...")
        sys.exit(1)

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
    from data_sources.dtcc import download_dtcc_swap_data
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
    from processor_dtcc import DTCCProcessor
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
