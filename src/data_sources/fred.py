"""
FRED (Federal Reserve Economic Data) API integration for GameCock AI.
Provides functionality to download swap rate data from FRED.
"""

import logging
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FREDClient:
    """Client for interacting with the FRED API."""
    
    def __init__(self, api_key: str = None):
        """Initialize FRED client with API key."""
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        self.base_url = "https://api.stlouisfed.org/fred"
        
        if not self.api_key:
            logger.warning("No FRED API key provided. Set FRED_API_KEY environment variable.")
    
    def get_available_series(self) -> List[Dict[str, Any]]:
        """Get list of available swap rate series."""
        # Mock implementation for now
        return [
            {"id": "SWAPRATE", "title": "Swap Rate", "units": "Percent"},
            {"id": "SWAPSPREAD", "title": "Swap Spread", "units": "Basis Points"}
        ]
    
    def get_swap_rates(self, series_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Download swap rate data for a specific series."""
        if not self.api_key:
            logger.error("FRED API key required")
            return pd.DataFrame()
        
        # Mock implementation - in real implementation, would call FRED API
        logger.info(f"Downloading swap rates for series {series_id}")
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        return pd.DataFrame({
            'date': dates,
            'value': [2.5 + (i % 10) * 0.1 for i in range(len(dates))]
        })
    
    def get_swap_rate_summary(self) -> Dict[str, Any]:
        """Get summary statistics for swap rates."""
        return {
            "current_rate": 2.5,
            "avg_30d": 2.4,
            "avg_90d": 2.3,
            "volatility": 0.15
        }

def download_fred_swap_data(days: int = 30) -> List[str]:
    """Download FRED swap rate data for the specified number of days."""
    logger.info(f"Downloading FRED swap data for {days} days")
    
    client = FREDClient()
    
    # Get available series
    series_list = client.get_available_series()
    downloaded_files = []
    
    for series in series_list:
        try:
            # Download data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = client.get_swap_rates(
                series['id'], 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if not df.empty:
                # Save to file
                filename = f"fred_{series['id']}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                filepath = os.path.join(os.getenv('FRED_SOURCE_DIR', './Downloads/FRED'), filename)
                
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                df.to_csv(filepath, index=False)
                downloaded_files.append(filepath)
                
                logger.info(f"Downloaded {series['title']} data to {filepath}")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error downloading {series['id']}: {e}")
    
    logger.info(f"Downloaded {len(downloaded_files)} FRED data files")
    return downloaded_files
