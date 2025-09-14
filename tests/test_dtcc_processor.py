"""
Tests for the DTCC data processor.
"""
import unittest
import os
import tempfile
import pandas as pd
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Add GameCockAI directory to path to allow imports from the main package
gamecock_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(gamecock_dir)
sys.path.append(gamecock_dir)  # Add GameCockAI/ to path
sys.path.append(root_dir)      # Add root/ to path for other dependencies

# Import the processor and models
from src.processor_dtcc import DTCCProcessor
# Import from the correct database module (GameCockAI/database.py)
from database import Base
from dtcc_models import DTCCOrganization, DTCCOptionTrade, DTCCInterestRateSwap, DTCCEquityOption

class TestDTCCProcessor(unittest.TestCase):
    """Test cases for the DTCC data processor."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and session."""
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        
        # Create all tables
        Base.metadata.create_all(cls.engine)
    
    def setUp(self):
        """Start a new transaction for each test."""
        self.session = self.Session()
        self.session.begin_nested()
        self.processor = DTCCProcessor(self.session)
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Roll back the transaction after each test."""
        self.session.rollback()
        self.session.close()
    
    def create_test_csv(self, data, filename):
        """Helper to create a test CSV file."""
        filepath = os.path.join(self.temp_dir, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        return filepath
    
    def test_process_option_trades(self):
        """Test processing of option trade data."""
        # Create test data
        test_data = [
            {
                'trade_id': 'OPT123456789',
                'execution_timestamp': '2023-01-01 10:00:00',
                'effective_date': '2023-01-03',
                'trade_status': 'NEW',
                'clearing_status': 'PENDING',
                'reporting_party_lei': 'TESTLEI12345678901234',
                'reporting_party_name': 'Test Bank A',
                'other_party_lei': 'TESTLEI98765432109876',
                'other_party_name': 'Test Fund B',
                'underlying_asset': 'AAPL',
                'option_type': 'CALL',
                'strike_price': 150.00,
                'strike_currency': 'USD',
                'expiration_date': '2023-06-30',
                'premium_amount': 5.50,
                'premium_currency': 'USD',
                'security_type': 'STOCK',
                'security_description': 'Apple Inc. Common Stock'
            }
        ]
        
        # Create test CSV file
        test_file = self.create_test_csv(test_data, 'test_options.csv')
        
        # Process the file
        result = self.processor.process_dtcc_file(
            file_path=test_file,
            file_type='OPTION_TRADE',
            source_entity='TEST_SOURCE'
        )
        
        # Verify results
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['records_processed'], 1)
        self.assertEqual(len(result['errors']), 0)
        
        # Verify data was loaded correctly
        trade = self.session.query(DTCCOptionTrade).filter_by(trade_id='OPT123456789').first()
        self.assertIsNotNone(trade)
        self.assertEqual(trade.underlying_asset, 'AAPL')
        self.assertEqual(trade.option_type, 'CALL')
        self.assertEqual(trade.strike_price, 150.00)
        
        # Verify organization was created
        org = self.session.query(DTCCOrganization).filter_by(lei='TESTLEI12345678901234').first()
        self.assertIsNotNone(org)
        self.assertEqual(org.name, 'Test Bank A')
        
        # Verify equity option details
        equity = self.session.query(DTCCEquityOption).filter_by(trade_id='OPT123456789').first()
        self.assertIsNotNone(equity)
        self.assertEqual(equity.security_type, 'STOCK')
    
    def test_process_interest_rate_swaps(self):
        """Test processing of interest rate swap data."""
        # Create test data
        test_data = [
            {
                'trade_id': 'SWAP987654321',
                'execution_timestamp': '2023-01-01 09:30:00',
                'effective_date': '2023-01-03',
                'termination_date': '2028-01-03',
                'notional_amount': 10000000.00,
                'notional_currency': 'USD',
                'trade_status': 'ACTIVE',
                'clearing_status': 'CLEARED',
                'reporting_party_lei': 'TESTLEI11223344556677',
                'reporting_party_name': 'Test Bank X',
                'other_party_lei': 'TESTLEI99887766554433',
                'other_party_name': 'Test Fund Y',
                'fixed_rate': 3.25,
                'floating_index': 'SOFR',
                'day_count_convention': 'ACT/360',
                'payment_frequency': 'QUARTERLY'
            }
        ]
        
        # Create test CSV file
        test_file = self.create_test_csv(test_data, 'test_swaps.csv')
        
        # Process the file
        result = self.processor.process_dtcc_file(
            file_path=test_file,
            file_type='INTEREST_RATE_SWAP',
            source_entity='TEST_SOURCE'
        )
        
        # Verify results
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['records_processed'], 1)
        self.assertEqual(len(result['errors']), 0)
        
        # Verify data was loaded correctly
        swap = self.session.query(DTCCInterestRateSwap).filter_by(trade_id='SWAP987654321').first()
        self.assertIsNotNone(swap)
        self.assertEqual(swap.notional_amount, 10000000.00)
        self.assertEqual(swap.fixed_rate, 3.25)
        self.assertEqual(swap.floating_index, 'SOFR')
        
        # Verify organization was created
        org = self.session.query(DTCCOrganization).filter_by(lei='TESTLEI11223344556677').first()
        self.assertIsNotNone(org)
        self.assertEqual(org.name, 'Test Bank X')
    
    def test_duplicate_trade_id(self):
        """Test that duplicate trade IDs from different sources don't conflict."""
        # First process a trade
        test_data1 = [
            {
                'trade_id': 'DUPLICATE123',
                'execution_timestamp': '2023-01-01 10:00:00',
                'effective_date': '2023-01-03',
                'reporting_party_lei': 'TESTLEI11111111111111',
                'other_party_lei': 'TESTLEI22222222222222',
                'underlying_asset': 'AAPL',
                'option_type': 'CALL',
                'strike_price': 150.00,
                'strike_currency': 'USD',
                'expiration_date': '2023-06-30'
            }
        ]
        
        # Create and process first file
        test_file1 = self.create_test_csv(test_data1, 'source1.csv')
        result1 = self.processor.process_dtcc_file(
            file_path=test_file1,
            file_type='OPTION_TRADE',
            source_entity='SOURCE_1'
        )
        
        # Process same trade ID from different source
        test_data2 = [
            {
                'trade_id': 'DUPLICATE123',  # Same trade ID
                'execution_timestamp': '2023-01-01 10:00:00',
                'effective_date': '2023-01-03',
                'reporting_party_lei': 'TESTLEI33333333333333',
                'other_party_lei': 'TESTLEI44444444444444',
                'underlying_asset': 'MSFT',  # Different details
                'option_type': 'PUT',
                'strike_price': 300.00,
                'strike_currency': 'USD',
                'expiration_date': '2023-12-31'
            }
        ]
        
        test_file2 = self.create_test_csv(test_data2, 'source2.csv')
        result2 = self.processor.process_dtcc_file(
            file_path=test_file2,
            file_type='OPTION_TRADE',
            source_entity='SOURCE_2'
        )
        
        # First record should be processed successfully
        self.assertEqual(result1['records_processed'], 1)
        
        # Second record should be processed as an update to the existing trade
        self.assertEqual(result2['records_processed'], 1)
        
        # Verify only one trade exists with this ID (the updated one)
        trades = self.session.query(DTCCOptionTrade).filter_by(trade_id='DUPLICATE123').all()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].underlying_asset, 'MSFT')  # Second trade's data should overwrite
        
        # Clean up
        for trade in trades:
            self.session.delete(trade)
        self.session.commit()

if __name__ == "__main__":
    unittest.main()
