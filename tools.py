import json
import sys
import os

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Add GameCockAI directory to path for config imports
gamecock_dir = current_dir
if gamecock_dir not in sys.path:
    sys.path.insert(0, gamecock_dir)

from company_manager import get_company_map, find_company
from company_data import TARGET_COMPANIES, save_target_companies
from data_sources import cftc, sec
from processor import process_zip_files, load_cftc_data_to_db
# Import from the correct database module (GameCockAI/database.py)
try:
    from .database import get_db_stats, export_db_to_csv
except ImportError:
    # Fallback for when running from GameCockAI directory
    from database import get_db_stats, export_db_to_csv
from config import (
    CFTC_CREDIT_SOURCE_DIR, CFTC_RATES_SOURCE_DIR, CFTC_EQUITY_SOURCE_DIR,
    CFTC_COMMODITIES_SOURCE_DIR, CFTC_FOREX_SOURCE_DIR
)
try:
    from worker import add_task, get_task_status as get_task_status_from_worker
    WORKER_AVAILABLE = True
except ImportError:
    print("⚠️ Worker functions not available")
    def add_task(func, *args, **kwargs):
        return "worker-disabled"
    def get_task_status_from_worker(task_id):
        return {"status": "disabled", "message": "Worker not available"}
    WORKER_AVAILABLE = False
from analytics_tools import ANALYTICS_TOOLS
from enhanced_analytics_tools import ENHANCED_ANALYTICS_TOOLS

def search_companies(company_name: str):
    """Searches for a company by name or ticker in the SEC's CIK lookup data.

    Args:
        company_name (str): The name or ticker of the company to search for.

    Returns:
        str: A JSON string representing a list of matching companies.
    """
    print(f"[Tool] Searching for company: {company_name}")
    company_map = get_company_map()
    if company_map is None:
        return json.dumps({"error": "Could not retrieve company data."})
    
    results = find_company(company_map, company_name)
    if not results:
        return json.dumps({"message": "No companies found."})
    
    return json.dumps(results)

def add_to_target_list(cik: str, ticker: str, title: str):
    """Adds a company to the user's target list.

    Args:
        cik (str): The CIK of the company to add.
        ticker (str): The ticker symbol of the company.
        title (str): The title (name) of the company.

    Returns:
        str: A JSON string confirming the action.
    """
    print(f"[Tool] Adding company to target list: {title} ({cik})")
    company_to_add = {
        'cik_str': str(cik).zfill(10),
        'ticker': ticker,
        'title': title
    }

    if any(c['cik_str'] == company_to_add['cik_str'] for c in TARGET_COMPANIES):
        return json.dumps({"message": f"{title} is already in the target list."})
    
    TARGET_COMPANIES.append(company_to_add)
    save_target_companies(TARGET_COMPANIES)
    return json.dumps({"message": f"Added {title} to target list."})

def view_target_list():
    """Displays the current list of target companies.

    Returns:
        str: A JSON string of the target companies.
    """
    print("[Tool] Viewing target list")
    if not TARGET_COMPANIES:
        return json.dumps({"message": "Target list is empty."})
    return json.dumps(TARGET_COMPANIES)

def download_data(source: str, data_type: str):
    """Adds a data download task to the background worker queue.

    Args:
        source (str): The data source, either 'cftc' or 'sec'.
        data_type (str): The type of data to download (e.g., 'credit', 'rates').

    Returns:
        str: A JSON string containing the task ID for the download job.
    """
    print(f"[Tool] Queuing download for {data_type} from {source.upper()}")
    source = source.lower()
    data_type = data_type.lower()

    download_func = None
    if source == 'cftc':
        download_funcs = {
            'credit': cftc.download_cftc_credit_archives,
            'commodities': cftc.download_cftc_commodities_archives,
            'rates': cftc.download_cftc_rates_archives,
            'equity': cftc.download_cftc_equities_archives,
            'forex': cftc.download_cftc_forex_archives
        }
        download_func = download_funcs.get(data_type)
    elif source == 'sec':
        download_funcs = {
            'insider_transactions': sec.download_insider_archives,
            'exchange_metrics': sec.download_exchange_archives,
            '13f_holdings': sec.download_13F_archives
        }
        download_func = download_funcs.get(data_type)

    if download_func:
        task_id = add_task(download_func)
        return json.dumps({"message": f"Task queued for downloading {data_type} data.", "task_id": task_id})
    else:
        return json.dumps({"error": f"Invalid source or data type: {source}/{data_type}"})

def _process_data_task(source_dir_name: str):
    """The actual logic for processing data, intended to be run by a worker."""
    source_map = {
        'credit': CFTC_CREDIT_SOURCE_DIR,
        'rates': CFTC_RATES_SOURCE_DIR,
        'equity': CFTC_EQUITY_SOURCE_DIR,
        'commodities': CFTC_COMMODITIES_SOURCE_DIR,
        'forex': CFTC_FOREX_SOURCE_DIR
    }
    source_dir = source_map.get(source_dir_name.lower())
    if not source_dir:
        raise ValueError(f"Invalid source directory name: {source_dir_name}")

    df = process_zip_files(source_dir, TARGET_COMPANIES)
    if not df.empty:
        load_cftc_data_to_db(df)
        return f"Processing for {source_dir_name} complete. Records loaded."
    else:
        return f"No data found for selected companies in {source_dir_name}."

def process_data(source_dir_name: str):
    """Adds a data processing task to the background worker queue.

    Args:
        source_dir_name (str): The name of the data category to process (e.g., 'credit').

    Returns:
        str: A JSON string containing the task ID for the processing job.
    """
    print(f"[Tool] Queuing processing for: {source_dir_name}")
    task_id = add_task(_process_data_task, source_dir_name)
    return json.dumps({"message": f"Task queued for processing {source_dir_name} data.", "task_id": task_id})

def get_database_statistics():
    """Retrieves statistics from the database, such as record counts per table.

    Returns:
        str: A JSON string with the database statistics.
    """
    print("[Tool] Getting database statistics")
    stats = get_db_stats()
    return json.dumps(stats)

def check_task_status(task_id: str):
    """Checks the status of a background task.

    Args:
        task_id (str): The ID of the task to check.

    Returns:
        str: A JSON string with the task's status and result if completed.
    """
    print(f"[Tool] Checking status for task: {task_id}")
    status = get_task_status_from_worker(task_id)
    return json.dumps(status)


# This dictionary maps tool names to their corresponding functions and schema.
# The schema is essential for the AI to understand how to use each tool.
TOOL_MAP = {
    "search_companies": {
        "function": search_companies,
        "schema": {
            "name": "search_companies",
            "description": "Searches for a company by name or ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "The name or ticker of the company."}
                },
                "required": ["company_name"]
            }
        }
    },
    "add_to_target_list": {
        "function": add_to_target_list,
        "schema": {
            "name": "add_to_target_list",
            "description": "Adds a specific company to the user's target list for focused data processing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cik": {"type": "string", "description": "The CIK of the company."},
                    "ticker": {"type": "string", "description": "The ticker symbol of the company."},
                    "title": {"type": "string", "description": "The name of the company."}
                },
                "required": ["cik", "ticker", "title"]
            }
        }
    },
    "view_target_list": {
        "function": view_target_list,
        "schema": {
            "name": "view_target_list",
            "description": "Shows the user's current list of target companies.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    "download_data": {
        "function": download_data,
        "schema": {
            "name": "download_data",
            "description": "Queues a background task to download a specific type of financial data. Returns a task ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "enum": ["cftc", "sec"], "description": "The data source."},
                    "data_type": {"type": "string", "description": "The type of data to download (e.g., 'credit', 'insider_transactions')."}
                },
                "required": ["source", "data_type"]
            }
        }
    },
    "process_data": {
        "function": process_data,
        "schema": {
            "name": "process_data",
            "description": "Queues a background task to process downloaded data. Returns a task ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_dir_name": {"type": "string", "description": "The name of the data category to process (e.g., 'credit')."}
                },
                "required": ["source_dir_name"]
            }
        }
    },
    "get_database_statistics": {
        "function": get_database_statistics,
        "schema": {
            "name": "get_database_statistics",
            "description": "Gets statistics about the database, like table record counts.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    "check_task_status": {
        "function": check_task_status,
        "schema": {
            "name": "check_task_status",
            "description": "Checks the status of a background task using its task ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The ID of the task to check."}
                },
                "required": ["task_id"]
            }
        }
    },
    # Import analytics tools
    **ANALYTICS_TOOLS,
    # Import enhanced cross-dataset analytics tools (fixed version)
    **ENHANCED_ANALYTICS_TOOLS
}
