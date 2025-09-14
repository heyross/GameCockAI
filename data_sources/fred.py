"""
FRED (Federal Reserve Economic Data) API client for fetching economic data.

This module provides functionality to fetch swap rates and other economic data
from the Federal Reserve Economic Data (FRED) API.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# FRED API key (get one at https://fred.stlouisfed.org/docs/api/api_key.html)
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    logger.warning("FRED_API_KEY not found in environment variables. Some functionality may be limited.")

# FRED Series IDs for swap rates (source: https://fred.stlouisfed.org/categories/33045)
SWAP_RATE_SERIES = {
    # USD Interest Rate Swaps
    'USD_1Y': 'DSWRD1',    # 1-Year USD Swap Rate
    'USD_2Y': 'DSWRD2',    # 2-Year USD Swap Rate
    'USD_5Y': 'DSWRD5',    # 5-Year USD Swap Rate
    'USD_10Y': 'DSWRD10',  # 10-Year USD Swap Rate
    'USD_30Y': 'DSWRD30',  # 30-Year USD Swap Rate
    
    # EUR Interest Rate Swaps
    'EUR_1Y': 'DSWRD1F',   # 1-Year EUR Swap Rate
    'EUR_5Y': 'DSWRD5F',   # 5-Year EUR Swap Rate
    'EUR_10Y': 'DSWRD10F', # 10-Year EUR Swap Rate
    
    # Credit Default Swaps (CDS)
    'CDX_IG': 'CDXIG',     # CDX North America Investment Grade Index
    'CDX_HY': 'CDXHY',     # CDX North America High Yield Index
}

class FREDClient:
    """Client for interacting with the FRED API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the FRED client with an API key.
        
        Args:
            api_key: FRED API key. If not provided, will try to use FRED_API_KEY from environment.
        """
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED API key is required. Get one at https://fred.stlouisfed.org/docs/api/api_key.html")
        
        self.fred = Fred(api_key=self.api_key)
    
    def get_swap_rate(self, series_id: str, days: int = 365) -> pd.DataFrame:
        """Get historical swap rate data for a specific series.
        
        Args:
            series_id: The FRED series ID (e.g., 'DSWRD10' for 10-year USD swap rate)
            days: Number of days of historical data to retrieve (max 10 years for free tier)
            
        Returns:
            DataFrame with date index and rate values
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            data = self.fred.get_series(series_id, start_date, end_date)
            return pd.DataFrame({'rate': data}, index=data.index)
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            raise
    
    def get_swap_rates(self, series_ids: List[str] = None, days: int = 365) -> Dict[str, pd.DataFrame]:
        """Get multiple swap rate series.
        
        Args:
            series_ids: List of FRED series IDs. If None, uses default swap rate series.
            days: Number of days of historical data to retrieve
            
        Returns:
            Dictionary mapping series IDs to DataFrames with rate data
        """
        if series_ids is None:
            series_ids = list(SWAP_RATE_SERIES.values())
        
        results = {}
        for series_id in series_ids:
            try:
                results[series_id] = self.get_swap_rate(series_id, days)
            except Exception as e:
                logger.warning(f"Skipping series {series_id}: {e}")
                continue
                
        return results
    
    def get_swap_rate_summary(self, days: int = 30) -> pd.DataFrame:
        """Get a summary of current swap rates with change from previous period.
        
        Args:
            days: Number of days to look back for calculating changes
            
        Returns:
            DataFrame with current rates and changes
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        summary = []
        
        for name, series_id in SWAP_RATE_SERIES.items():
            try:
                # Get the full series data
                series = self.fred.get_series(series_id, start_date, end_date)
                if series.empty:
                    continue
                
                # Get the most recent and previous values
                latest = series.iloc[-1]
                previous = series.iloc[-2] if len(series) > 1 else None
                change = (latest - previous) / previous * 100 if previous is not None else None
                
                summary.append({
                    'series_id': series_id,
                    'name': name,
                    'current_rate': latest,
                    'previous_rate': previous,
                    'change_pct': change,
                    'last_updated': series.index[-1].strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                logger.warning(f"Error processing {name} ({series_id}): {e}")
                continue
        
        return pd.DataFrame(summary)

def download_fred_swap_data(output_dir: str = 'data/fred', days: int = 365) -> Dict[str, str]:
    """Download swap rate data from FRED and save to CSV files.
    
    Args:
        output_dir: Directory to save the downloaded files
        days: Number of days of historical data to retrieve
        
    Returns:
        Dictionary mapping series IDs to file paths of saved data
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        client = FREDClient()
        
        # Get all swap rate series
        swap_rates = client.get_swap_rates(days=days)
        
        # Save each series to a CSV file
        saved_files = {}
        for series_id, data in swap_rates.items():
            if not data.empty:
                # Get the series name for the filename
                series_name = next((k for k, v in SWAP_RATE_SERIES.items() if v == series_id), series_id)
                filename = f"{series_name}.csv"
                filepath = os.path.join(output_dir, filename)
                data.to_csv(filepath)
                saved_files[series_id] = filepath
                logger.info(f"Saved {len(data)} data points to {filepath}")
        
        # Also save a summary file
        summary = client.get_swap_rate_summary()
        if not summary.empty:
            summary_file = os.path.join(output_dir, 'swap_rates_summary.csv')
            summary.to_csv(summary_file, index=False)
            logger.info(f"Saved swap rate summary to {summary_file}")
        
        return saved_files
        
    except Exception as e:
        logger.error(f"Error downloading FRED swap data: {e}")
        raise
