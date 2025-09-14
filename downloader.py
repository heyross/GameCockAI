import logging
import os
import requests
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress
from config import SEC_USER_AGENT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_file(url, destination_folder, company_identifier=None, retries=3, rate_limit_delay=0):
    """Downloads a file from a URL with retries and intelligent error handling."""
    if company_identifier:
        destination_folder = os.path.join(destination_folder, str(company_identifier))
    
    os.makedirs(destination_folder, exist_ok=True)
    filename = url.split('/')[-1]
    filepath = os.path.join(destination_folder, filename)

    headers = {
        'User-Agent': SEC_USER_AGENT
    }

    if os.path.exists(filepath):
        logging.info(f"Skipping download of {filename} as it already exists.")
        return True

    for attempt in range(retries):
        try:
            logging.info(f"Attempting to download: {filename} (Attempt {attempt + 1}/{retries})")
            with requests.get(url, stream=True, timeout=30, headers=headers) as req:
                # Treat 404 and 500 errors as 'file not found' and don't retry
                if req.status_code in [404, 500]:
                    logging.info(f"File not found on server (status {req.status_code}): {filename}")
                    return False
                
                req.raise_for_status() # Raise an exception for other bad status codes

                with open(filepath, 'wb') as f:
                    for chunk in req.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logging.info(f"Successfully downloaded: {filename}")
                if rate_limit_delay > 0:
                    time.sleep(rate_limit_delay)
                return True

        except requests.exceptions.RequestException as e:
            logging.warning(f"Download failed for {filename}: {e}. Retrying...")
            time.sleep(2 ** attempt) # Exponential backoff

    logging.error(f"Failed to download {filename} after {retries} attempts.")
    return False

def download_archives(urls, destination_folder, max_workers=16, rate_limit_delay=0):
    """Downloads a list of archives from URLs in parallel."""
    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading archives...", total=len(urls))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Use keyword arguments to avoid positional argument confusion
            futures = {executor.submit(
                download_file, 
                url=url, 
                destination_folder=destination_folder, 
                rate_limit_delay=rate_limit_delay
            ): url for url in urls}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error processing {futures[future]}: {e}")
                progress.update(task, advance=1)
