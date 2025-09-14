import logging
import os
import requests
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

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

    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")
        return False

def download_archives(urls, destination_folder, max_workers=16, rate_limit_delay=0):
    """Downloads a list of archives from URLs in parallel."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_file, url, destination_folder, rate_limit_delay): url for url in urls}
        for future in tqdm(as_completed(futures), total=len(urls), desc="Downloading archives"):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error downloading {futures[future]}: {e}")
