"""
Processor for 8-K SEC filings.

This module provides functionality to download, parse, and process 8-K filings
from the SEC EDGAR database. It extracts structured data and other relevant information from these filings.
"""

import os
import re
import json
import logging
import zipfile
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from database import SessionLocal, Sec8KSubmission, Sec8KItem
from config import EDGAR_BASE_URL, SEC_API_KEY, DATA_DIR

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SEC_FORMS = ['8-K', '8-K/A']

class SEC8KProcessor:
    """Processor for 8-K SEC filings."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the SEC 8-K processor."""
        self.db = db_session if db_session else SessionLocal()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GameCockAI/1.0 (your-email@example.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
        self.raw_dir = os.path.join(DATA_DIR, 'sec', '8k', 'raw')
        self.processed_dir = os.path.join(DATA_DIR, 'sec', '8k', 'processed')
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'db'):
            self.db.close()

    def download_filing(self, accession_number: str, cik: str, form_type: str, force: bool = False) -> Optional[str]:
        """Download an 8-K filing from SEC EDGAR."""
        cik = str(cik).zfill(10)
        acc_parts = accession_number.split('-')
        if len(acc_parts) < 3:
            logger.error(f"Invalid accession number format: {accession_number}")
            return None
        filing_path_part = f"{''.join(acc_parts[:-1])}"
        url = f"{EDGAR_BASE_URL}/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{accession_number}.txt"
        
        company_dir = os.path.join(self.raw_dir, cik)
        os.makedirs(company_dir, exist_ok=True)
        output_file = os.path.join(company_dir, f"{accession_number}.txt")

        if os.path.exists(output_file) and not force:
            logger.info(f"Filing {accession_number} already exists.")
            return output_file

        try:
            logger.info(f"Downloading {form_type} filing from {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            with open(output_file, 'wb') as f:
                f.write(response.content)
            logger.info(f"Saved filing to {output_file}")
            return output_file
        except requests.RequestException as e:
            logger.error(f"Error downloading filing {accession_number}: {e}")
            return None

    def extract_filing_metadata(self, filing_path: str) -> Dict:
        """Extract metadata from an 8-K filing."""
        metadata = {}
        try:
            with open(filing_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(20480) # Read first 20KB for header

            header_match = re.search(r'<SEC-HEADER>(.*?)</SEC-HEADER>', content, re.DOTALL)
            if not header_match:
                logger.error("SEC header not found.")
                return metadata
            header = header_match.group(1)

            metadata['accession_number'] = os.path.basename(filing_path).replace('.txt', '')
            cik_match = re.search(r'<CIK>\s*(\d+)', header)
            if cik_match:
                metadata['cik'] = cik_match.group(1).strip()

            company_name_match = re.search(r'<COMPANY-CONFORMED-NAME>\s*([^<]*)', header)
            if company_name_match:
                metadata['company_name'] = company_name_match.group(1).strip()

            form_type_match = re.search(r'<TYPE>\s*([^<]*)', header)
            if form_type_match:
                metadata['form_type'] = form_type_match.group(1).strip()

            filing_date_match = re.search(r'<FILING-DATE>\s*(\d{4}-\d{2}-\d{2})', header)
            if filing_date_match:
                metadata['filing_date'] = datetime.strptime(filing_date_match.group(1).strip(), '%Y-%m-%d')

            period_of_report_match = re.search(r'<PERIOD>\s*(\d+)', header)
            if period_of_report_match:
                metadata['period_of_report'] = datetime.strptime(period_of_report_match.group(1).strip(), '%Y%m%d')

            items_match = re.search(r'<ITEMS>\s*([^<]*)', header)
            if items_match:
                metadata['items'] = items_match.group(1).strip()

            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {filing_path}: {e}")
            return {}

    def parse_filing_items(self, filing_path: str) -> List[Dict]:
        """Parse an 8-K filing to extract all items."""
        items = []
        try:
            with open(filing_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Use regex to find all documents within the filing
            documents = re.findall(r'<DOCUMENT>(.*?)</DOCUMENT>', content, re.DOTALL)
            html_content = ""
            for doc in documents:
                doc_type = re.search(r'<TYPE>([^\n]+)', doc)
                if doc_type and '8-K' in doc_type.group(1):
                    text_match = re.search(r'<TEXT>(.*?)</TEXT>', doc, re.DOTALL)
                    if text_match:
                        html_content = text_match.group(1)
                        break
            
            if not html_content:
                return []

            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()

            # Regex to find all occurrences of 'Item X.XX'
            item_pattern = re.compile(r"(Item\s+\d+\.\d+.*)")
            found_items = item_pattern.finditer(text)

            item_positions = [(m.start(), m.group(1)) for m in found_items]
            if not item_positions:
                return []

            for i, (start, title) in enumerate(item_positions):
                end = item_positions[i + 1][0] if i + 1 < len(item_positions) else len(text)
                item_content = text[start:end].strip()
                item_number = title.split()[1]
                items.append({
                    'item_number': item_number,
                    'item_title': title,
                    'content': item_content
                })
            return items
        except Exception as e:
            logger.error(f"Error parsing items from {filing_path}: {e}")
            return []

    def save_to_database(self, metadata: Dict, items: List[Dict]) -> bool:
        """Save extracted 8-K data to the database."""
        required_fields = ['accession_number', 'cik', 'company_name', 'form_type', 'filing_date']
        if not metadata or not all(field in metadata and metadata[field] is not None for field in required_fields):
            logger.error(f"Missing one or more required metadata fields to save to DB: {metadata}")
            return False

        try:
            submission_data = {
                'accession_number': metadata.get('accession_number'),
                'cik': metadata.get('cik'),
                'company_name': metadata.get('company_name'),
                'form_type': metadata.get('form_type'),
                'filing_date': metadata.get('filing_date'),
                'period_of_report': metadata.get('period_of_report'),
                'items': metadata.get('items')
            }
            submission = Sec8KSubmission(**submission_data)
            self.db.merge(submission)

            for item_data in items:
                item = Sec8KItem(
                    accession_number=metadata['accession_number'],
                    **item_data
                )
                self.db.merge(item)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error for {metadata.get('accession_number')}: {e}")
            return False

    def process_filing(self, filing_path: str, force: bool = False) -> bool:
        """Process a single 8-K filing."""
        accession_number = os.path.basename(filing_path).replace('.txt', '')
        if not force and self.db.query(Sec8KSubmission).filter_by(accession_number=accession_number).first():
            logger.info(f"Filing {accession_number} already processed.")
            return True

        logger.info(f"Processing filing: {accession_number}")
        metadata = self.extract_filing_metadata(filing_path)
        if not metadata:
            logger.error(f"Failed to extract metadata for {accession_number}")
            return False
        
        items = self.parse_filing_items(filing_path)
        if not items:
            logger.warning(f"No items found for {accession_number}")

        if self.save_to_database(metadata, items):
            logger.info(f"Successfully processed and saved {accession_number}")
            return True
        else:
            logger.error(f"Failed to save {accession_number} to database.")
            return False

def process_8k_filings(source_dir: str, force: bool = False) -> None:
    """Process all 8-K filings in a directory.
    
    Args:
        source_dir: Directory containing 8-K filings
        force: If True, reprocess even if already in database
    """
    processor = SEC8KProcessor()
    
    # Find all .txt files in the source directory and subdirectories
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                processor.process_filing(file_path, force)
    
    # Clean up
    del processor

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process 8-K SEC filings')
    parser.add_argument('source_dir', help='Directory containing 8-K filings')
    parser.add_argument('--force', action='store_true', help='Reprocess even if already in database')
    
    args = parser.parse_args()
    process_8k_filings(args.source_dir, args.force)
