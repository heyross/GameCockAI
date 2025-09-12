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


def download_cftc_credit_archives():
    os.makedirs(CFTC_CREDIT_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_CREDITS_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)
    urls = generate_urls(start_date, end_date)
    download_archives(urls, CFTC_CREDIT_SOURCE_DIR, rate_limit_delay=1)




def download_cftc_commodities_archives():
    os.makedirs(CFTC_COMMODITIES_SOURCE_DIR, exist_ok=True)
    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_COMMODITIES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)
    urls = generate_urls(start_date, end_date)
    download_archives(urls, CFTC_COMMODITIES_SOURCE_DIR, rate_limit_delay=1)


def download_cftc_rates_archives():
    os.makedirs(CFTC_RATES_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)
    urls = generate_urls(start_date, end_date)
    download_archives(urls, CFTC_RATES_SOURCE_DIR)


def download_cftc_equities_archives():
    os.makedirs(CFTC_EQUITY_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_EQUITIES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)
    urls = generate_urls(start_date, end_date)
    download_archives(urls, CFTC_EQUITY_SOURCE_DIR)


def download_cftc_forex_archives():
    os.makedirs(CFTC_FOREX_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_FOREX_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)
    urls = generate_urls(start_date, end_date)
    download_archives(urls, CFTC_FOREX_SOURCE_DIR)
