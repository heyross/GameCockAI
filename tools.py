import json
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# Set up logging for tool operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Add GameCockAI directory to path for config imports
gamecock_dir = current_dir
if gamecock_dir not in sys.path:
    sys.path.insert(0, gamecock_dir)

# Import with error handling and fallbacks
try:
    from company_manager import get_company_map, find_company
    COMPANY_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Company manager not available: {e}")
    COMPANY_MANAGER_AVAILABLE = False
    def get_company_map():
        return None
    def find_company(company_map, search_term):
        return []

try:
    from company_data import TARGET_COMPANIES, save_target_companies
    COMPANY_DATA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Company data not available: {e}")
    COMPANY_DATA_AVAILABLE = False
    TARGET_COMPANIES = []
    def save_target_companies(companies):
        pass

try:
    from data_sources import cftc, sec
    DATA_SOURCES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Data sources not available: {e}")
    DATA_SOURCES_AVAILABLE = False
    cftc = None
    sec = None

try:
    from processor import process_zip_files, load_cftc_data_to_db
    PROCESSOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Processor not available: {e}")
    PROCESSOR_AVAILABLE = False
    def process_zip_files(source_dir, target_companies):
        return None
    def load_cftc_data_to_db(df):
        pass

# Import from the correct database module (GameCockAI/database.py)
try:
    from .database import get_db_stats, export_db_to_csv
    DATABASE_AVAILABLE = True
except ImportError:
    try:
        # Fallback for when running from GameCockAI directory
        from database import get_db_stats, export_db_to_csv
        DATABASE_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"⚠️ Database not available: {e}")
        DATABASE_AVAILABLE = False
        def get_db_stats():
            return {"error": "Database not available"}
        def export_db_to_csv(path):
            return {"error": "Database not available"}

try:
    from config import (
        CFTC_CREDIT_SOURCE_DIR, CFTC_RATES_SOURCE_DIR, CFTC_EQUITY_SOURCE_DIR,
        CFTC_COMMODITIES_SOURCE_DIR, CFTC_FOREX_SOURCE_DIR
    )
    CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Config not available: {e}")
    CONFIG_AVAILABLE = False
    CFTC_CREDIT_SOURCE_DIR = None
    CFTC_RATES_SOURCE_DIR = None
    CFTC_EQUITY_SOURCE_DIR = None
    CFTC_COMMODITIES_SOURCE_DIR = None
    CFTC_FOREX_SOURCE_DIR = None

try:
    from worker import add_task, get_task_status as get_task_status_from_worker
    WORKER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Worker functions not available")
    WORKER_AVAILABLE = False
    def add_task(func, *args, **kwargs):
        return "worker-disabled"
    def get_task_status_from_worker(task_id):
        return {"status": "disabled", "message": "Worker not available"}

try:
    from analytics_tools import ANALYTICS_TOOLS
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Analytics tools not available: {e}")
    ANALYTICS_AVAILABLE = False
    ANALYTICS_TOOLS = {}

try:
    from enhanced_analytics_tools_fixed import ENHANCED_ANALYTICS_TOOLS_FIXED as ENHANCED_ANALYTICS_TOOLS
    ENHANCED_ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Enhanced analytics tools not available: {e}")
    ENHANCED_ANALYTICS_AVAILABLE = False
    ENHANCED_ANALYTICS_TOOLS = {}

# Error handling decorator for all tools
def handle_tool_errors(func):
    """Decorator to provide consistent error handling for all tools"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "tool": func.__name__,
                "suggestion": "Please check your data sources and try again"
            })
    return wrapper

@handle_tool_errors
def search_companies(company_name: str):
    """Searches for a company by name or ticker in the SEC's CIK lookup data.

    Args:
        company_name (str): The name or ticker of the company to search for.

    Returns:
        str: A JSON string representing a list of matching companies.
    """
    if not COMPANY_MANAGER_AVAILABLE:
        return json.dumps({
            "error": "Company search service not available",
            "suggestion": "Please check your internet connection and try again"
        })
    
    if not company_name or not company_name.strip():
        return json.dumps({
            "error": "Company name is required",
            "suggestion": "Please provide a company name or ticker symbol"
        })
    
    logger.info(f"[Tool] Searching for company: {company_name}")
    
    try:
        company_map = get_company_map()
        if company_map is None:
            return json.dumps({
                "error": "Could not retrieve company data",
                "suggestion": "Please check your internet connection and try again"
            })
        
        results = find_company(company_map, company_name.strip())
        if not results:
            return json.dumps({
                "message": "No companies found",
                "search_term": company_name,
                "suggestion": "Try a different spelling or ticker symbol"
            })
        
        return json.dumps({
            "results": results,
            "count": len(results),
            "search_term": company_name
        })
    except Exception as e:
        logger.error(f"Company search failed: {str(e)}")
        return json.dumps({
            "error": "Company search failed",
            "suggestion": "Please try again or contact support"
        })

@handle_tool_errors
def add_to_target_list(cik: str, ticker: str, title: str):
    """Adds a company to the user's target list.

    Args:
        cik (str): The CIK of the company to add.
        ticker (str): The ticker symbol of the company.
        title (str): The title (name) of the company.

    Returns:
        str: A JSON string confirming the action.
    """
    if not COMPANY_DATA_AVAILABLE:
        return json.dumps({
            "error": "Target list service not available",
            "suggestion": "Please check your installation and try again"
        })
    
    if not all([cik, ticker, title]):
        return json.dumps({
            "error": "All parameters (CIK, ticker, title) are required",
            "suggestion": "Please provide complete company information"
        })
    
    logger.info(f"[Tool] Adding company to target list: {title} ({cik})")
    
    try:
        company_to_add = {
            'cik_str': str(cik).zfill(10),
            'ticker': str(ticker).strip(),
            'title': str(title).strip()
        }

        if any(c['cik_str'] == company_to_add['cik_str'] for c in TARGET_COMPANIES):
            return json.dumps({
                "message": f"{title} is already in the target list",
                "company": company_to_add
            })
        
        TARGET_COMPANIES.append(company_to_add)
        save_target_companies(TARGET_COMPANIES)
        return json.dumps({
            "message": f"Added {title} to target list",
            "company": company_to_add,
            "total_targets": len(TARGET_COMPANIES)
        })
    except Exception as e:
        logger.error(f"Failed to add company to target list: {str(e)}")
        return json.dumps({
            "error": "Failed to add company to target list",
            "suggestion": "Please try again or contact support"
        })

@handle_tool_errors
def view_target_list():
    """Displays the current list of target companies.

    Returns:
        str: A JSON string of the target companies.
    """
    if not COMPANY_DATA_AVAILABLE:
        return json.dumps({
            "error": "Target list service not available",
            "suggestion": "Please check your installation and try again"
        })
    
    logger.info("[Tool] Viewing target list")
    
    try:
        if not TARGET_COMPANIES:
            return json.dumps({
                "message": "Target list is empty",
                "count": 0,
                "suggestion": "Use 'search_companies' to find companies and add them to your target list"
            })
        
        return json.dumps({
            "target_companies": TARGET_COMPANIES,
            "count": len(TARGET_COMPANIES),
            "message": f"Found {len(TARGET_COMPANIES)} target companies"
        })
    except Exception as e:
        logger.error(f"Failed to view target list: {str(e)}")
        return json.dumps({
            "error": "Failed to retrieve target list",
            "suggestion": "Please try again or contact support"
        })

@handle_tool_errors
def download_data(source: str, data_type: str):
    """Adds a data download task to the background worker queue.

    Args:
        source (str): The data source, either 'cftc' or 'sec'.
        data_type (str): The type of data to download (e.g., 'credit', 'rates').

    Returns:
        str: A JSON string containing the task ID for the download job.
    """
    if not DATA_SOURCES_AVAILABLE:
        return json.dumps({
            "error": "Data download service not available",
            "suggestion": "Please check your installation and try again"
        })
    
    if not WORKER_AVAILABLE:
        return json.dumps({
            "error": "Background worker not available",
            "suggestion": "Please restart the application to enable background tasks"
        })
    
    if not source or not data_type:
        return json.dumps({
            "error": "Both source and data_type are required",
            "suggestion": "Please specify the data source (cftc/sec) and data type"
        })
    
    logger.info(f"[Tool] Queuing download for {data_type} from {source.upper()}")
    
    try:
        source = source.lower().strip()
        data_type = data_type.lower().strip()

        download_func = None
        available_types = []
        
        if source == 'cftc' and cftc:
            download_funcs = {
                'credit': cftc.download_cftc_credit_archives,
                'commodities': cftc.download_cftc_commodities_archives,
                'rates': cftc.download_cftc_rates_archives,
                'equity': cftc.download_cftc_equities_archives,
                'forex': cftc.download_cftc_forex_archives
            }
            available_types = list(download_funcs.keys())
            download_func = download_funcs.get(data_type)
        elif source == 'sec' and sec:
            download_funcs = {
                'insider_transactions': sec.download_insider_archives,
                'exchange_metrics': sec.download_exchange_archives,
                '13f_holdings': sec.download_13F_archives
            }
            available_types = list(download_funcs.keys())
            download_func = download_funcs.get(data_type)
        else:
            return json.dumps({
                "error": f"Invalid or unavailable data source: {source}",
                "suggestion": "Use 'cftc' or 'sec' as the source",
                "available_sources": ["cftc", "sec"]
            })

        if download_func:
            task_id = add_task(download_func)
            return json.dumps({
                "message": f"Task queued for downloading {data_type} data from {source.upper()}",
                "task_id": task_id,
                "source": source,
                "data_type": data_type
            })
        else:
            return json.dumps({
                "error": f"Invalid data type '{data_type}' for source '{source}'",
                "suggestion": f"Use one of the available data types for {source.upper()}",
                "available_types": available_types
            })
    except Exception as e:
        logger.error(f"Failed to queue download task: {str(e)}")
        return json.dumps({
            "error": "Failed to queue download task",
            "suggestion": "Please try again or contact support"
        })

def _process_data_task(source_dir_name: str):
    """The actual logic for processing data, intended to be run by a worker."""
    if not CONFIG_AVAILABLE or not PROCESSOR_AVAILABLE:
        raise ValueError("Processing service not available")
    
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

@handle_tool_errors
def process_data(source_dir_name: str):
    """Adds a data processing task to the background worker queue.

    Args:
        source_dir_name (str): The name of the data category to process (e.g., 'credit').

    Returns:
        str: A JSON string containing the task ID for the processing job.
    """
    if not PROCESSOR_AVAILABLE:
        return json.dumps({
            "error": "Data processing service not available",
            "suggestion": "Please check your installation and try again"
        })
    
    if not CONFIG_AVAILABLE:
        return json.dumps({
            "error": "Configuration not available",
            "suggestion": "Please check your configuration files and try again"
        })
    
    if not WORKER_AVAILABLE:
        return json.dumps({
            "error": "Background worker not available",
            "suggestion": "Please restart the application to enable background tasks"
        })
    
    if not source_dir_name or not source_dir_name.strip():
        return json.dumps({
            "error": "Source directory name is required",
            "suggestion": "Please specify the data category to process (e.g., 'credit', 'rates')"
        })
    
    logger.info(f"[Tool] Queuing processing for: {source_dir_name}")
    
    try:
        source_dir_name = source_dir_name.lower().strip()
        available_categories = ['credit', 'rates', 'equity', 'commodities', 'forex']
        
        if source_dir_name not in available_categories:
            return json.dumps({
                "error": f"Invalid data category: {source_dir_name}",
                "suggestion": f"Use one of the available categories",
                "available_categories": available_categories
            })
        
        task_id = add_task(_process_data_task, source_dir_name)
        return json.dumps({
            "message": f"Task queued for processing {source_dir_name} data",
            "task_id": task_id,
            "category": source_dir_name
        })
    except Exception as e:
        logger.error(f"Failed to queue processing task: {str(e)}")
        return json.dumps({
            "error": "Failed to queue processing task",
            "suggestion": "Please try again or contact support"
        })

@handle_tool_errors
def get_database_statistics():
    """Retrieves statistics from the database, such as record counts per table.

    Returns:
        str: A JSON string with the database statistics.
    """
    if not DATABASE_AVAILABLE:
        return json.dumps({
            "error": "Database service not available",
            "suggestion": "Please check your database connection and try again"
        })
    
    logger.info("[Tool] Getting database statistics")
    
    try:
        stats = get_db_stats()
        if isinstance(stats, dict) and "error" in stats:
            return json.dumps(stats)
        
        return json.dumps({
            "database_statistics": stats,
            "message": "Database statistics retrieved successfully",
            "timestamp": str(datetime.now())
        })
    except Exception as e:
        logger.error(f"Failed to get database statistics: {str(e)}")
        return json.dumps({
            "error": "Failed to retrieve database statistics",
            "suggestion": "Please check your database connection and try again"
        })

@handle_tool_errors
def check_task_status(task_id: str):
    """Checks the status of a background task.

    Args:
        task_id (str): The ID of the task to check.

    Returns:
        str: A JSON string with the task's status and result if completed.
    """
    if not WORKER_AVAILABLE:
        return json.dumps({
            "error": "Background worker not available",
            "suggestion": "Please restart the application to enable background tasks"
        })
    
    if not task_id or not task_id.strip():
        return json.dumps({
            "error": "Task ID is required",
            "suggestion": "Please provide a valid task ID"
        })
    
    logger.info(f"[Tool] Checking status for task: {task_id}")
    
    try:
        status = get_task_status_from_worker(task_id.strip())
        return json.dumps({
            "task_status": status,
            "task_id": task_id,
            "timestamp": str(datetime.now())
        })
    except Exception as e:
        logger.error(f"Failed to check task status: {str(e)}")
        return json.dumps({
            "error": "Failed to check task status",
            "suggestion": "Please try again or contact support"
        })


# Enhanced analytics tools with error handling
def create_resilient_analytics_tools():
    """Create analytics tools with proper error handling"""
    if not ANALYTICS_AVAILABLE:
        logger.warning("Analytics tools not available - creating fallback versions")
        return {
            "analyze_market_trends": {
                "function": lambda days_back=30, asset_class=None: json.dumps({
                    "error": "Analytics service not available",
                    "suggestion": "Please check your installation and try again"
                }),
                "schema": {
                    "name": "analyze_market_trends",
                    "description": "Analyze market trends over a specified time period with AI insights (service unavailable)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days_back": {"type": "integer", "description": "Number of days to analyze (default: 30)"},
                            "asset_class": {"type": "string", "description": "Specific asset class to analyze (optional)"}
                        },
                        "required": []
                    }
                }
            }
        }
    return ANALYTICS_TOOLS

def create_resilient_enhanced_analytics_tools():
    """Create enhanced analytics tools with proper error handling"""
    if not ENHANCED_ANALYTICS_AVAILABLE:
        logger.warning("Enhanced analytics tools not available - creating fallback versions")
        return {
            "comprehensive_company_analysis": {
                "function": lambda cik, include_subsidiaries=True: json.dumps({
                    "error": "Enhanced analytics service not available",
                    "suggestion": "Please check your installation and try again"
                }),
                "schema": {
                    "name": "comprehensive_company_analysis",
                    "description": "Company analysis using available financial data sources (service unavailable)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cik": {"type": "string", "description": "Company CIK identifier (required)"},
                            "include_subsidiaries": {"type": "boolean", "description": "Include subsidiary analysis (default: true)"}
                        },
                        "required": ["cik"]
                    }
                }
            }
        }
    return ENHANCED_ANALYTICS_TOOLS

# This dictionary maps tool names to their corresponding functions and schema.
# The schema is essential for the AI to understand how to use each tool.
TOOL_MAP = {
    "search_companies": {
        "function": search_companies,
        "schema": {
            "name": "search_companies",
            "description": "Searches for a company by name or ticker with enhanced error handling and fallbacks.",
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
            "description": "Adds a specific company to the user's target list for focused data processing with validation.",
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
            "description": "Shows the user's current list of target companies with enhanced information.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    "download_data": {
        "function": download_data,
        "schema": {
            "name": "download_data",
            "description": "Queues a background task to download a specific type of financial data with validation. Returns a task ID.",
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
            "description": "Queues a background task to process downloaded data with validation. Returns a task ID.",
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
            "description": "Gets statistics about the database, like table record counts, with error handling.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    "check_task_status": {
        "function": check_task_status,
        "schema": {
            "name": "check_task_status",
            "description": "Checks the status of a background task using its task ID with validation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The ID of the task to check."}
                },
                "required": ["task_id"]
            }
        }
    },
    # Import analytics tools with resilience
    **create_resilient_analytics_tools(),
    # Import enhanced cross-dataset analytics tools with resilience
    **create_resilient_enhanced_analytics_tools()
}
