import logging
import os
import requests
import time
import zipfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from config import FORMD_SOURCE_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_file(url, destination_folder, rate_limit_delay=0):
    """Downloads a file from a URL to a destination folder."""
    os.makedirs(destination_folder, exist_ok=True)
    filename = url.split('/')[-1]
    filepath = os.path.join(destination_folder, filename)

    if os.path.exists(filepath):
        logging.info(f"Skipping download of {filename} as it already exists.")
        return True

    try:
        logging.info(f"Attempting to download: {filename}")
        req = requests.get(url, stream=True)
        req.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in req.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logging.info(f"Successfully downloaded: {filename}")
        if rate_limit_delay > 0:
            time.sleep(rate_limit_delay)
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logging.warning(f"File not found (404): {filename} - skipping")
            return True  # Return True to continue processing other files
        else:
            logging.error(f"HTTP error {e.response.status_code} downloading {url}: {e}")
            return False
    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")
        return False

def download_archives(urls, destination_folder, max_workers=16, rate_limit_delay=0):
    """Downloads a list of archives from URLs in parallel."""
    successful_downloads = 0
    failed_downloads = 0
    skipped_downloads = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_file, url, destination_folder, rate_limit_delay): url for url in urls}
        for future in tqdm(as_completed(futures), total=len(urls), desc="Downloading archives"):
            try:
                result = future.result()
                if result:
                    successful_downloads += 1
                else:
                    failed_downloads += 1
            except Exception as e:
                logging.error(f"Error downloading {futures[future]}: {e}")
                failed_downloads += 1
    
    logging.info(f"Download summary: {successful_downloads} successful, {failed_downloads} failed, {skipped_downloads} skipped")
    return successful_downloads, failed_downloads

def extract_formd_filings(archive_path):
    """Extracts Form D filings from a quarterly archive.
    The quarterly archive contains TSV files directly, so we extract
    to a directory named after the quarter.
    """
    # Get the quarter name from the archive filename
    archive_name = os.path.basename(archive_path)
    quarter_name = os.path.splitext(archive_name)[0]  # e.g., "2024q3_d"
    
    # Create extraction directory for this quarter
    quarter_dir = os.path.join(FORMD_SOURCE_DIR, quarter_name)
    
    if os.path.exists(quarter_dir):
        logging.info(f"Directory {quarter_dir} already exists, skipping extraction.")
        return

    try:
        # Extract the quarterly archive directly to its own directory
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(quarter_dir)
            logging.info(f"Extracted {archive_path} to {quarter_dir}")

    except zipfile.BadZipFile:
        logging.error(f"Error: {archive_path} is not a valid zip file or is corrupted.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during extraction: {e}")
