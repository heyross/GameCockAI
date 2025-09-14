"""
Integration tests for N-CEN functionality.
"""

import unittest
import os

# Adjust path to import from the root directory and base test file
import sys
# Add GameCockAI directory to path to allow imports from the main package
gamecock_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(gamecock_dir)
sys.path.append(gamecock_dir)  # Add GameCockAI/ to path
sys.path.append(root_dir)      # Add root/ to path for other dependencies

from tests.test_base import BaseIntegrationTest
from processor import process_ncen_data, process_sec_filings
# Import from the correct database module (GameCockAI/database.py)
from database import SessionLocal, NCENSubmission, NCENFundReportedInfo, get_db_stats

class TestNCENIntegration(BaseIntegrationTest):
    """Contains integration tests for N-CEN data processing."""

    def test_ncen_full_processing_pipeline(self):
        """Test the complete N-CEN processing pipeline in an isolated environment."""
        self.create_ncen_test_data()
        
        db = SessionLocal()
        try:
            result = process_ncen_data(self.test_dir, db_session=db)
            
            # In an isolated test, only one ZIP file is processed.
            self.assertEqual(result['processed'], 1)
            self.assertEqual(result['errors'], 0)
            
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
        
        db = SessionLocal()
        try:
            # The generic processor should correctly route to the N-CEN function.
            result = process_sec_filings('N-CEN', self.test_dir, db_session=db)
            
            self.assertEqual(result['processed'], 1)
            self.assertEqual(result['errors'], 0)

            self.assertEqual(db.query(NCENSubmission).count(), 1)
        finally:
            db.close()

    def test_database_stats_for_ncen(self):
        """Verify that get_db_stats correctly reports counts for N-CEN tables."""
        self.create_ncen_test_data()
        db = SessionLocal()
        try:
            process_ncen_data(self.test_dir, db_session=db)
            stats = get_db_stats(db_session=db)
        finally:
            db.close()
        
        self.assertGreater(stats.get('ncen_submissions', 0), 0)
        self.assertGreater(stats.get('ncen_registrants', 0), 0)
        self.assertGreater(stats.get('ncen_fund_reported_info', 0), 0)

if __name__ == '__main__':
    unittest.main()
