import os
import glob
import logging
import pandas as pd
import requests
import hashlib
import zipfile
import time
import concurrent.futures
from datetime import datetime, timedelta
from queue import Queue

from downloader import download_archives, download_file
from config import (
    INSIDER_SOURCE_DIR,
    EXCHANGE_SOURCE_DIR,
    EDGAR_SOURCE_DIR,
    CREDIT_SOURCE_DIR,
    EQUITY_SOURCE_DIR,
    NCEN_SOURCE_DIR,
    NPORT_SOURCE_DIR,
    THRTNF_SOURCE_DIR,
    NMFP_SOURCE_DIR,
    FORMD_SOURCE_DIR
)

def download_insider_archives():
    os.makedirs(INSIDER_SOURCE_DIR, exist_ok=True)
    base_url = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/"
    file_names = [
        "2006q1_form345.zip",
        "2006q2_form345.zip",
        "2006q3_form345.zip",
        "2006q4_form345.zip",
        "2007q1_form345.zip",
        "2007q2_form345.zip",
        "2007q3_form345.zip",
        "2007q4_form345.zip",
        "2008q1_form345.zip",
        "2008q2_form345.zip",
        "2008q3_form345.zip",
        "2008q4_form345.zip",
        "2009q1_form345.zip",
        "2009q2_form345.zip",
        "2009q3_form345.zip",
        "2009q4_form345.zip",
        "2010q1_form345.zip",
        "2010q2_form345.zip",
        "2010q3_form345.zip",
        "2010q4_form345.zip",
        "2011q1_form345.zip",
        "2011q2_form345.zip",
        "2011q3_form345.zip",
        "2011q4_form345.zip",
        "2012q1_form345.zip",
        "2012q2_form345.zip",
        "2012q3_form345.zip",
        "2012q4_form345.zip",
        "2013q1_form345.zip",
        "2013q2_form345.zip",
        "2013q3_form345.zip",
        "2013q4_form345.zip",
        "2014q1_form345.zip",
        "2014q2_form345.zip",
        "2014q3_form345.zip",
        "2014q4_form345.zip",
        "2015q1_form345.zip",
        "2015q2_form345.zip",
        "2015q3_form345.zip",
        "2015q4_form345.zip",
        "2016q1_form345.zip",
        "2016q2_form345.zip",
        "2016q3_form345.zip",
        "2016q4_form345.zip",
        "2017q1_form345.zip",
        "2017q2_form345.zip",
        "2017q3_form345.zip",
        "2017q4_form345.zip",
        "2018q1_form345.zip",
        "2018q2_form345.zip",
        "2018q3_form345.zip",
        "2018q4_form345.zip",
        "2019q1_form345.zip",
        "2019q2_form345.zip",
        "2019q3_form345.zip",
        "2019q4_form345.zip",
        "2020q1_form345.zip",
        "2020q2_form345.zip",
        "2020q3_form345.zip",
        "2020q4_form345.zip",
        "2021q1_form345.zip",
        "2021q2_form345.zip",
        "2021q3_form345.zip",
        "2021q4_form345.zip",
        "2022q1_form345.zip",
        "2022q2_form345.zip",
        "2022q3_form345.zip",
        "2022q4_form345.zip",
        "2023q1_form345.zip",
        "2023q2_form345.zip",
        "2023q3_form345.zip",
        "2023q4_form345.zip",
        "2024q1_form345.zip",
        "2024q2_form345.zip",
        "2024q3_form345.zip",
    ]
    urls = [f"{base_url}{file_name}" for file_name in file_names]
    download_archives(urls, INSIDER_SOURCE_DIR)

def download_exchange_archives():
    os.makedirs(EXCHANGE_SOURCE_DIR, exist_ok=True)
    base_url = "https://www.sec.gov/files/opa/data/market-structure/metrics-individual-security-and-exchange/"
    file_names = [
        "individual_security_exchange_2012_q1.zip",
        "individual_security_exchange_2012_q20.zip",
        "individual_security_exchange_2012_q30.zip",
        "individual_security_exchange_2012_q40.zip",
        "individual_security_exchange_2013_q10.zip",
        "individual_security_exchange_2013_q20.zip",
        "individual_security_exchange_2013_q30.zip",
        "individual_security_exchange_2013_q43.zip",
        "individual_security_exchange_2014_q1.zip",
        "individual_security_exchange_2014_q2.zip",
        "individual_security_exchange_2014_q3.zip",
        "individual_security_exchange_2014_q4.zip",
        "individual_security_exchange_2015_q1.zip",
        "individual_security_exchange_2015_q2.zip",
        "individual_security_exchange_2015_q3.zip",
        "individual_security_exchange_2015_q4.zip",
        "individual_security_exchange_2016_q1-v2.zip",
        "individual_security_exchange_2016_q2.zip",
        "individual_security_exchange_2016_q3.zip",
        "individual_security_exchange_2016_q4.zip",
        "individual_security_exchange_2017_q1.zip",
        "individual_security_exchange_2017_q2.zip",
        "individual_security_exchange_2017_q3.zip",
        "individual_security_exchange_2017_q4.zip",
        "individual_security_exchange_2018_q1.zip",
        "individual_security_exchange_2018_q2.zip",
        "individual_security_exchange_2018_q3.zip",
        "individual_security_exchange_2018_q4.zip",
        "individual_security_exchange_2019_q1.zip",
        "individual_security_exchange_2019_q2.zip",
        "individual_security_exchange_2019_q3.zip",
        "individual_security_exchange_2019_q4.zip",
        "individual_security_exchange_2020_q1.zip",
        "individual_security_exchange_2020_q2.zip",
        "individual_security_exchange_2020_q3.zip",
        "individual_security_exchange_2020_q4.zip",
        "individual_security_exchange_2021_q1.zip",
        "individual_security_exchange_2021_q2.zip",
        "individual_security_exchange_2021_q3.zip",
        "individual_security_exchange_2021_q4.zip",
        "individual_security_exchange_2022_q1.zip",
        "individual_security_exchange_2022_q2.zip",
        "individual_security_exchange_2022_q3.zip",
        "individual_security_exchange_2022_q4.zip",
        "individual_security_exchange_2023_q1.zip",
        "individual_security_exchange_2023_q2.zip",
        "individual_security_exchange_2023_q3.zip",
        "individual_security_exchange_2023_q4.zip",
        "individual_security_exchange_2024_q1.zip",
        "individual_security_exchange_2024_q2.zip",
        "individual_security_exchange_2024_q3.zip"
    ]
    urls = [f"{base_url}{file_name}" for file_name in file_names]
    download_archives(urls, EXCHANGE_SOURCE_DIR)

def allyourbasearebelongtous():
    file_queue = Queue()
    idx_file = os.path.join(EDGAR_SOURCE_DIR, "master.idx")
    log_file = os.path.join(EDGAR_SOURCE_DIR, "sec_download_log.txt")

    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='error_log.txt',
        filemode='w'
    )

    def log_progress(message):
        with open(log_file, 'a') as log:
            log.write(f"{datetime.now()}: {message}\n")
        print(message)

    def download_edgar_file(url, download_directory):
        try:
            headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            filename = url.split('/')[-1]
            cik_parts = url.split('/data/')
            if len(cik_parts) > 1:
                cik = cik_parts[1].split('/')[0]
                dir_path = os.path.join(download_directory, cik)
                os.makedirs(dir_path, exist_ok=True)
                filepath = os.path.join(dir_path, filename)
            else:
                filepath = os.path.join(download_directory, filename)

            if os.path.exists(filepath):
                # File verification logic can be added here if needed
                print(f"FILE already downloaded: {filepath}")
                return True, filepath

            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"Downloaded: {filepath}")
            return True, filepath

        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False, None

    def process_line(line):
        parts = line.split('|')
        if len(parts) >= 5:
            filename = parts[4].strip()
            if filename.endswith("Filename"):
                filename = filename.rsplit('/', 1)[0]
            url = f"https://www.sec.gov/Archives/{filename}"
            return url
        return None

    def extract_idx_from_zip(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith('.idx'):
                    return zip_ref.read(file_name).decode('utf-8', errors='ignore')
        raise FileNotFoundError("No IDX file found in ZIP archive.")

    # TODO: The original logic for processing EDGAR filings is complex and needs a full refactoring.
    # This includes handling user input for selecting years/quarters, compiling a master index, 
    # and managing the download and processing of a large number of files.
    # This will be addressed in a future development cycle.
    print("EDGAR processing logic is not yet fully implemented.")

def download_credit_archives():
    os.makedirs(CREDIT_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_CREDITS_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)
    urls = generate_urls(start_date, end_date)
    download_archives(urls, CREDIT_SOURCE_DIR, rate_limit_delay=1)

def download_equities_archives():
    os.makedirs(EQUITY_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_EQUITIES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)
    urls = generate_urls(start_date, end_date)
    download_archives(urls, EQUITY_SOURCE_DIR)

def download_ncen_archives():
    os.makedirs(NCEN_SOURCE_DIR, exist_ok=True)
    BASE_URL = "https://www.sec.gov/files/dera/data/form-n-cen-data-sets/"
    urls = [
        BASE_URL + "2019q3_ncen.zip",
        BASE_URL + "2019q4_ncen.zip",
        BASE_URL + "2020q1_ncen.zip",
        BASE_URL + "2020q2_ncen.zip",
        BASE_URL + "2020q3_ncen.zip",
        BASE_URL + "2020q4_ncen.zip",
        BASE_URL + "2021q1_ncen.zip",
        BASE_URL + "2021q2_ncen.zip",
        BASE_URL + "2021q3_ncen.zip",
        BASE_URL + "2021q4_ncen.zip",
        BASE_URL + "2022q1_ncen.zip",
        BASE_URL + "2022q2_ncen.zip",
        BASE_URL + "2022q3_ncen.zip",
        BASE_URL + "2022q4_ncen.zip",
        BASE_URL + "2023q1_ncen.zip",
        BASE_URL + "2023q2_ncen.zip",
        BASE_URL + "2023q3_ncen.zip",
        BASE_URL + "2023q4_ncen.zip",
        BASE_URL + "2024q1_ncen.zip",
        BASE_URL + "2024q2_ncen.zip",
        BASE_URL + "2024q3_ncen.zip",
        BASE_URL + "2024q4_ncen.zip",
        BASE_URL + "2025q1_ncen.zip",
        BASE_URL + "2025q2_ncen.zip",
    ]
    download_archives(urls, NCEN_SOURCE_DIR)

def download_nport_archives():
    os.makedirs(NPORT_SOURCE_DIR, exist_ok=True)
    BASE_URL = "https://www.sec.gov/files/dera/data/form-n-port-data-sets/"
    urls = [
        BASE_URL + "2019q4_nport.zip",
        BASE_URL + "2020q1_nport.zip",
        BASE_URL + "2020q2_nport.zip",
        BASE_URL + "2020q3_nport.zip",
        BASE_URL + "2020q4_nport.zip",
        BASE_URL + "2021q1_nport.zip",
        BASE_URL + "2021q2_nport.zip",
        BASE_URL + "2021q3_nport.zip",
        BASE_URL + "2021q4_nport.zip",
        BASE_URL + "2022q1_nport.zip",
        BASE_URL + "2022q2_nport.zip",
        BASE_URL + "2022q3_nport.zip",
        BASE_URL + "2022q4_nport.zip",
        BASE_URL + "2023q1_nport.zip",
        BASE_URL + "2023q2_nport.zip",
        BASE_URL + "2023q3_nport.zip",
        BASE_URL + "2023q4_nport.zip",
        BASE_URL + "2024q1_nport.zip",
        BASE_URL + "2024q2_nport.zip",
        BASE_URL + "2024q3_nport.zip",
        BASE_URL + "2024q4_nport.zip",
        BASE_URL + "2025q1_nport.zip",
        BASE_URL + "2025q2_nport.zip",
    ]
    download_archives(urls, NPORT_SOURCE_DIR)

def download_13F_archives():
    os.makedirs(THRTNF_SOURCE_DIR, exist_ok=True)
    BASE_URL = "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/"
    urls = [
        BASE_URL + "2013q2_form13f.zip",
        BASE_URL + "2013q3_form13f.zip",
        BASE_URL + "2013q4_form13f.zip",
        BASE_URL + "2014q1_form13f.zip",
        BASE_URL + "2014q2_form13f.zip",
        BASE_URL + "2014q3_form13f.zip",
        BASE_URL + "2014q4_form13f.zip",
        BASE_URL + "2015q1_form13f.zip",
        BASE_URL + "2015q2_form13f.zip",
        BASE_URL + "2015q3_form13f.zip",
        BASE_URL + "2015q4_form13f.zip",
        BASE_URL + "2016q1_form13f.zip",
        BASE_URL + "2016q2_form13f.zip",
        BASE_URL + "2016q3_form13f.zip",
        BASE_URL + "2016q4_form13f.zip",
        BASE_URL + "2017q1_form13f.zip",
        BASE_URL + "2017q2_form13f.zip",
        BASE_URL + "2017q3_form13f.zip",
        BASE_URL + "2017q4_form13f.zip",
        BASE_URL + "2018q1_form13f.zip",
        BASE_URL + "2018q2_form13f.zip",
        BASE_URL + "2018q3_form13f.zip",
        BASE_URL + "2018q4_form13f.zip",
        BASE_URL + "2019q1_form13f.zip",
        BASE_URL + "2019q2_form13f.zip",
        BASE_URL + "2019q3_form13f.zip",
        BASE_URL + "2019q4_form13f.zip",
        BASE_URL + "2020q1_form13f.zip",
        BASE_URL + "2020q2_form13f.zip",
        BASE_URL + "2020q3_form13f.zip",
        BASE_URL + "2020q4_form13f.zip",
        BASE_URL + "2021q1_form13f.zip",
        BASE_URL + "2021q2_form13f.zip",
        BASE_URL + "2021q3_form13f.zip",
        BASE_URL + "2021q4_form13f.zip",
        BASE_URL + "2022q1_form13f.zip",
        BASE_URL + "2022q2_form13f.zip",
        BASE_URL + "2022q3_form13f.zip",
        BASE_URL + "2022q4_form13f.zip",
        BASE_URL + "2023q1_form13f.zip",
        BASE_URL + "2023q2_form13f.zip",
        BASE_URL + "2023q3_form13f.zip",
        BASE_URL + "2023q4_form13f.zip",
        BASE_URL + "01jan2024-29feb2024_form13f.zip",
        BASE_URL + "01mar2024-31may2024_form13f.zip",
        BASE_URL + "01jun2024-31aug2024_form13f.zip",
        BASE_URL + "01sep2024-30nov2024_form13f.zip",
    ]
    download_archives(urls, THRTNF_SOURCE_DIR)

def download_nmfp_archives():
    os.makedirs(NMFP_SOURCE_DIR, exist_ok=True)
    BASE_URL = "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/"
    urls = [
        BASE_URL + "2010q4_nmfp.zip",
        BASE_URL + "2011q1_nmfp.zip",
        BASE_URL + "2011q2_nmfp.zip",
        BASE_URL + "2011q3_nmfp.zip",
        BASE_URL + "2011q4_nmfp.zip",
        BASE_URL + "2012q1_nmfp.zip",
        BASE_URL + "2012q2_nmfp.zip",
        BASE_URL + "2012q3_nmfp.zip",
        BASE_URL + "2012q4_nmfp.zip",
        BASE_URL + "2013q1_nmfp.zip",
        BASE_URL + "2013q2_nmfp.zip",
        BASE_URL + "2013q3_nmfp.zip",
        BASE_URL + "2013q4_nmfp.zip",
        BASE_URL + "2014q1_nmfp.zip",
        BASE_URL + "2014q2_nmfp.zip",
        BASE_URL + "2014q3_nmfp.zip",
        BASE_URL + "2014q4_nmfp.zip",
        BASE_URL + "2015q1_nmfp.zip",
        BASE_URL + "2015q2_nmfp.zip",
        BASE_URL + "2015q3_nmfp.zip",
        BASE_URL + "2015q4_nmfp.zip",
        BASE_URL + "2016q1_nmfp.zip",
        BASE_URL + "2016q2_nmfp.zip",
        BASE_URL + "2016q3_nmfp.zip",
        BASE_URL + "2016q4_nmfp.zip",
        BASE_URL + "2017q1_nmfp.zip",
        BASE_URL + "2017q2_nmfp.zip",
        BASE_URL + "2017q3_nmfp.zip",
        BASE_URL + "2017q4_nmfp.zip",
        BASE_URL + "2018q1_nmfp.zip",
        BASE_URL + "2018q2_nmfp.zip",
        BASE_URL + "2018q3_nmfp.zip",
        BASE_URL + "2018q4_nmfp.zip",
        BASE_URL + "2019q1_nmfp.zip",
        BASE_URL + "2019q2_nmfp.zip",
        BASE_URL + "2019q3_nmfp.zip",
        BASE_URL + "2019q4_nmfp.zip",
        BASE_URL + "2020q1_nmfp.zip",
        BASE_URL + "2020q2_nmfp.zip",
        BASE_URL + "2020q3_nmfp.zip",
        BASE_URL + "2020q4_nmfp.zip",
        BASE_URL + "2021q1_nmfp.zip",
        BASE_URL + "2021q2_nmfp.zip",
        BASE_URL + "2021q3_nmfp.zip",
        BASE_URL + "2021q4_nmfp.zip",
        BASE_URL + "2022q1_nmfp.zip",
        BASE_URL + "2022q2_nmfp.zip",
        BASE_URL + "20221007_nmfp.zip",
        BASE_URL + "20220701-20220710_nmfp",
        BASE_URL + "20220808-20220908_nmfp.zip",
        BASE_URL + "20221108-20221207_nmfp.zip",
        BASE_URL + "20221208-20230109_nmfp.zip",
        BASE_URL + "20230110-20230207_nmfp.zip",
        BASE_URL + "20230208-20230307_nmfp.zip",
        BASE_URL + "20230308-20230410_nmfp.zip",
        BASE_URL + "20230411-20230505_nmfp.zip",
        BASE_URL + "20230508-20230607_nmfp.zip",
        BASE_URL + "20230608-20230711_nmfp.zip",
        BASE_URL + "20230712-20230807_nmfp.zip",
        BASE_URL + "20230808-20230911_nmfp.zip",
        BASE_URL + "20230912-20231006_nmfp.zip",
        BASE_URL + "20231010-20231107_nmfp.zip",
        BASE_URL + "20231108-20231207_nmfp.zip",
        BASE_URL + "20231208-20240108_nmfp.zip",
        BASE_URL + "20240109-20240207_nmfp.zip",
        BASE_URL + "20240208-20240307_nmfp.zip",
        BASE_URL + "20240308-20240405_nmfp.zip",
        BASE_URL + "20240408-20240507_nmfp.zip",
        BASE_URL + "20240508-20240607_nmfp.zip",
    ]
    download_archives(urls, NMFP_SOURCE_DIR)

def download_formd_archives():
    os.makedirs(FORMD_SOURCE_DIR, exist_ok=True)
    BASE_URL = "https://www.sec.gov/files/structureddata/data/form-d-data-sets/"
    urls = [
        BASE_URL + "2008q1_d.zip",
        BASE_URL + "2008q2_d_0.zip",
        BASE_URL + "2008q3_d_0.zip",
        BASE_URL + "2008q4_d_0.zip",
        BASE_URL + "2009q1_d_0.zip",
        BASE_URL + "2009q2_d_0.zip",
        BASE_URL + "2009q3_d_0.zip",
        BASE_URL + "2009q4_d_0.zip",
        BASE_URL + "2010q1_d_0.zip",
        BASE_URL + "2010q2_d_0.zip",
        BASE_URL + "2010q3_d_0.zip",
        BASE_URL + "2010q4_d_0.zip",
        BASE_URL + "2011q1_d_0.zip",
        BASE_URL + "2011q2_d_0.zip",
        BASE_URL + "2011q3_d_0.zip",
        BASE_URL + "2011q4_d_0.zip",
        BASE_URL + "2012q1_d.zip",
        BASE_URL + "2012q2_d.zip",
        BASE_URL + "2012q3_d.zip",
        BASE_URL + "2012q4_d.zip",
        BASE_URL + "2013q1_d.zip",
        BASE_URL + "2013q2_d.zip",
        BASE_URL + "2013q3_d.zip",
        BASE_URL + "2013q4_d.zip",
        BASE_URL + "2014q1_d.zip",
        BASE_URL + "2014q2_d.zip",
        BASE_URL + "2014q3_d.zip",
        BASE_URL + "2014q4_d.zip",
        BASE_URL + "2015q1_d.zip",
        BASE_URL + "2015q2_d.zip",
        BASE_URL + "2015q3_d.zip",
        BASE_URL + "2015q4_d.zip",
        BASE_URL + "2016q1_d.zip",
        BASE_URL + "2016q2_d.zip",
        BASE_URL + "2016q3_d.zip",
        BASE_URL + "2016q4_d.zip",
        BASE_URL + "2017q1_d.zip",
        BASE_URL + "2017q2_d.zip",
        BASE_URL + "2017q3_d.zip",
        BASE_URL + "2017q4_d.zip",
        BASE_URL + "2018q1_d.zip",
        BASE_URL + "2018q2_d.zip",
        BASE_URL + "2018q3_d.zip",
        BASE_URL + "2018q4_d.zip",
        BASE_URL + "2019q1_d.zip",
        BASE_URL + "2019q2_d.zip",
        BASE_URL + "2019q3_d.zip",
        BASE_URL + "2019q4_d.zip",
        BASE_URL + "2020q1_d.zip",
        BASE_URL + "2020q2_d.zip",
        BASE_URL + "2020q3_d.zip",
        BASE_URL + "2020q4_d.zip",
        BASE_URL + "2021q1_d.zip",
        BASE_URL + "2021q2_d.zip",
        BASE_URL + "2021q3_d.zip",
        BASE_URL + "2021q4_d.zip",
        BASE_URL + "2022q1_d.zip",
        BASE_URL + "2022q2_d.zip",
        BASE_URL + "2022q3_d.zip",
        BASE_URL + "2022q4_d.zip",
        BASE_URL + "2023q1_d.zip",
        BASE_URL + "2023q2_d.zip",
        BASE_URL + "2023q3_d.zip",
        BASE_URL + "2023q4_d.zip",
        BASE_URL + "2024q1_d.zip",
        BASE_URL + "2024q2_d.zip",
        BASE_URL + "2024q3_d.zip",
    ]
    download_archives(urls, FORMD_SOURCE_DIR)
