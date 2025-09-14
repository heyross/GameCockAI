import unittest
import os
import tempfile
import shutil
import pandas as pd
from zipfile import ZipFile
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor import process_formd_data, process_formd_quarter
from downloader import extract_formd_filings
from database import (SessionLocal, FormDSubmission, FormDIssuer, FormDOffering, 
                     FormDRecipient, FormDRelatedPerson, FormDSignature)


class TestFormDProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_source_dir = os.path.join(self.test_dir, 'SecFormD')
        os.makedirs(self.test_source_dir, exist_ok=True)
        
        # Create mock TSV data
        self.mock_submission_data = {
            'ACCESSIONNUMBER': ['0001234567-20-000001', '0001234567-20-000002'],
            'FILENUM': ['021-123456', '021-123457'],
            'FILINGDATE': ['2020-01-15 10:30:00', '2020-01-16 11:45:00'],
            'SICCODE': ['1234', '5678'],
            'SCHEMAVERSION': ['X0603', 'X0603'],
            'SUBMISSIONTYPE': ['D', 'D'],
            'TESTORLIVE': ['LIVE', 'LIVE'],
            'OVER100PERSONSFLAG': ['Y', 'N'],
            'OVER100ISSUERFLAG': ['N', 'Y']
        }
        
        self.mock_issuer_data = {
            'ACCESSIONNUMBER': ['0001234567-20-000001', '0001234567-20-000002'],
            'SEQUENCENUMBER': ['1', '1'],
            'CIKOFISSUER': ['1234567', '2345678'],
            'NAMEOFISSUER': ['Test Company Inc.', 'Another Corp'],
            'JURISDICTIONOFINCORPORATION': ['DE', 'CA'],
            'YEAROFINCORPORATION': ['2010', '2015'],
            'ENTITYTYPE': ['Corporation', 'LLC'],
            'STREETADDRESS1': ['123 Main St', '456 Oak Ave'],
            'STREETADDRESS2': ['Suite 100', ''],
            'CITY': ['New York', 'Los Angeles'],
            'STATEORCOUNTRY': ['NY', 'CA'],
            'ZIPCODE': ['10001', '90210'],
            'PHONENUMBER': ['555-123-4567', '555-987-6543']
        }
        
        self.mock_offering_data = {
            'ACCESSIONNUMBER': ['0001234567-20-000001', '0001234567-20-000002'],
            'SEQUENCENUMBER': ['1', '1'],
            'INDUSTRYGROUP': ['Technology', 'Healthcare'],
            'INVESTMENTFUNDTYPE': ['', ''],
            'ISFEEDERORFUND': ['N', 'N'],
            'TYPEOFFILINGFLAG': ['NewNotice', 'Amendment'],
            'DATEOFSALEFIRST': ['2020-01-01', '2020-01-02'],
            'DATEOFSALELAST': ['2020-12-31', '2020-12-30'],
            'TYPEOFOFFERING': ['506b', '506c'],
            'DURATIONOFOFFERING': ['MoreThanOneYear', 'MoreThanOneYear'],
            'TYPEOFSECURITYOFFERED': ['Equity', 'Debt'],
            'BUSINESSCOMBINATIONFLAG': ['N', 'N'],
            'MINIMUMINVESTMENTACCEPTED': ['50000', '100000'],
            'SALESCOMPENSATIONAMOUNT': ['25000', '50000'],
            'FINDERSFEEAMOUNT': ['5000', '10000'],
            'SALESCOMMISSIONAMOUNT': ['20000', '40000'],
            'OFFERAMOUNT': ['1000000', '2000000'],
            'TOTALOFFERINGAMOUNT': ['1000000', '2000000'],
            'TOTALAMOUNTSOLD': ['750000', '1500000'],
            'TOTALREMAINING': ['250000', '500000'],
            'CLARIFICATIONOFRESPONSE': ['', '']
        }

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir)

    def create_mock_quarterly_archive(self, quarter_name):
        """Create a mock quarterly archive with TSV files."""
        # Create quarterly directory structure that matches real Form D archives
        quarter_dir = os.path.join(self.test_source_dir, quarter_name)
        quarter_subdir = os.path.join(quarter_dir, quarter_name.upper())  # e.g., 2020Q1_D
        os.makedirs(quarter_subdir, exist_ok=True)
        
        # Create TSV files in the subdirectory
        submission_df = pd.DataFrame(self.mock_submission_data)
        submission_df.to_csv(os.path.join(quarter_subdir, 'FORMDSUBMISSION.tsv'), 
                           sep='\t', index=False)
        
        issuer_df = pd.DataFrame(self.mock_issuer_data)
        issuer_df.to_csv(os.path.join(quarter_subdir, 'ISSUERS.tsv'), 
                        sep='\t', index=False)
        
        offering_df = pd.DataFrame(self.mock_offering_data)
        offering_df.to_csv(os.path.join(quarter_subdir, 'OFFERING.tsv'), 
                          sep='\t', index=False)
        
        # Create empty TSV files for other tables
        for filename in ['RECIPIENTS.tsv', 'RELATEDPERSONS.tsv', 'SIGNATURES.tsv']:
            with open(os.path.join(quarter_subdir, filename), 'w') as f:
                f.write('ACCESSIONNUMBER\n')  # Empty file with header
        
        # Create zip archive
        zip_path = os.path.join(self.test_source_dir, f'{quarter_name}.zip')
        with ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(quarter_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.test_source_dir)
                    zipf.write(file_path, arcname)
        
        # Remove the directory (we only want the zip)
        shutil.rmtree(quarter_dir)
        
        return zip_path

    @patch('downloader.FORMD_SOURCE_DIR')
    def test_extract_formd_filings(self, mock_formd_source_dir):
        """Test the extraction of Form D quarterly archives."""
        # Mock the FORMD_SOURCE_DIR to use our test directory
        mock_formd_source_dir.__str__ = lambda: self.test_source_dir
        mock_formd_source_dir.return_value = self.test_source_dir
        
        # Create mock archive
        zip_path = self.create_mock_quarterly_archive('2020q1_d')
        
        # Test extraction with mocked source directory
        with patch('downloader.FORMD_SOURCE_DIR', self.test_source_dir):
            extract_formd_filings(zip_path)
        
        # Verify extraction - check for the extracted directory
        extracted_dir = os.path.join(self.test_source_dir, '2020q1_d')
        self.assertTrue(os.path.exists(extracted_dir))
        
        # Debug: Print the actual directory structure
        print(f"\nDebugging extracted directory: {extracted_dir}")
        for root, dirs, files in os.walk(extracted_dir):
            level = root.replace(extracted_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        # Find TSV files recursively
        tsv_files_found = []
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                if file.endswith('.tsv'):
                    tsv_files_found.append(file)
        
        # Verify we found at least some TSV files
        self.assertTrue(len(tsv_files_found) >= 3, f"Expected TSV files not found. Found: {tsv_files_found}")

    @patch('processor.SessionLocal')
    def test_process_formd_quarter(self, mock_session_local):
        """Test processing of a single Form D quarter."""
        # Create mock quarterly directory structure (quarter_dir contains a subdirectory)
        quarter_dir = os.path.join(self.test_source_dir, '2020q1_d')
        quarter_subdir = os.path.join(quarter_dir, '2020Q1_d')  # Actual data directory
        os.makedirs(quarter_subdir, exist_ok=True)
        
        # Create TSV files in the subdirectory
        submission_df = pd.DataFrame(self.mock_submission_data)
        submission_df.to_csv(os.path.join(quarter_subdir, 'FORMDSUBMISSION.tsv'), 
                           sep='\t', index=False)
        
        issuer_df = pd.DataFrame(self.mock_issuer_data)
        issuer_df.to_csv(os.path.join(quarter_subdir, 'ISSUERS.tsv'), 
                        sep='\t', index=False)
        
        # Create empty TSV files for other tables
        for filename in ['OFFERING.tsv', 'RECIPIENTS.tsv', 'RELATEDPERSONS.tsv', 'SIGNATURES.tsv']:
            with open(os.path.join(quarter_subdir, filename), 'w') as f:
                f.write('ACCESSIONNUMBER\n')  # Empty file with header
        
        # Mock database session
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Test processing
        process_formd_quarter(quarter_dir, mock_session)
        
        # Verify bulk_insert_mappings was called
        self.assertTrue(mock_session.bulk_insert_mappings.called)
        
        # Verify commit was called
        mock_session.commit.assert_called()

    @patch('processor.SessionLocal')
    def test_process_formd_data_integration(self, mock_session_local):
        """Test the complete Form D data processing pipeline."""
        # Create multiple mock quarterly archives
        quarters = ['2020q1_d', '2020q2_d']
        for quarter in quarters:
            self.create_mock_quarterly_archive(quarter)
        
        # Mock database session
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Test complete processing
        process_formd_data(self.test_source_dir, mock_session)
        
        # Verify extraction and processing occurred
        for quarter in quarters:
            extracted_dir = os.path.join(self.test_source_dir, quarter)
            self.assertTrue(os.path.exists(extracted_dir))
        
        # Verify database operations
        self.assertTrue(mock_session.bulk_insert_mappings.called)
        mock_session.commit.assert_called()

    def test_column_sanitization(self):
        """Test that column names are properly sanitized."""
        # Create test data with problematic column names
        test_data = {
            'ACCESS ION-NUMBER': ['test1', 'test2'],
            'FILE NUM': ['file1', 'file2'],
            'FILING@DATE': ['2020-01-01', '2020-01-02']
        }
        
        df = pd.DataFrame(test_data)
        
        # Apply sanitization (same logic as in processor)
        sanitized_columns = df.columns.str.strip().str.lower()
        sanitized_columns = sanitized_columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
        df.columns = sanitized_columns
        
        # Verify sanitization
        expected_columns = ['access_ion_number', 'file_num', 'filing_date']
        self.assertEqual(list(df.columns), expected_columns)

    def test_empty_tsv_handling(self):
        """Test handling of empty TSV files."""
        # Create quarterly directory with empty TSV
        quarter_dir = os.path.join(self.test_source_dir, '2020q1_d')
        os.makedirs(quarter_dir, exist_ok=True)
        
        # Create empty TSV file
        empty_file = os.path.join(quarter_dir, 'FORMDSUBMISSION.tsv')
        with open(empty_file, 'w') as f:
            f.write('ACCESSIONNUMBER\n')  # Header only
        
        # Mock database session
        with patch('processor.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # Should not raise exception
            process_formd_quarter(quarter_dir, mock_session)
            
            # Should not attempt to insert empty data
            mock_session.bulk_insert_mappings.assert_not_called()

    def test_missing_tsv_files(self):
        """Test handling of missing TSV files."""
        # Create quarterly directory without TSV files
        quarter_dir = os.path.join(self.test_source_dir, '2020q1_d')
        os.makedirs(quarter_dir, exist_ok=True)
        
        # Mock database session
        with patch('processor.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # Should not raise exception
            process_formd_quarter(quarter_dir, mock_session)
            
            # Should not attempt any database operations
            mock_session.bulk_insert_mappings.assert_not_called()


class TestFormDDatabaseSchema(unittest.TestCase):
    """Test Form D database schema and model definitions."""
    
    def test_formd_submission_model(self):
        """Test FormDSubmission model attributes."""
        # Test that model has expected attributes
        expected_attrs = ['accessionnumber', 'file_num', 'filing_date', 'sic_code',
                         'schemaversion', 'submissiontype', 'testorlive', 
                         'over100personsflag', 'over100issuerflag']
        
        for attr in expected_attrs:
            self.assertTrue(hasattr(FormDSubmission, attr),
                          f"FormDSubmission missing attribute: {attr}")

    def test_formd_issuer_model(self):
        """Test FormDIssuer model attributes."""
        expected_attrs = ['formd_issuer_sk', 'accessionnumber', 'is_primaryissuer_flag',
                         'issuer_seq_key', 'cik', 'entityname']
        
        for attr in expected_attrs:
            self.assertTrue(hasattr(FormDIssuer, attr),
                          f"FormDIssuer missing attribute: {attr}")

    def test_formd_offering_model(self):
        """Test FormDOffering model attributes."""
        expected_attrs = ['formd_offering_sk', 'accessionnumber', 'industrygrouptype',
                         'investmentfundtype', 'isamendment', 'sale_date']
        
        for attr in expected_attrs:
            self.assertTrue(hasattr(FormDOffering, attr),
                          f"FormDOffering missing attribute: {attr}")


if __name__ == '__main__':
    unittest.main()
