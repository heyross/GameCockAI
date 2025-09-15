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

from ..downloader import download_archives, download_file
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

def download_edgar_filings(target_companies=None, filing_types=None, years=None, max_files_per_company=50):
    """
    Download EDGAR filings for target companies
    
    Args:
        target_companies: List of company dictionaries with 'cik_str' key
        filing_types: List of filing types to download (e.g., ['8-K', '10-K', 'S-4'])
        years: List of years to download (e.g., [2023, 2024])
        max_files_per_company: Maximum number of files to download per company
    """
    os.makedirs(EDGAR_SOURCE_DIR, exist_ok=True)
    
    # Default filing types if none specified
    if filing_types is None:
        filing_types = ['8-K', '10-K', '10-Q', 'S-4', 'DEF 14A']
    
    # Default years if none specified
    if years is None:
        current_year = datetime.now().year
        years = [current_year - 1, current_year]
    
    # Default target companies if none specified
    if target_companies is None:
        # Load from company_data if available
        try:
            from company_data import TARGET_COMPANIES
            target_companies = TARGET_COMPANIES
        except ImportError:
            print("No target companies specified and cannot load from company_data")
            return
    
    if not target_companies:
        print("No target companies available for EDGAR download")
        return
    
    print(f"Downloading EDGAR filings for {len(target_companies)} companies")
    print(f"Filing types: {', '.join(filing_types)}")
    print(f"Years: {', '.join(map(str, years))}")
    
    headers = {
        'User-Agent': 'GameCock AI Financial Analysis Tool contact@example.com',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    downloaded_count = 0
    error_count = 0
    
    for company in target_companies:
        cik = company.get('cik_str')
        company_name = company.get('title', 'Unknown')
        
        if not cik:
            print(f"Skipping {company_name} - no CIK available")
            continue
            
        print(f"\nProcessing {company_name} (CIK: {cik})")
        
        # Create company directory
        company_dir = os.path.join(EDGAR_SOURCE_DIR, cik)
        os.makedirs(company_dir, exist_ok=True)
        
        # Download filings for each year
        for year in years:
            for filing_type in filing_types:
                try:
                    filings = get_company_filings(cik, filing_type, year, headers)
                    
                    if not filings:
                        continue
                    
                    # Limit number of files per company
                    filings = filings[:max_files_per_company]
                    
                    for filing in filings:
                        if download_filing_document(filing, company_dir, headers):
                            downloaded_count += 1
                        else:
                            error_count += 1
                            
                        # Rate limiting
                        time.sleep(0.1)
                        
                except Exception as e:
                    print(f"Error processing {company_name} {filing_type} {year}: {e}")
                    error_count += 1
                    continue
    
    print(f"\nEDGAR download complete:")
    print(f"  Downloaded: {downloaded_count} files")
    print(f"  Errors: {error_count} files")
    print(f"  Files saved to: {EDGAR_SOURCE_DIR}")

def get_company_filings(cik, filing_type, year, headers):
    """
    Get list of filings for a company from SEC API
    """
    try:
        # SEC API endpoint for company filings
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
        
        # Try to get company facts first (this gives us filing information)
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            # Fallback to EDGAR search API
            return get_filings_from_edgar_search(cik, filing_type, year, headers)
        
        response.raise_for_status()
        data = response.json()
        
        # Extract filing information from company facts
        filings = []
        if 'facts' in data and 'dei' in data['facts']:
            # This is a simplified approach - in practice you'd need to parse the full structure
            pass
        
        # Fallback to EDGAR search
        return get_filings_from_edgar_search(cik, filing_type, year, headers)
        
    except Exception as e:
        print(f"Error getting filings for CIK {cik}: {e}")
        return []

def get_filings_from_edgar_search(cik, filing_type, year, headers):
    """
    Get filings using EDGAR search API
    """
    try:
        # EDGAR search API
        search_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': filing_type,
            'dateb': f'{year}1231',  # End date
            'datea': f'{year}0101',  # Start date
            'count': '100',
            'output': 'atom'
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        filings = []
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            try:
                title = entry.find('.//{http://www.w3.org/2005/Atom}title')
                link = entry.find('.//{http://www.w3.org/2005/Atom}link[@type="text/html"]')
                
                if title is not None and link is not None:
                    # Extract additional information for unique filenames
                    filing_date = 'unknown_date'
                    accession_number = 'unknown_accession'
                    
                    # Try to extract filing date from the link URL
                    href = link.get('href', '')
                    if '/Archives/edgar/data/' in href:
                        # Extract accession number from URL like: /Archives/edgar/data/1234567/0001234567-23-000001/
                        parts = href.split('/')
                        for part in parts:
                            if part and '-' in part and len(part) > 10:
                                accession_number = part
                                # Extract date from accession number (format: 0001234567-23-000001)
                                if '-' in part:
                                    date_part = part.split('-')[1]  # Get the year part
                                    if len(date_part) == 2:
                                        filing_date = f"20{date_part}"  # Convert YY to YYYY
                                break
                    
                    filing_info = {
                        'title': title.text,
                        'url': link.get('href'),
                        'filing_type': filing_type,
                        'year': year,
                        'filing_date': filing_date,
                        'accession_number': accession_number
                    }
                    filings.append(filing_info)
                    
            except Exception as e:
                continue
        
        return filings
        
    except Exception as e:
        print(f"Error searching EDGAR for CIK {cik}: {e}")
        return []

def download_filing_document(filing_info, company_dir, headers):
    """
    Download a specific filing document
    """
    try:
        filing_url = filing_info['url']
        
        # Get the filing page to find the actual document URL
        response = requests.get(filing_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML to find document links
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for document links (usually .txt files)
        doc_links = soup.find_all('a', href=True)
        document_urls = []
        
        for link in doc_links:
            href = link.get('href')
            if href and (href.endswith('.txt') or 'document' in href.lower()):
                if href.startswith('/'):
                    href = f"https://www.sec.gov{href}"
                document_urls.append(href)
        
        if not document_urls:
            print(f"No documents found for {filing_info['title']}")
            return False
        
        # Download the first document (usually the main filing)
        doc_url = document_urls[0]
        doc_response = requests.get(doc_url, headers=headers, timeout=30)
        doc_response.raise_for_status()
        
        # Create unique filename to prevent overwrites
        safe_title = "".join(c for c in filing_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Include filing date and accession number for uniqueness
        filing_date = filing_info.get('filing_date', 'unknown_date')
        accession = filing_info.get('accession_number', 'unknown_accession')
        
        # Create a unique filename
        if accession != 'unknown_accession':
            # Use accession number for uniqueness
            filename = f"{filing_info['year']}_{filing_info['filing_type']}_{filing_date}_{accession}_{safe_title}.txt"
        else:
            # Fallback to timestamp if no accession number
            import time
            timestamp = int(time.time() * 1000)  # milliseconds
            filename = f"{filing_info['year']}_{filing_info['filing_type']}_{filing_date}_{timestamp}_{safe_title}.txt"
        
        filepath = os.path.join(company_dir, filename)
        
        # Check if file already exists to prevent overwrites
        if os.path.exists(filepath):
            print(f"  Skipping: {filename} (already exists)")
            return True
        
        # Save the document
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(doc_response.text)
        
        print(f"  Downloaded: {filename}")
        return True
        
    except Exception as e:
        print(f"  Error downloading {filing_info.get('title', 'unknown')}: {e}")
        return False

def allyourbasearebelongtous():
    """
    Legacy function name - now calls the new EDGAR download system
    """
    print("Downloading EDGAR filings using new system...")
    download_edgar_filings()

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
