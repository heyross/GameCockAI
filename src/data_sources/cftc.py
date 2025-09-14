import os
import glob
import logging
import json
import requests
import pandas as pd
from zipfile import ZipFile
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

try:
    from downloader import download_archives
    from config import (
        CFTC_CREDIT_SOURCE_DIR,
        CFTC_COMMODITIES_SOURCE_DIR,
        CFTC_RATES_SOURCE_DIR,
        CFTC_EQUITY_SOURCE_DIR,
        CFTC_FOREX_SOURCE_DIR,
        CFTC_SWAP_DEALER_DIR,
        CFTC_SWAP_EXECUTION_DIR,
        CFTC_SWAP_DATA_REPOSITORY_DIR,
        CFTC_SWAP_DEALER_URL,
        CFTC_SWAP_EXECUTION_URL,
        CFTC_SWAP_DATA_REPOSITORY_URL,
    )
except ImportError:
    # Fallback for when running from root directory
    from GameCockAI.src.downloader import download_archives
    from GameCockAI.config import (
        CFTC_CREDIT_SOURCE_DIR,
        CFTC_COMMODITIES_SOURCE_DIR,
        CFTC_RATES_SOURCE_DIR,
        CFTC_EQUITY_SOURCE_DIR,
        CFTC_FOREX_SOURCE_DIR,
        CFTC_SWAP_DEALER_DIR,
        CFTC_SWAP_EXECUTION_DIR,
        CFTC_SWAP_DATA_REPOSITORY_DIR,
        CFTC_SWAP_DEALER_URL,
        CFTC_SWAP_EXECUTION_URL,
        CFTC_SWAP_DATA_REPOSITORY_URL,
    )

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _generate_cftc_urls(base_url: str, start_date: datetime, end_date: datetime) -> List[str]:
    """
    Generates a list of URLs for a given date range, skipping weekends.
    
    Args:
        base_url: Base URL for the CFTC data
        start_date: Start date for the date range
        end_date: End date for the date range
        
    Returns:
        List of formatted URLs for each business day in the range
    """
    url_list = []
    current_date = start_date
    while current_date <= end_date:
        # Monday is 0 and Sunday is 6. We only want weekdays.
        if current_date.weekday() < 5:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
        current_date += timedelta(days=1)
    return url_list

def _download_cftc_data(destination_dir: str, url_fragment: str, years_back: int = 2, rate_limit_delay: float = 0.5) -> None:
    """
    Generic function to download CFTC data for a given asset class.
    
    Args:
        destination_dir: Directory to save the downloaded files
        url_fragment: URL fragment specific to the data type
        years_back: Number of years of historical data to download
        rate_limit_delay: Delay between requests in seconds to avoid rate limiting
    """
    try:
        os.makedirs(destination_dir, exist_ok=True)
        base_url = f"https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/{url_fragment}"
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=years_back * 365)
        
        urls = _generate_cftc_urls(base_url, start_date, end_date)
        logger.info(f"Downloading {len(urls)} files to {destination_dir}")
        download_archives(urls, destination_dir, rate_limit_delay=rate_limit_delay)
        
    except Exception as e:
        logger.error(f"Error downloading CFTC data: {e}")
        raise

def _fetch_swap_data(url: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Fetches data from the CFTC Swap Data Repositories.
    
    Args:
        url: API endpoint URL or web page URL
        params: Optional query parameters for API requests
        
    Returns:
        List of dictionaries containing the response data
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }
        
        # Check if this is an API endpoint or a webpage
        if url.startswith('https://www.cftc.gov/api/'):
            # Handle API endpoints
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Handle pagination if needed
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            return data
            
        else:
            # Handle web pages (returning basic info for now)
            return [{
                'url': url,
                'note': 'This is a web page. Please visit the URL for detailed information.',
                'last_updated': datetime.now().isoformat()
            }]
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing {url}: {e}")
        raise

def _save_swap_data(data: List[Dict[str, Any]], file_path: str) -> None:
    """
    Saves swap data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the data
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} records to {file_path}")
    except IOError as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        raise

# Standard CFTC Data Download Functions
def download_cftc_credit_archives() -> None:
    """Download CFTC credit derivatives data."""
    _download_cftc_data(CFTC_CREDIT_SOURCE_DIR, "CFTC_CUMULATIVE_CREDITS_")

def download_cftc_commodities_archives() -> None:
    """Download CFTC commodities data."""
    _download_cftc_data(CFTC_COMMODITIES_SOURCE_DIR, "CFTC_CUMULATIVE_COMMODITIES_")

def download_cftc_rates_archives() -> None:
    """Download CFTC interest rates data."""
    _download_cftc_data(CFTC_RATES_SOURCE_DIR, "CFTC_CUMULATIVE_RATES_")

def download_cftc_equities_archives() -> None:
    """Download CFTC equities data."""
    _download_cftc_data(CFTC_EQUITY_SOURCE_DIR, "CFTC_CUMULATIVE_EQUITIES_")

def download_cftc_forex_archives() -> None:
    """Download CFTC forex data."""
    _download_cftc_data(CFTC_FOREX_SOURCE_DIR, "CFTC_CUMULATIVE_FOREX_")

# Swap Data Download Functions
def download_swap_dealer_data() -> None:
    """
    Download CFTC swap dealer and major swap participant data.
    This now provides information about where to find the data online.
    """
    try:
        os.makedirs(CFTC_SWAP_DEALER_DIR, exist_ok=True)
        logger.info("Fetching swap dealer information...")
        
        # Get basic info about the data source
        data = _fetch_swap_data(CFTC_SWAP_DEALER_URL)
        
        # Save the data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(CFTC_SWAP_DEALER_DIR, f'swap_dealers_info_{timestamp}.json')
        _save_swap_data(data, file_path)
        
        print("\nSwap Dealer Data Source Information:")
        print(f"- Data available at: {CFTC_SWAP_DEALER_URL}")
        print("- This is a web page with the latest list of registered swap dealers and major swap participants")
        print(f"- Information saved to: {file_path}")
        
    except Exception as e:
        logger.error(f"Error accessing swap dealer information: {e}")
        print(f"\nNote: Direct API access to swap dealer data is not available.")
        print(f"Please visit {CFTC_SWAP_DEALER_URL} for the latest information.")

def download_swap_execution_facility_data() -> None:
    """
    Download CFTC swap execution facility data.
    This now provides information about where to find the data online.
    """
    try:
        os.makedirs(CFTC_SWAP_EXECUTION_DIR, exist_ok=True)
        logger.info("Fetching swap execution facility information...")
        
        # Get basic info about the data source
        data = _fetch_swap_data(CFTC_SWAP_EXECUTION_URL)
        
        # Save the data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(CFTC_SWAP_EXECUTION_DIR, f'sef_info_{timestamp}.json')
        _save_swap_data(data, file_path)
        
        print("\nSwap Execution Facility Information:")
        print(f"- Data available at: {CFTC_SWAP_EXECUTION_URL}")
        print("- This is a web page with the latest list of registered Swap Execution Facilities (SEFs)")
        print(f"- Information saved to: {file_path}")
        
    except Exception as e:
        logger.error(f"Error accessing swap execution facility information: {e}")
        print(f"\nNote: Direct API access to SEF data is not available.")
        print(f"Please visit {CFTC_SWAP_EXECUTION_URL} for the latest information.")

def download_swap_data_repository_data() -> None:
    """
    Download CFTC swap data repository data.
    This now provides information about where to find the data online.
    """
    try:
        os.makedirs(CFTC_SWAP_DATA_REPOSITORY_DIR, exist_ok=True)
        logger.info("Fetching swap data repository information...")
        
        # Get basic info about the data source
        data = _fetch_swap_data(CFTC_SWAP_DATA_REPOSITORY_URL)
        
        # Save the data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(CFTC_SWAP_DATA_REPOSITORY_DIR, f'sdr_info_{timestamp}.json')
        _save_swap_data(data, file_path)
        
        print("\nSwap Data Repository Information:")
        print(f"- Data available at: {CFTC_SWAP_DATA_REPOSITORY_URL}")
        print("- This is a web page with information about Swap Data Repositories (SDRs)")
        print(f"- Information saved to: {file_path}")
        
    except Exception as e:
        logger.error(f"Error accessing swap data repository information: {e}")
        print(f"\nNote: Direct API access to SDR data is not available.")
        print(f"Please visit {CFTC_SWAP_DATA_REPOSITORY_URL} for the latest information.")

def download_all_swap_data() -> None:
    """Download all available CFTC swap data."""
    try:
        logger.info("Starting download of all CFTC swap data...")
        download_swap_dealer_data()
        download_swap_execution_facility_data()
        download_swap_data_repository_data()
        logger.info("Completed download of all CFTC swap data")
    except Exception as e:
        logger.error(f"Error during CFTC swap data download: {e}")
        raise
