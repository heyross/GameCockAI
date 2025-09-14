"""
Integration tests for N-PORT functionality.
"""

import unittest
import os
import zipfile
import pandas as pd

# Adjust path to import from the root directory and base test file
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_base import BaseIntegrationTest
from processor import process_nport_data, process_sec_filings
from database import SessionLocal, NPORTSubmission, NPORTHolding, get_db_stats

class TestNPORTIntegration(BaseIntegrationTest):
    """Contains integration tests for N-PORT data processing."""

    def test_nport_full_processing_pipeline(self):
        """Test the complete N-PORT processing pipeline in an isolated environment."""
        self.create_nport_test_data()
        
        result = process_nport_data(self.test_dir)
        
        # In an isolated test, only one ZIP file is processed.
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['errors'], 0)
        
        db = SessionLocal()
        try:
            holdings = db.query(NPORTHolding).all()
            self.assertEqual(len(holdings), 2)
            
            tesla_holding = next((h for h in holdings if h.issuer_name == 'Tesla Inc.'), None)
            self.assertIsNotNone(tesla_holding)
            self.assertTrue(tesla_holding.is_restricted_security)
        finally:
            db.close()

    def test_large_dataset_processing(self):
        """Test processing a larger N-PORT dataset to ensure scalability."""
        num_records = 1000
        holdings_data = {
            'ACCESSION_NUMBER': ['000987654-23-000001'] * num_records,
            'ISSUER_NAME': [f'Company {i}' for i in range(num_records)],
            'BALANCE_HELD': [str(1000 + i) for i in range(num_records)],
            'IS_RESTRICTED_SECURITY': ['Y' if i % 10 == 0 else 'N' for i in range(num_records)]
        }
        
        large_zip_path = os.path.join(self.test_dir, "large_nport.zip")
        with zipfile.ZipFile(large_zip_path, 'w') as zf:
            zf.writestr('HOLDING.tsv', pd.DataFrame(holdings_data).to_csv(sep='\t', index=False))

        result = process_nport_data(self.test_dir)
        
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['errors'], 0)
        
        db = SessionLocal()
        try:
            holdings_count = db.query(NPORTHolding).count()
            self.assertEqual(holdings_count, num_records)
            
            restricted_count = db.query(NPORTHolding).filter(NPORTHolding.is_restricted_security == True).count()
            self.assertEqual(restricted_count, num_records / 10)
        finally:
            db.close()

    def test_database_stats_for_nport(self):
        """Verify that get_db_stats correctly reports counts for N-PORT tables."""
        self.create_nport_test_data()
        process_nport_data(self.test_dir)
        
        stats = get_db_stats()
        
        self.assertGreater(stats.get('nport_submissions', 0), 0)
        self.assertGreater(stats.get('nport_holdings', 0), 0)

if __name__ == '__main__':
    unittest.main()
