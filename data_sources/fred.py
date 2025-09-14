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

# FRED Series IDs for interest rates and economic indicators
# Source: https://fred.stlouisfed.org/categories/22
SWAP_RATE_SERIES = {
    # US Treasury Yields (as a proxy for swap rates)
    'US_1M': 'DGS1MO',        # 1-Month Treasury Yield
    'US_3M': 'DGS3MO',        # 3-Month Treasury Yield
    'US_6M': 'DGS6MO',        # 6-Month Treasury Yield
    'US_1Y': 'DGS1',          # 1-Year Treasury Yield
    'US_2Y': 'DGS2',          # 2-Year Treasury Yield
    'US_5Y': 'DGS5',          # 5-Year Treasury Yield
    'US_10Y': 'DGS10',        # 10-Year Treasury Yield
    'US_30Y': 'DGS30',        # 30-Year Treasury Yield
    
    # Key Policy Rates
    'FEDFUNDS': 'FEDFUNDS',   # Federal Funds Rate
    'DFF': 'DFF',             # Effective Federal Funds Rate
    'EFFR': 'EFFR',           # EFFR Volume-Weighted Median
    'SOFR': 'SOFR',           # Secured Overnight Financing Rate
    
    # Market Rates
    'LIBOR_1M': 'USD1MTD156N',  # 1-Month LIBOR
    'LIBOR_3M': 'USD3MTD156N',  # 3-Month LIBOR
    'PRIME': 'MPRIME'           # Bank Prime Loan Rate
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
        self.available_series = {}
    
    def check_series_availability(self, series_ids: List[str] = None) -> Dict[str, bool]:
        """Check which series are available in FRED.
        
        Args:
            series_ids: List of series IDs to check. If None, checks all in SWAP_RATE_SERIES.
            
        Returns:
            Dictionary mapping series IDs to availability status (True/False)
        """
        if series_ids is None:
            series_ids = list(SWAP_RATE_SERIES.values())
            
        available = {}
        for series_id in series_ids:
            try:
                # Try to get series info - will raise an exception if not found
                self.fred.get_series_info(series_id)
                available[series_id] = True
                logger.info(f"Found series: {series_id}")
            except Exception as e:
                available[series_id] = False
                logger.warning(f"Series not found: {series_id} - {str(e)}")
                
        self.available_series = {k: v for k, v in available.items() if v}
        return available
    
    def get_series_data(self, series_id: str, days: int = 365) -> pd.DataFrame:
        """Get historical data for a specific FRED series.
        
        Args:
            series_id: The FRED series ID (e.g., 'DGS10' for 10-year Treasury yield)
            days: Number of days of historical data to retrieve (max 10 years for free tier)
            
        Returns:
            DataFrame with date index and values
        """
        # Check if we've already verified this series is available
        if series_id not in self.available_series:
            self.check_series_availability([series_id])
            if series_id not in self.available_series:
                raise ValueError(f"Series {series_id} is not available in FRED")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            data = self.fred.get_series(series_id, start_date, end_date)
            if data.empty:
                logger.warning(f"No data returned for series {series_id} in the specified date range")
                return pd.DataFrame()
                
            # Get series info for better column naming
            try:
                info = self.fred.get_series_info(series_id)
                col_name = info.get('title', series_id).split(';')[0].strip()
            except:
                col_name = series_id
                
            return pd.DataFrame({col_name: data})
            
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            raise
    
    def get_available_series(self, days: int = 30) -> List[dict]:
        """Get a list of available series with their metadata.
        
        Args:
            days: Number of days of data to check for availability
            
        Returns:
            List of dictionaries containing series metadata
        """
        available_series = []
        
        for name, series_id in SWAP_RATE_SERIES.items():
            try:
                # Get series info
                info = self.fred.get_series_info(series_id)
                
                # Try to get some data to verify it's working
                data = self.get_series_data(series_id, days=min(days, 30))
                
                available_series.append({
                    'id': series_id,
                    'name': name,
                    'title': info.get('title', ''),
                    'frequency': info.get('frequency', ''),
                    'units': info.get('units', ''),
                    'last_updated': info.get('last_updated', ''),
                    'data_points': len(data) if not data.empty else 0
                })
                
            except Exception as e:
                logger.debug(f"Skipping unavailable series {series_id}: {e}")
                continue
                
        return available_series
    
    def get_swap_rates(self, series_ids: List[str] = None, days: int = 365) -> Dict[str, pd.DataFrame]:
        """Get multiple interest rate series.
        
        Args:
            series_ids: List of FRED series IDs. If None, uses available series.
            days: Number of days of historical data to retrieve
            
        Returns:
            Dictionary mapping series names to DataFrames with rate data
        """
        # First check which series are available
        available_series = self.get_available_series()
        available_ids = {s['id']: s for s in available_series}
        
        if not series_ids:
            # Use all available series
            series_ids = list(available_ids.keys())
        
        results = {}
        for series_id in series_ids:
            if series_id not in available_ids:
                logger.warning(f"Skipping unavailable series: {series_id}")
                continue
                
            try:
                series_info = available_ids[series_id]
                df = self.get_series_data(series_id, days)
                if not df.empty:
                    results[series_info['name']] = df
            except Exception as e:
                logger.warning(f"Error processing series {series_id}: {e}")
                continue
                
        return results
    
    def get_swap_rate_summary(self, days: int = 30) -> pd.DataFrame:
        """Get a summary of current interest rates with change from previous period.
        
        Args:
            days: Number of days to look back for calculating changes
            
        Returns:
            DataFrame with current rates and changes
        """
        summary = []
        available_series = self.get_available_series(days)
        
        for series in available_series:
            series_id = series['id']
            
            try:
                # Get the full series data
                df = self.get_series_data(series_id, days)
                if df.empty:
                    continue
                    
                series_data = df.iloc[:, 0]  # Get first column
                
                # Get the most recent and previous values
                latest = series_data.iloc[-1]
                previous = series_data.iloc[-2] if len(series_data) > 1 else None
                
                # Calculate percentage change if we have previous value
                if pd.notna(previous) and previous != 0:
                    change_pct = (latest - previous) / abs(previous) * 100
                else:
                    change_pct = None
                
                summary.append({
                    'series_id': series_id,
                    'name': series['name'],
                    'title': series['title'],
                    'current_rate': latest,
                    'previous_rate': previous,
                    'change_pct': change_pct,
                    'last_updated': series_data.index[-1].strftime('%Y-%m-%d'),
                    'frequency': series['frequency'],
                    'units': series['units']
                })
                
            except Exception as e:
                logger.warning(f"Error processing {series.get('name', series_id)}: {e}")
                continue
        
        return pd.DataFrame(summary)

def download_fred_swap_data(output_dir: str = 'data/fred', days: int = 365) -> Dict[str, str]:
    """Download interest rate data from FRED and save to CSV files.
    
    Args:
        output_dir: Directory to save the downloaded files
        days: Number of days of historical data to retrieve
        
    Returns:
        Dictionary mapping series names to file paths of saved data
    """
    os.makedirs(output_dir, exist_ok=True)
    saved_files = {}
    
    try:
        client = FREDClient()
        
        # First, get available series with metadata
        logger.info("Checking available FRED series...")
        available_series = client.get_available_series(days=min(days, 30))
        
        if not available_series:
            logger.warning("No available FRED series found. Check your API key and internet connection.")
            return {}
            
        logger.info(f"Found {len(available_series)} available series")
        
        # Get all available interest rate series
        logger.info(f"Downloading up to {days} days of historical data...")
        all_rates = client.get_swap_rates(days=days)
        
        if not all_rates:
            logger.warning("No data was downloaded. No valid series available.")
            return {}
        
        # Save each series to a CSV file
        for series_name, data in all_rates.items():
            if not data.empty:
                # Clean the series name for filename
                safe_name = "".join(c if c.isalnum() else "_" for c in series_name)
                filename = f"{safe_name}.csv"
                filepath = os.path.join(output_dir, filename)
                
                # Save with index (dates) and proper header
                data.to_csv(filepath, index_label='date')
                saved_files[series_name] = filepath
                logger.info(f"Saved {len(data)} data points to {filepath}")
        
        # Save a summary of all rates
        logger.info("Generating summary...")
        summary = client.get_swap_rate_summary(days=min(days, 365))  # Limit to 1 year for summary
        
        if not summary.empty:
            summary_file = os.path.join(output_dir, 'interest_rates_summary.csv')
            # Reorder columns for better readability
            cols = ['name', 'title', 'current_rate', 'units', 'change_pct', 
                   'last_updated', 'frequency', 'series_id']
            summary[cols].to_csv(summary_file, index=False, float_format='%.4f')
            logger.info(f"Saved interest rate summary to {summary_file}")
        
        return saved_files
        
    except Exception as e:
        logger.error(f"Error downloading FRED data: {e}")
        logger.exception("Full error details:")
        raise
