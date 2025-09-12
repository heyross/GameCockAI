import os
import glob
import logging
import pandas as pd
from zipfile import ZipFile
from datetime import datetime, timedelta

from downloader import download_archives
from config import (
    CFTC_CREDIT_SOURCE_DIR,
    CFTC_COMMODITIES_SOURCE_DIR,
    CFTC_RATES_SOURCE_DIR,
    CFTC_EQUITY_SOURCE_DIR,
    CFTC_FOREX_SOURCE_DIR,
)


def _generate_cftc_urls(base_url, start_date, end_date):
    """Generates a list of URLs for a given date range, skipping weekends."""
    url_list = []
    current_date = start_date
    while current_date <= end_date:
        # Monday is 0 and Sunday is 6. We only want weekdays.
        if current_date.weekday() < 5:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
        current_date += timedelta(days=1)
    return url_list

def _download_cftc_data(destination_dir, url_fragment, years_back=2, rate_limit_delay=0):
    """Generic function to download CFTC data for a given asset class."""
    os.makedirs(destination_dir, exist_ok=True)
    base_url = f"https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/{url_fragment}"
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=years_back * 365)
    
    urls = _generate_cftc_urls(base_url, start_date, end_date)
    download_archives(urls, destination_dir, rate_limit_delay=rate_limit_delay)

def download_cftc_credit_archives():
    _download_cftc_data(CFTC_CREDIT_SOURCE_DIR, "CFTC_CUMULATIVE_CREDITS_", rate_limit_delay=1)

def download_cftc_commodities_archives():
    _download_cftc_data(CFTC_COMMODITIES_SOURCE_DIR, "CFTC_CUMULATIVE_COMMODITIES_", rate_limit_delay=1)

def download_cftc_rates_archives():
    _download_cftc_data(CFTC_RATES_SOURCE_DIR, "CFTC_CUMULATIVE_RATES_")

def download_cftc_equities_archives():
    _download_cftc_data(CFTC_EQUITY_SOURCE_DIR, "CFTC_CUMULATIVE_EQUITIES_")

def download_cftc_forex_archives():
    _download_cftc_data(CFTC_FOREX_SOURCE_DIR, "CFTC_CUMULATIVE_FOREX_")
