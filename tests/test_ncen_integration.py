"""
Integration tests for N-CEN functionality.
"""

import unittest
import os

# Adjust path to import from the root directory and base test file
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_base import BaseIntegrationTest
from processor import process_ncen_data, process_sec_filings
from database import SessionLocal, NCENSubmission, NCENFundReportedInfo, get_db_stats

class TestNCENIntegration(BaseIntegrationTest):
    """Contains integration tests for N-CEN data processing."""

    def test_ncen_full_processing_pipeline(self):
        """Test the complete N-CEN processing pipeline in an isolated environment."""
        self.create_ncen_test_data()
        
        result = process_ncen_data(self.test_dir)
        
        # In an isolated test, only one ZIP file is processed.
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['errors'], 0)
        
        db = SessionLocal()
        try:
            submissions = db.query(NCENSubmission).count()
            self.assertEqual(submissions, 1)
            
            funds = db.query(NCENFundReportedInfo).all()
            etf_fund = next((f for f in funds if f.fund_name == 'Tech ETF'), None)
            self.assertIsNotNone(etf_fund)
            self.assertTrue(etf_fund.is_etf)
            self.assertFalse(etf_fund.is_money_market)
        finally:
            db.close()

    def test_process_sec_filings_for_ncen(self):
        """Test the generic process_sec_filings function for N-CEN data."""
        self.create_ncen_test_data()
        
        # The generic processor should correctly route to the N-CEN function.
        result = process_sec_filings('N-CEN', self.test_dir)
        
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['errors'], 0)

        db = SessionLocal()
        try:
            self.assertEqual(db.query(NCENSubmission).count(), 1)
        finally:
            db.close()

    def test_database_stats_for_ncen(self):
        """Verify that get_db_stats correctly reports counts for N-CEN tables."""
        self.create_ncen_test_data()
        process_ncen_data(self.test_dir)
        
        stats = get_db_stats()
        
        self.assertGreater(stats.get('ncen_submissions', 0), 0)
        self.assertGreater(stats.get('ncen_registrants', 0), 0)
        self.assertGreater(stats.get('ncen_fund_reported_info', 0), 0)

if __name__ == '__main__':
    unittest.main()
