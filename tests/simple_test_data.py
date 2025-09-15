"""Simple test data generator for enhanced SEC processing tests."""

import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Any

class SimpleTestDataGenerator:
    """Simple test data generator for SEC filings."""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def create_10k_test_file(self, cik: str, year: int) -> str:
        """Create a simple 10-K test file."""
        filing_date = datetime(year, 3, 15)
        accession_number = f"{cik}-{str(year)[2:]}-03150001"
        
        content = f"""
<SEC-HEADER>
ACCESSION NUMBER: {accession_number}
CONFORMED PERIOD OF REPORT: {year}1231
</SEC-HEADER>

<DOCUMENT>
<TYPE>10-K
<SEQUENCE>1

Item 1. Business
Test Company is a specialty retailer operating through multiple channels.

Item 1A. Risk Factors
Our business is subject to various risks and uncertainties.

Item 7. Management's Discussion and Analysis
Our financial results reflect ongoing business transformation.

Item 8. Financial Statements
Our consolidated financial statements are presented below.
</DOCUMENT>
        """
        
        file_path = os.path.join(self.temp_dir, f"{accession_number}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def create_8k_test_file(self, cik: str, year: int, month: int) -> str:
        """Create a simple 8-K test file."""
        filing_date = datetime(year, month, 15)
        accession_number = f"{cik}-{str(year)[2:]}-{month:02d}15001"
        
        content = f"""
<SEC-HEADER>
ACCESSION NUMBER: {accession_number}
CONFORMED PERIOD OF REPORT: {filing_date.strftime('%Y%m%d')}
</SEC-HEADER>

<DOCUMENT>
<TYPE>8-K
<SEQUENCE>1

Item 1.01 Entry into a Material Definitive Agreement
The Company entered into a new distribution agreement.

Item 2.02 Results of Operations and Financial Condition
The Company reported quarterly results showing improved performance.
</DOCUMENT>
        """
        
        file_path = os.path.join(self.temp_dir, f"{accession_number}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def create_multi_year_test_data(self, cik: str, years: List[int]) -> List[str]:
        """Create test data for multiple years."""
        files = []
        for year in years:
            files.append(self.create_10k_test_file(cik, year))
        return files
    
    def get_temp_directory(self) -> str:
        """Get temporary directory path."""
        return self.temp_dir
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
