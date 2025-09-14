"""
Comprehensive tests for N-CEN (Form N-CEN) data processing functionality.
"""

import unittest
import tempfile
import os
import zipfile
import pandas as pd
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the modules we're testing
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor import process_ncen_data, sanitize_column_names
from database import (NCENSubmission, NCENRegistrant, NCENFundReportedInfo, 
                     NCENAdviser, create_db_and_tables, SessionLocal)


class TestNCENProcessing(unittest.TestCase):
    """Test cases for N-CEN data processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_zip_path = os.path.join(self.test_dir, "test_ncen.zip")
        
        # Create sample N-CEN data
        self.sample_submission_data = {
            'ACCESSION_NUMBER': ['0001234567-23-000001', '0001234567-23-000002'],
            'SUBMISSION_TYPE': ['N-CEN', 'N-CEN'],
            'CIK': ['0001234567', '0001234567'],
            'FILING_DATE': ['2023-03-31', '2023-06-30'],
            'REPORT_ENDING_PERIOD': ['2023-03-31', '2023-06-30'],
            'IS_REPORT_PERIOD_LT_12MONTH': ['N', 'N'],
            'FILE_NUM': ['811-12345', '811-12345'],
            'REGISTRANT_SIGNED_NAME': ['John Doe', 'Jane Smith'],
            'DATE_SIGNED': ['2023-04-15', '2023-07-15'],
            'SIGNATURE': ['/s/ John Doe', '/s/ Jane Smith'],
            'TITLE': ['President', 'Chief Compliance Officer'],
            'IS_LEGAL_PROCEEDINGS': ['N', 'N'],
            'IS_PROVISION_FINANCIAL_SUPPORT': ['N', 'N']
        }
        
        self.sample_registrant_data = {
            'ACCESSION_NUMBER': ['0001234567-23-000001', '0001234567-23-000002'],
            'REGISTRANT_NAME': ['Test Fund Company', 'Test Fund Company'],
            'FILE_NUM': ['811-12345', '811-12345'],
            'CIK': ['0001234567', '0001234567'],
            'LEI': ['123456789012345678AB', '123456789012345678AB'],
            'ADDRESS1': ['123 Main St', '123 Main St'],
            'CITY': ['New York', 'New York'],
            'STATE': ['NY', 'NY'],
            'COUNTRY': ['US', 'US'],
            'ZIP': ['10001', '10001'],
            'PHONE': ['212-555-0123', '212-555-0123'],
            'IS_FIRST_FILING': ['Y', 'N'],
            'IS_LAST_FILING': ['N', 'N'],
            'INVESTMENT_COMPANY_TYPE': ['Open-End Fund', 'Open-End Fund'],
            'TOTAL_SERIES': ['5', '5']
        }
        
        self.sample_fund_data = {
            'FUND_ID': ['F001', 'F002'],
            'ACCESSION_NUMBER': ['0001234567-23-000001', '0001234567-23-000001'],
            'FUND_NAME': ['Growth Fund', 'Value Fund'],
            'SERIES_ID': ['S001', 'S002'],
            'LEI': ['123456789012345678CD', '123456789012345678EF'],
            'IS_FIRST_FILING': ['Y', 'Y'],
            'AUTHORIZED_SHARES_CNT': ['1000000', '2000000'],
            'IS_ETF': ['N', 'N'],
            'IS_MONEY_MARKET': ['N', 'N'],
            'IS_TARGET_DATE': ['N', 'Y'],
            'MONTHLY_AVG_NET_ASSETS': ['50000000', '75000000'],
            'MANAGEMENT_FEE': ['0.75', '0.65'],
            'NAV_PER_SHARE': ['25.50', '18.75']
        }
        
        self.sample_adviser_data = {
            'FUND_ID': ['F001', 'F002'],
            'SOURCE': ['SUBMISSION', 'SUBMISSION'],
            'ADVISER_TYPE': ['Investment Adviser', 'Investment Adviser'],
            'ADVISER_NAME': ['Test Investment Management', 'Test Investment Management'],
            'FILE_NUM': ['801-12345', '801-12345'],
            'CRD_NUM': ['123456', '123456'],
            'ADVISER_LEI': ['123456789012345678GH', '123456789012345678GH'],
            'STATE': ['NY', 'NY'],
            'COUNTRY': ['US', 'US'],
            'IS_AFFILIATED': ['Y', 'Y'],
            'IS_ADVISOR_HIRED': ['N', 'N'],
            'ADVISOR_START_DATE': ['2020-01-01', '2020-01-01']
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_zip(self):
        """Create a test ZIP file with sample N-CEN data."""
        with zipfile.ZipFile(self.test_zip_path, 'w') as zf:
            # Create submission TSV
            submission_df = pd.DataFrame(self.sample_submission_data)
            submission_tsv = submission_df.to_csv(sep='\t', index=False)
            zf.writestr('SUBMISSION.tsv', submission_tsv)
            
            # Create registrant TSV
            registrant_df = pd.DataFrame(self.sample_registrant_data)
            registrant_tsv = registrant_df.to_csv(sep='\t', index=False)
            zf.writestr('REGISTRANT.tsv', registrant_tsv)
            
            # Create fund reported info TSV
            fund_df = pd.DataFrame(self.sample_fund_data)
            fund_tsv = fund_df.to_csv(sep='\t', index=False)
            zf.writestr('FUND_REPORTED_INFO.tsv', fund_tsv)
            
            # Create adviser TSV
            adviser_df = pd.DataFrame(self.sample_adviser_data)
            adviser_tsv = adviser_df.to_csv(sep='\t', index=False)
            zf.writestr('ADVISER.tsv', adviser_tsv)
    
    def test_column_sanitization(self):
        """Test that column names are properly sanitized."""
        df = pd.DataFrame({
            'ACCESSION_NUMBER': ['test'],
            'IS_LEGAL_PROCEEDINGS': ['Y'],
            'FUND_NAME': ['Test Fund']
        })
        
        sanitized_df = sanitize_column_names(df)
        
        expected_columns = ['accession_number', 'is_legal_proceedings', 'fund_name']
        self.assertEqual(list(sanitized_df.columns), expected_columns)
    
    def test_data_type_conversion(self):
        """Test data type conversion functionality."""
        df = pd.DataFrame({
            'filing_date': ['2023-03-31', '2023-06-30'],
            'total_series': ['5', '10'],
            'is_etf': ['Y', 'N'],
            'management_fee': ['0.75', '0.65']
        })
        
        # Manually convert data types as done in the actual processing functions
        df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
        df['total_series'] = pd.to_numeric(df['total_series'], errors='coerce')
        df['management_fee'] = pd.to_numeric(df['management_fee'], errors='coerce')
        df['is_etf'] = df['is_etf'].map({'Y': True, 'N': False})
        
        # Check data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['filing_date']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['total_series']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['management_fee']))
        self.assertTrue(df['is_etf'].dtype == bool)
        
        # Check values
        self.assertEqual(df['is_etf'].iloc[0], True)
        self.assertEqual(df['is_etf'].iloc[1], False)
        self.assertEqual(df['total_series'].iloc[0], 5)
        self.assertEqual(df['management_fee'].iloc[0], 0.75)
    
    @patch('processor.load_data_to_db')
    def test_process_ncen_data_success(self, mock_load_data):
        """Test successful N-CEN data processing."""
        self.create_test_zip()
        
        # Mock the database loading function
        mock_load_data.return_value = None
        
        # Process the data
        result = process_ncen_data(self.test_dir)
        
        # Check results
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['errors'], 0)
        self.assertIn('test_ncen.zip', result['files'])
        
        # Verify that load_data_to_db was called for each table type
        self.assertEqual(mock_load_data.call_count, 4)  # submission, registrant, fund, adviser
    
    def test_process_ncen_data_no_directory(self):
        """Test N-CEN processing with non-existent directory."""
        result = process_ncen_data('/nonexistent/directory')
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Source directory not found')
    
    def test_process_ncen_data_no_zip_files(self):
        """Test N-CEN processing with no ZIP files."""
        result = process_ncen_data(self.test_dir)
        
        self.assertEqual(result['processed'], 0)
        self.assertEqual(result['errors'], 0)
    
    @patch('processor.load_data_to_db')
    def test_process_ncen_data_with_error(self, mock_load_data):
        """Test N-CEN processing with database error."""
        self.create_test_zip()
        
        # Mock database error
        mock_load_data.side_effect = Exception("Database error")
        
        result = process_ncen_data(self.test_dir)
        
        # Should still process the file but report errors
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['errors'], 4)  # One error per TSV file
    
    def test_empty_tsv_handling(self):
        """Test handling of empty TSV files."""
        with zipfile.ZipFile(self.test_zip_path, 'w') as zf:
            # Create empty TSV
            zf.writestr('SUBMISSION.tsv', 'ACCESSION_NUMBER\n')  # Header only
        
        with patch('processor.load_data_to_db') as mock_load_data:
            result = process_ncen_data(self.test_dir)
            
            # Should process without errors but not call load_data_to_db
            self.assertEqual(result['processed'], 1)
            self.assertEqual(result['errors'], 0)
            mock_load_data.assert_not_called()
    
    def test_unsupported_tsv_files(self):
        """Test handling of unsupported TSV files."""
        with zipfile.ZipFile(self.test_zip_path, 'w') as zf:
            # Create unsupported TSV
            df = pd.DataFrame({'UNKNOWN_FIELD': ['value1', 'value2']})
            tsv_content = df.to_csv(sep='\t', index=False)
            zf.writestr('UNKNOWN_TABLE.tsv', tsv_content)
        
        with patch('processor.load_data_to_db') as mock_load_data:
            result = process_ncen_data(self.test_dir)
            
            # Should process without errors but not call load_data_to_db
            self.assertEqual(result['processed'], 1)
            self.assertEqual(result['errors'], 0)
            mock_load_data.assert_not_called()


class TestNCENDatabaseModels(unittest.TestCase):
    """Test cases for N-CEN database models."""
    
    def test_ncen_submission_model(self):
        """Test NCENSubmission model creation."""
        submission = NCENSubmission(
            accession_number='0001234567-23-000001',
            submission_type='N-CEN',
            cik='0001234567',
            filing_date=datetime(2023, 3, 31),
            report_ending_period=datetime(2023, 3, 31),
            is_legal_proceedings=False
        )
        
        self.assertEqual(submission.accession_number, '0001234567-23-000001')
        self.assertEqual(submission.submission_type, 'N-CEN')
        self.assertEqual(submission.cik, '0001234567')
        self.assertFalse(submission.is_legal_proceedings)
    
    def test_ncen_registrant_model(self):
        """Test NCENRegistrant model creation."""
        registrant = NCENRegistrant(
            accession_number='0001234567-23-000001',
            registrant_name='Test Fund Company',
            cik='0001234567',
            city='New York',
            state='NY',
            is_first_filing=True,
            total_series=5
        )
        
        self.assertEqual(registrant.registrant_name, 'Test Fund Company')
        self.assertEqual(registrant.city, 'New York')
        self.assertEqual(registrant.state, 'NY')
        self.assertTrue(registrant.is_first_filing)
        self.assertEqual(registrant.total_series, 5)
    
    def test_ncen_fund_model(self):
        """Test NCENFundReportedInfo model creation."""
        fund = NCENFundReportedInfo(
            fund_id='F001',
            accession_number='0001234567-23-000001',
            fund_name='Growth Fund',
            is_etf=False,
            is_money_market=False,
            monthly_avg_net_assets=50000000,
            management_fee=0.75,
            nav_per_share=25.50
        )
        
        self.assertEqual(fund.fund_id, 'F001')
        self.assertEqual(fund.fund_name, 'Growth Fund')
        self.assertFalse(fund.is_etf)
        self.assertEqual(fund.monthly_avg_net_assets, 50000000)
        self.assertEqual(fund.management_fee, 0.75)
        self.assertEqual(fund.nav_per_share, 25.50)
    
    def test_ncen_adviser_model(self):
        """Test NCENAdviser model creation."""
        adviser = NCENAdviser(
            fund_id='F001',
            adviser_name='Test Investment Management',
            adviser_type='Investment Adviser',
            state='NY',
            country='US',
            is_affiliated=True
        )
        
        self.assertEqual(adviser.fund_id, 'F001')
        self.assertEqual(adviser.adviser_name, 'Test Investment Management')
        self.assertEqual(adviser.adviser_type, 'Investment Adviser')
        self.assertEqual(adviser.state, 'NY')
        self.assertTrue(adviser.is_affiliated)


if __name__ == '__main__':
    unittest.main()
