"""
DTCC Data Downloader Module

This module provides functionality to download swap data from the DTCC (Depository Trust & Clearing Corporation)
public data repository. It handles the downloading of various types of swap data including interest rate swaps,
credit default swaps, and other OTC derivatives data.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dtcc_downloader.log')
    ]
)
logger = logging.getLogger(__name__)

# DTCC API endpoints
DTCC_BASE_URL = "https://pddata.dtcc.com/"
DTCC_API_BASE = urljoin(DTCC_BASE_URL, "api/")

# DTCC data endpoints
DTCC_SWAP_DATA_ENDPOINTS = {
    'irs': "report/cumulative/cftc/irs",
    'cds': "report/cumulative/cftc/cds",
    'equity_derivatives': "report/cumulative/cftc/equity_derivatives",
    'commodities': "report/cumulative/cftc/commodities",
    'forex': "report/cumulative/cftc/forex"
}

# Default headers for DTCC API requests
DEFAULT_HEADERS = {
    'User-Agent': 'GameCockAI/1.0 (https://github.com/yourusername/GameCockAI)',
    'Accept': 'application/json',
}

class DTCCHTTPError(requests.HTTPError):
    """Custom exception for DTCC API HTTP errors."""
    pass

class DTCCDownloader:
    """
    A class to handle downloading of DTCC swap data.
    
    This class provides methods to download various types of swap data from DTCC's public data repository,
    including interest rate swaps, credit default swaps, and other OTC derivatives data.
    """
    
    def __init__(self, base_url: str = DTCC_API_BASE, headers: Optional[Dict] = None):
        """
        Initialize the DTCC downloader.
        
        Args:
            base_url: Base URL for the DTCC API
            headers: Optional headers to include in requests
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(headers or DEFAULT_HEADERS)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the DTCC API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            Dict containing the JSON response
            
        Raises:
            DTCCHTTPError: If the request fails
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            if isinstance(e, requests.exceptions.HTTPError):
                raise DTCCHTTPError(f"HTTP Error {e.response.status_code}: {e.response.text}")
            raise
    
    def get_available_dates(self, data_type: str) -> List[str]:
        """
        Get a list of available dates for a specific data type.
        
        Args:
            data_type: Type of data (e.g., 'irs', 'cds', 'equity_derivatives')
            
        Returns:
            List of available dates in 'YYYY-MM-DD' format
        """
        if data_type not in DTCC_SWAP_DATA_ENDPOINTS:
            raise ValueError(f"Invalid data type: {data_type}. Must be one of: {list(DTCC_SWAP_DATA_ENDPOINTS.keys())}")
        
        endpoint = DTCC_SWAP_DATA_ENDPOINTS[data_type]
        data = self._make_request(endpoint)
        return data.get('available_dates', [])
    
    def download_swap_data(
        self,
        data_type: str,
        start_date: str,
        end_date: Optional[str] = None,
        output_dir: str = 'data/dtcc',
        overwrite: bool = False
    ) -> List[str]:
        """
        Download swap data for a specific date range.
        
        Args:
            data_type: Type of data to download (e.g., 'irs', 'cds')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (defaults to start_date if None)
            output_dir: Directory to save downloaded files
            overwrite: Whether to overwrite existing files
            
        Returns:
            List of paths to downloaded files
        """
        if data_type not in DTCC_SWAP_DATA_ENDPOINTS:
            raise ValueError(f"Invalid data type: {data_type}. Must be one of: {list(DTCC_SWAP_DATA_ENDPOINTS.keys())}")
        
        # Set end_date to start_date if not provided
        if end_date is None:
            end_date = start_date
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert string dates to datetime objects for iteration
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        downloaded_files = []
        
        # Iterate through each day in the date range
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y-%m-%d')
            
            # Skip weekends (no data available)
            if current_dt.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                logger.debug(f"Skipping weekend date: {date_str}")
                current_dt += timedelta(days=1)
                continue
            
            # Generate filename based on data type and date
            filename = f"dtcc_{data_type}_{date_str}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Skip if file exists and we're not overwriting
            if os.path.exists(filepath) and not overwrite:
                logger.debug(f"File already exists, skipping: {filepath}")
                downloaded_files.append(filepath)
                current_dt += timedelta(days=1)
                continue
            
            try:
                # Build the endpoint URL for the specific date
                endpoint = f"{DTCC_SWAP_DATA_ENDPOINTS[data_type]}/{date_str}"
                
                # Make the API request
                logger.info(f"Downloading {data_type} data for {date_str}...")
                data = self._make_request(endpoint)
                
                # Save the data to a file
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Saved {data_type} data to {filepath}")
                downloaded_files.append(filepath)
                
            except DTCCHTTPError as e:
                logger.error(f"Failed to download {data_type} data for {date_str}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error processing {date_str}: {e}", exc_info=True)
            
            # Move to the next day
            current_dt += timedelta(days=1)
        
        return downloaded_files
    
    def download_all_swap_data(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        output_base_dir: str = 'data/dtcc',
        overwrite: bool = False
    ) -> Dict[str, List[str]]:
        """
        Download all available types of swap data for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (defaults to start_date if None)
            output_base_dir: Base directory to save downloaded files
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dict mapping data types to lists of downloaded file paths
        """
        results = {}
        
        for data_type in DTCC_SWAP_DATA_ENDPOINTS.keys():
            output_dir = os.path.join(output_base_dir, data_type)
            try:
                files = self.download_swap_data(
                    data_type=data_type,
                    start_date=start_date,
                    end_date=end_date,
                    output_dir=output_dir,
                    overwrite=overwrite
                )
                results[data_type] = files
            except Exception as e:
                logger.error(f"Error downloading {data_type} data: {e}", exc_info=True)
                results[data_type] = []
        
        return results


def download_dtcc_swap_data(
    data_type: str,
    start_date: str,
    end_date: Optional[str] = None,
    output_dir: str = 'data/dtcc',
    overwrite: bool = False
) -> List[str]:
    """
    Convenience function to download DTCC swap data.
    
    Args:
        data_type: Type of data to download (e.g., 'irs', 'cds')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format (defaults to start_date if None)
        output_dir: Directory to save downloaded files
        overwrite: Whether to overwrite existing files
        
    Returns:
        List of paths to downloaded files
    """
    downloader = DTCCDownloader()
    return downloader.download_swap_data(
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        output_dir=output_dir,
        overwrite=overwrite
    )


def download_all_dtcc_swap_data(
    start_date: str,
    end_date: Optional[str] = None,
    output_base_dir: str = 'data/dtcc',
    overwrite: bool = False
) -> Dict[str, List[str]]:
    """
    Convenience function to download all available types of DTCC swap data.
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format (defaults to start_date if None)
        output_base_dir: Base directory to save downloaded files
        overwrite: Whether to overwrite existing files
        
    Returns:
        Dict mapping data types to lists of downloaded file paths
    """
    downloader = DTCCDownloader()
    return downloader.download_all_swap_data(
        start_date=start_date,
        end_date=end_date,
        output_base_dir=output_base_dir,
        overwrite=overwrite
    )


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Download DTCC swap data')
    parser.add_argument('--data-type', type=str, default='all',
                        choices=['all'] + list(DTCC_SWAP_DATA_ENDPOINTS.keys()),
                        help='Type of data to download')
    parser.add_argument('--start-date', type=str, required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                        help='End date (YYYY-MM-DD), defaults to start date')
    parser.add_argument('--output-dir', type=str, default='data/dtcc',
                        help='Output directory for downloaded files')
    parser.add_argument('--overwrite', action='store_true',
                        help='Overwrite existing files')
    
    args = parser.parse_args()
    
    if args.data_type == 'all':
        download_all_dtcc_swap_data(
            start_date=args.start_date,
            end_date=args.end_date,
            output_base_dir=args.output_dir,
            overwrite=args.overwrite
        )
    else:
        download_dtcc_swap_data(
            data_type=args.data_type,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=os.path.join(args.output_dir, args.data_type),
            overwrite=args.overwrite
        )
