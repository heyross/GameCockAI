"""
Processor for 10-K and 10-Q SEC filings.

This module provides functionality to download, parse, and process 10-K and 10-Q filings
from the SEC EDGAR database. It extracts structured data, financial statements,
and other relevant information from these filings.
"""

# Standard library imports
import json
import os
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Third-party imports
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

# Add parent directory to path for local imports
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Local application imports
try:
    from GameCockAI.config import DATA_DIR, EDGAR_BASE_URL, SEC_API_KEY
    from GameCockAI.database import (
        Sec10KDocument, Sec10KExhibits, Sec10KFinancials, Sec10KMetadata,
        Sec10KSubmission, SessionLocal
    )
    from GameCockAI.src.logging_utils import get_processor_logger
    logger = get_processor_logger('processor_10k')
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('processor_10k')
    logger.warning('Failed to import some modules: %s', e)
except ImportError:
    # Fallback for direct execution
    from src.logging_utils import get_processor_logger
    from database import SessionLocal, Sec10KSubmission, Sec10KDocument, Sec10KFinancials, Sec10KExhibits, Sec10KMetadata
    from config import EDGAR_BASE_URL, SEC_API_KEY, DATA_DIR

# Initialize logger
logger = get_processor_logger('processor_10k')

# Constants
SEC_FORMS = ['10-K', '10-Q', '10-K/A', '10-Q/A']
XBRL_EXTENSIONS = ['.xsd', '.xml', '_cal.xml', '_def.xml', '_lab.xml', '_pre.xml']

class SEC10KProcessor:
    """Processor for 10-K and 10-Q SEC filings."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the SEC 10-K/10-Q processor.
        
        Args:
            db_session: Optional SQLAlchemy session. If not provided, a new one will be created.
        """
        self.db = db_session if db_session else SessionLocal()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GameCockAI/1.0 (your-email@example.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
        
        # Create data directories if they don't exist
        self.raw_dir = os.path.join(DATA_DIR, 'sec', '10k', 'raw')
        self.processed_dir = os.path.join(DATA_DIR, 'sec', '10k', 'processed')
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def download_filing(self, accession_number: str, cik: str, form_type: str, force: bool = False) -> Optional[str]:
        """Download a 10-K/10-Q filing from SEC EDGAR.
        
        Args:
            accession_number: The SEC accession number (e.g., '0000320193-20-000096')
            cik: The company's CIK number
            form_type: The form type (e.g., '10-K', '10-Q')
            force: If True, force re-download even if file exists
            
        Returns:
            Path to the downloaded file, or None if download failed
        """
        # Convert CIK to 10-digit string with leading zeros
        cik = str(cik).zfill(10)
        
        # Parse the accession number to get the filing path
        # Format: 0000320193-20-000096 -> 0000320193/20-000096
        acc_parts = accession_number.split('-')
        if len(acc_parts) < 3:
            logger.error(f"Invalid accession number format: {accession_number}")
            return None
            
        filing_path = f"{acc_parts[0]}/{'-'.join(acc_parts[1:])}"
        
        # Create company directory
        company_dir = os.path.join(self.raw_dir, cik)
        os.makedirs(company_dir, exist_ok=True)
        
        # Check if we already have this filing
        output_file = os.path.join(company_dir, f"{accession_number}.txt")
        if os.path.exists(output_file) and not force:
            logger.info(f"Filing {accession_number} already exists, skipping download")
            return output_file
        
        # Build the filing URL
        filing_url = f"{EDGAR_BASE_URL}/Archives/edgar/data/{cik}/{filing_path.replace('-', '')}/{accession_number}.txt"
        
        try:
            logger.info(f"Downloading {form_type} filing: {filing_url}")
            response = self.session.get(filing_url, timeout=30)
            response.raise_for_status()
            
            # Save the filing
            with open(output_file, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"Saved {form_type} filing to {output_file}")
            return output_file
            
        except requests.RequestException as e:
            logger.error(f"Error downloading filing {accession_number}: {e}")
            return None
    
    def extract_filing_metadata(self, filing_path: str) -> Dict:
        """Extract metadata from a 10-K/10-Q filing.
        
        Args:
            filing_path: Path to the filing text file
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            'accession_number': None,
            'form_type': None,
            'filing_date': None,
            'period_of_report': None,
            'company_name': None,
            'cik': None,
            'file_number': None,
            'sec_act': None,
            'film_number': None,
            'is_xbrl': False,
            'is_inline_xbrl': False,
            'primary_document': None,
            'size': None
        }
        
        try:
            # Get file size
            metadata['size'] = os.path.getsize(filing_path)
            
            # Read the first 10KB to find the header
            with open(filing_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10240)
                
            # Extract SEC header information
            header_pattern = re.compile(
                r'<SEC-HEADER>(.*?)</SEC-HEADER>', 
                re.DOTALL | re.IGNORECASE
            )
            
            header_match = header_pattern.search(content)
            if header_match:
                header = header_match.group(1)
                
                # Extract form type - try both formats
                form_match = re.search(r'<TYPE>(10-[KQ](?:/A)?)', header, re.IGNORECASE)
                if not form_match:
                    form_match = re.search(r'<FORM>(10-[KQ](?:/A)?)', header, re.IGNORECASE)
                if form_match:
                    metadata['form_type'] = form_match.group(1).upper()
                
                # Extract filing date
                date_match = re.search(r'<FILING-DATE>(\d{4}-\d{2}-\d{2})', header)
                if date_match:
                    metadata['filing_date'] = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                
                # Extract company info
                company_match = re.search(
                    r'<COMPANY-CONFORMED-NAME>([^<]+)', 
                    header, 
                    re.IGNORECASE
                )
                if company_match:
                    metadata['company_name'] = company_match.group(1).strip()
                
                # Extract CIK
                cik_match = re.search(r'<CIK>(\d+)', header, re.IGNORECASE)
                if cik_match:
                    metadata['cik'] = cik_match.group(1).zfill(10)
                
                # Extract file number
                file_num_match = re.search(r'<FILENUMBER>(\d+-\d+)', header, re.IGNORECASE)
                if file_num_match:
                    metadata['file_number'] = file_num_match.group(1)
                
                # Extract SEC Act
                sec_act_match = re.search(r'<SEC-ACT>(\d+)', header, re.IGNORECASE)
                if sec_act_match:
                    metadata['sec_act'] = sec_act_match.group(1)
                
                # Extract film number
                film_match = re.search(r'<FILM-NUMBER>(\d+)', header, re.IGNORECASE)
                if film_match:
                    metadata['film_number'] = film_match.group(1)
                
                # Check for XBRL/Inline XBRL
                metadata['is_xbrl'] = '<XBRL>' in content or any(ext in content for ext in XBRL_EXTENSIONS)
                metadata['is_inline_xbrl'] = '<IX:HTML' in content or 'xmlns:ix=' in content
                
                # Extract primary document
                doc_match = re.search(r'<FILENAME>(.*?\.(?:txt|htm|html))', header, re.IGNORECASE)
                if doc_match:
                    metadata['primary_document'] = doc_match.group(1)
            
            # Extract period of report from the document
            with open(filing_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(50000)  # Read first 50KB for performance
                
                # Try to find period of report in the header first
                period_match = None
                
                # Look for period of report in the header first (format: <PERIOD-OF-REPORT>YYYY-MM-DD</PERIOD-OF-REPORT>)
                period_match = re.search(
                    r'<PERIOD-OF-REPORT>(\d{4})-(\d{2})-(\d{2})</PERIOD-OF-REPORT>',
                    content,
                    re.IGNORECASE
                )
                
                if not period_match:
                    # Try alternative format: <PERIOD>YYYYMMDD
                    period_match = re.search(
                        r'<PERIOD>(\d{4})(\d{2})(\d{2})',
                        content,
                        re.IGNORECASE
                    )
                
                if period_match:
                    try:
                        year = int(period_match.group(1))
                        month = int(period_match.group(2))
                        day = int(period_match.group(3))
                        metadata['period_of_report'] = datetime(year, month, day)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing period from header: {e}")
                
                # If still not found, try to find in document text
                if 'period_of_report' not in metadata:
                    period_match = re.search(
                        r'(?:fiscal year|period|as of|for the (?:year|quarter|period) ended|ended|through|thru|as of the end of)'
                        r'[\s\-:]*'  # Optional separator
                        r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'  # Month
                        r'[\s,]*'  # Optional separator
                        r'(\d{1,2})(?:st|nd|rd|th)?'  # Day
                        r'(?:\s*[,\s-]\s*|\s+)'  # Separator
                        r'(\d{4})\b',  # Year
                        content,
                        re.IGNORECASE
                    )
                    
                    if period_match:
                        try:
                            month = period_match.group(1)[:3].title()
                            day = period_match.group(2).zfill(2)
                            year = period_match.group(3)
                            date_str = f"{month} {day} {year}"
                            metadata['period_of_report'] = datetime.strptime(date_str, '%b %d %Y')
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error parsing period of report from text: {e}")
                
                # If still not found, try to extract from filename or other metadata
                if 'period_of_report' not in metadata and 'filing_date' in metadata:
                    # Default to the last day of the fiscal year if we have a filing date
                    metadata['period_of_report'] = datetime(
                        metadata['filing_date'].year,
                        12,  # December
                        31   # Last day of year
                    )
            
            # Extract accession number from filename if not found in header
            if not metadata.get('accession_number'):
                base_name = os.path.basename(filing_path)
                if base_name.endswith('.txt'):
                    metadata['accession_number'] = base_name[:-4]
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {filing_path}: {e}")
            return metadata
    
    def parse_filing_sections(self, filing_path: str) -> List[Dict]:
        """Parse a 10-K/10-Q filing into sections.
        
        Args:
            filing_path: Path to the filing text file
            
        Returns:
            List of dictionaries containing section data
        """
        sections = []
        
        try:
            with open(filing_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract the main document (skip SEC header)
            doc_start = content.find('<DOCUMENT>')
            doc_end = content.rfind('</DOCUMENT>')
            
            if doc_start >= 0 and doc_end > doc_start:
                doc_content = content[doc_start:doc_end + 11]  # +11 for '</DOCUMENT>'
            else:
                doc_content = content
            
            # Parse HTML content
            soup = BeautifulSoup(doc_content, 'html.parser')
            
            # Remove scripts, styles, and other non-content elements
            for element in soup(['script', 'style', 'noscript', 'meta', 'link', 'button', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Common section patterns for 10-K/10-Q
            section_patterns = {
                'business': r'(?i)(?:item\s*1\.?\s*[\n\s]*|)(business|description of business|business\s*overview)',
                'risk_factors': r'(?i)(?:item\s*1a\.?\s*[\n\s]*|)(risk\s*factors)',
                'properties': r'(?i)(?:item\s*2\.?\s*[\n\s]*|)(properties|description of properties)',
                'legal_proceedings': r'(?i)(?:item\s*3\.?\s*[\n\s]*|)(legal\s*proceedings)',
                'mine_safety': r'(?i)(?:item\s*4\.?\s*[\n\s]*|)(mine\s*safety\s*disclosures?)',
                'mdna': r'(?i)(?:item\s*7\.?\s*[\n\s]*|)(management[\'\s]s\s*discussion\s*and\s*analysis|md&a)',
                'market_risk': r'(?i)(?:item\s*7a\.?\s*[\n\s]*|)(quantitative\s*and\s*qualitative\s*disclosures?\s*about\s*market\s*risk)',
                'financial_statements': r'(?i)(?:item\s*8\.?\s*[\n\s]*|)(financial\s*statements?\s*and\s*supplementary\s*data)',
                'controls': r'(?i)(?:item\s*9a\.?\s*[\n\s]*|)(controls\s*and\s*procedures)',
                'accounting': r'(?i)(?:item\s*9\.?\s*[\n\s]*|)(changes\s*in\s*and\s*disagreements\s*with\s*accountants\s*on\s*accounting\s*and\s*financial\s*disclosure)',
            }
            
            # Find all section headers
            text = soup.get_text('\n', strip=True)
            
            for section_id, pattern in section_patterns.items():
                match = re.search(pattern, text)
                if match:
                    start_pos = match.start()
                    
                    # Find the end of this section (start of next section or end of document)
                    end_pos = len(text)
                    for other_id, other_pattern in section_patterns.items():
                        if other_id != section_id:
                            other_match = re.search(other_pattern, text[start_pos+1:])
                            if other_match and other_match.start() < (end_pos - start_pos):
                                end_pos = start_pos + other_match.start()
                    
                    # Extract section content
                    section_content = text[start_pos:end_pos].strip()
                    word_count = len(section_content.split())
                    
                    sections.append({
                        'section': section_id,
                        'title': match.group(1) if match.groups() else section_id,
                        'content': section_content,
                        'word_count': word_count,
                        'sequence': len(sections) + 1
                    })
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing filing sections from {filing_path}: {e}")
            return []
    
    def extract_financial_data(self, filing_path: str) -> List[Dict]:
        """Extract financial data from a 10-K/10-Q filing.
        
        Args:
            filing_path: Path to the filing text file
            
        Returns:
            List of dictionaries containing financial data
        """
        financials = []
        
        try:
            with open(filing_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # This is a simplified example - in practice, you'd use XBRL parsing for structured data
            # and more sophisticated text extraction for unstructured data
            
            # First, try to extract the period end date from the content
            period_end = None
            period_match = re.search(
                r'(?:for\s*the\s*\w*\s*(?:quarter|period|year)\s*ended|as\s*of|on)\s*'  # Prefix
                r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'  # Month
                r'\s+(\d{1,2})(?:st|nd|rd|th)?'  # Day
                r'(?:\s*,\s*|\s+)'  # Separator
                r'(\d{4})\b',  # Year
                content,
                re.IGNORECASE
            )
            
            if period_match:
                try:
                    month = period_match.group(1)[:3].title()
                    day = period_match.group(2).zfill(2)
                    year = period_match.group(3)
                    period_end = datetime.strptime(f"{month} {day} {year}", '%b %d %Y')
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing period end date: {e}")
            
            # If we couldn't parse a date, use the current date as a fallback
            if period_end is None:
                period_end = datetime.now()
                logger.warning(f"Using current date as fallback for period end: {period_end}")
            
            # Example: Extract basic financial metrics using regex patterns
            patterns = {
                'revenue': r'(?:total\s*revenue|net\s*sales|sales|revenue\s*from\s*operations)[^$\d]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                'net_income': r'(?:net\s*income|net\s*earnings|net\s*loss)[^$\d]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                'total_assets': r'total\s*assets[^$\d]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                'total_liabilities': r'total\s*liabilities[^$\d]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
                'eps_basic': r'(?:basic\s*earnings\s*per\s*share|basic\s*eps|earnings\s*per\s*share)[^$\d]*\$?\s*(\d+\.\d+)',
                'eps_diluted': r'(?:diluted\s*earnings\s*per\s*share|diluted\s*eps)[^$\d]*\$?\s*(\d+\.\d+)',
            }
            
            
            # Determine period length based on form type
            form_type = None
            form_match = re.search(r'<TYPE>(10-[KQ](?:/A)?)', content, re.IGNORECASE)
            if form_match:
                form_type = form_match.group(1).upper()
            
            period_length = 'FY' if form_type == '10-K' else 'Q1'  # Default to Q1, should be determined from filing
            
            # Extract metrics using patterns
            for metric, pattern in patterns.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for i, match in enumerate(matches):
                    try:
                        value_str = match.group(1).replace(',', '')
                        value = float(value_str)
                        financials.append({
                            'metric_name': metric,
                            'metric_value': value,
                            'metric_unit': 'USD',
                            'is_restated': False,
                            'period_end': period_end,
                            'period_length': 'FY' if '10-K' in str(filing_path).upper() else 'Q1',
                            'statement_type': 'income' if 'revenue' in metric or 'income' in metric or 'earnings' in metric else 'balance',
                        })
                    except (ValueError, AttributeError) as e:
                        logger.debug(f"Could not parse value for {metric}: {e}")
            
            return financials
            
        except Exception as e:
            logger.error(f"Error extracting financial data from {filing_path}: {e}")
            return []
    
    def save_to_database(self, metadata: Dict, sections: List[Dict], financials: List[Dict]) -> bool:
        """Save extracted data to the database.
        
        Args:
            metadata: Dictionary containing filing metadata
            sections: List of document sections
            financials: List of financial data points
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create or update submission record
            submission = Sec10KSubmission(
                accession_number=metadata['accession_number'],
                cik=metadata['cik'],
                company_name=metadata['company_name'],
                form_type=metadata['form_type'],
                filing_date=metadata['filing_date'],
                period_of_report=metadata['period_of_report'],
                acceptance_datetime=metadata.get('acceptance_datetime'),
                file_number=metadata.get('file_number'),
                sec_act=metadata.get('sec_act'),
                film_number=metadata.get('film_number'),
                is_xbrl=metadata.get('is_xbrl', False),
                is_inline_xbrl=metadata.get('is_inline_xbrl', False),
                primary_document=metadata.get('primary_document'),
                size=metadata.get('size')
            )
            
            # Add to session and commit to get the ID
            self.db.merge(submission)
            self.db.commit()
            
            # Save document sections
            for section in sections:
                doc = Sec10KDocument(
                    accession_number=metadata['accession_number'],
                    section=section['section'],
                    sequence=section.get('sequence', 0),
                    content=section['content'][:10000000],  # Limit to 10MB
                    word_count=section.get('word_count', 0)
                )
                self.db.merge(doc)
            
            # Save financial data
            for fin in financials:
                fin_data = Sec10KFinancials(
                    accession_number=metadata['accession_number'],
                    statement_type=fin.get('statement_type', 'unknown'),
                    period_end=fin.get('period_end'),
                    period_length=fin.get('period_length'),
                    metric_name=fin['metric_name'],
                    metric_value=fin.get('metric_value'),
                    metric_unit=fin.get('metric_unit'),
                    is_restated=fin.get('is_restated', False)
                )
                self.db.merge(fin_data)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving to database: {e}")
            return False
    
    def process_filing(self, filing_path: str, force: bool = False) -> bool:
        """Process a single 10-K/10-Q filing.
        
        Args:
            filing_path: Path to the filing text file
            force: If True, reprocess even if already in database
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if already processed
            base_name = os.path.basename(filing_path)
            if base_name.endswith('.txt'):
                accession_number = base_name[:-4]
            else:
                accession_number = base_name
                
            if not force:
                existing = self.db.query(Sec10KSubmission).filter_by(accession_number=accession_number).first()
                if existing:
                    logger.info(f"Filing {accession_number} already processed, skipping")
                    return True
            
            # Extract metadata
            metadata = self.extract_filing_metadata(filing_path)
            if not metadata.get('accession_number'):
                metadata['accession_number'] = accession_number
            
            # Parse document sections
            sections = self.parse_filing_sections(filing_path)
            
            # Extract financial data
            financials = self.extract_financial_data(filing_path)
            
            # Save to database
            success = self.save_to_database(metadata, sections, financials)
            
            if success:
                logger.info(f"Successfully processed filing: {accession_number}")
            else:
                logger.error(f"Failed to process filing: {accession_number}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error processing filing {filing_path}: {e}")
            return False

def process_10k_filings(source_dir: str, force: bool = False) -> None:
    """Process all 10-K/10-Q filings in a directory.
    
    Args:
        source_dir: Directory containing 10-K/10-Q filings
        force: If True, reprocess even if already in database
    """
    processor = SEC10KProcessor()
    
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
    from src.logging_utils import get_processor_logger

    logger = get_processor_logger('processor_10k')
    
    parser = argparse.ArgumentParser(description='Process 10-K/10-Q SEC filings')
    parser.add_argument('source_dir', help='Directory containing 10-K/10-Q filings')
    parser.add_argument('--force', action='store_true', help='Reprocess even if already in database')
    
    args = parser.parse_args()
    process_10k_filings(args.source_dir, args.force)
