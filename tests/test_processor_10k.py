"""Tests for the 10-K/10-Q processor module."""

import os
import unittest
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the processor and database models
from database import Base, Sec10KSubmission, Sec10KDocument, Sec10KFinancials
from processor_10k import SEC10KProcessor

class TestSEC10KProcessor(unittest.TestCase):
    """Test cases for the SEC10KProcessor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and sample data."""
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        
        # Create a test data directory
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data', 'sec', '10k')
        os.makedirs(cls.test_data_dir, exist_ok=True)
        
        # Create a sample 10-K filing
        cls.sample_10k = os.path.join(cls.test_data_dir, '0000320193-20-000096.txt')
        sample_content = (
            "<SEC-HEADER>"
            "<ACCEPTANCE-DATETIME>20201102180000"
            "<FILING-DATE>2020-10-30"
            "<PERIOD>20200926"
            "<FILER>"
            "<COMPANY-CONFORMED-NAME>APPLE INC"
            "<CIK>0000320193"
            "</FILER>"
            "<FILING-VALUES>"
            "<FORM>10-K"
            "<FILENUMBER>001-36743"
            "<SEC-ACT>1934"
            "<FILM-NUMBER>20516103"
            "</FILING-VALUES>"
            "<PERIOD-OF-REPORT>2020-09-26</PERIOD-OF-REPORT>"
            "<FISCAL-YEAR-END>0930"
            "</SEC-HEADER>"
            "<DOCUMENT>"
            "<TYPE>10-K"
            "<SEQUENCE>1"
            "<FILENAME>aapl-20200926_10k.htm"
            "<TEXT>"
            "<html>"
            "<head>"
            "<title>10-K - Apple Inc. (Filing Date: 10/30/2020)</title>"
            "</head>"
            "<body>"
            "<div>Item 1. Business</div>"
            "<div>Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.</div>"
            "<div>Item 1A. Risk Factors</div>"
            "<div>The Company is exposed to various risks including global economic conditions, competition, and supply chain disruptions.</div>"
            "<div>Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations</div>"
            "<div>For the fiscal year ended September 26, 2020, the Company reported net sales of $274.5 billion, an increase of $15.9 billion or 6% compared to 2019.</div>"
            "<div>Item 8. Financial Statements and Supplementary Data</div>"
            "<div>CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except number of shares which are reflected in thousands and per share amounts)</div>"
            "<div>Net sales: $274,515</div>"
            "<div>Net income: $57,411</div>"
            "<div>Earnings per share: $3.28</div>"
            "</body>"
            "</html>"
            "</TEXT>"
            "</DOCUMENT>"
        )
        with open(cls.sample_10k, 'w', encoding='utf-8') as f:
            f.write(sample_content)
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_session = self.Session()
        self.processor = SEC10KProcessor(db_session=self.db_session)
    
    def tearDown(self):
        """Clean up after each test method."""
        self.db_session.rollback()
        self.db_session.close()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data after all tests."""
        # Remove test data directory
        if os.path.exists(os.path.dirname(cls.test_data_dir)):
            shutil.rmtree(os.path.dirname(cls.test_data_dir))
    
    def test_extract_filing_metadata(self):
        """Test extraction of metadata from a 10-K filing."""
        metadata = self.processor.extract_filing_metadata(self.sample_10k)
        
        self.assertEqual(metadata['accession_number'], '0000320193-20-000096')
        self.assertEqual(metadata['form_type'], '10-K')
        self.assertEqual(metadata['cik'], '0000320193')
        self.assertEqual(metadata['company_name'], 'APPLE INC')
        self.assertEqual(metadata['file_number'], '001-36743')
        self.assertEqual(metadata['sec_act'], '1934')
        self.assertEqual(metadata['film_number'], '20516103')
        self.assertIsNotNone(metadata['filing_date'])
        self.assertIsNotNone(metadata['period_of_report'])
    
    def test_parse_filing_sections(self):
        """Test parsing of 10-K filing sections."""
        sections = self.processor.parse_filing_sections(self.sample_10k)
        
        # Check that we found the expected sections
        section_ids = {s['section'] for s in sections}
        self.assertIn('business', section_ids)
        self.assertIn('risk_factors', section_ids)
        self.assertIn('mdna', section_ids)
        self.assertIn('financial_statements', section_ids)
        
        # Check content of a section
        business_section = next(s for s in sections if s['section'] == 'business')
        self.assertIn('Apple Inc. designs, manufactures', business_section['content'])
        self.assertGreater(business_section['word_count'], 0)
    
    def test_extract_financial_data(self):
        """Test extraction of financial data from a 10-K filing."""
        financials = self.processor.extract_financial_data(self.sample_10k)
        
        # Check that we found the expected financial metrics
        metrics = {f['metric_name'] for f in financials}
        self.assertIn('revenue', metrics)
        self.assertIn('net_income', metrics)
        
        # Check values
        for fin in financials:
            if fin['metric_name'] == 'revenue':
                self.assertGreater(fin['metric_value'], 0)
                self.assertEqual(fin['metric_unit'], 'USD')
    
    def test_save_to_database(self):
        """Test saving extracted data to the database."""
        # Extract data
        metadata = self.processor.extract_filing_metadata(self.sample_10k)
        sections = self.processor.parse_filing_sections(self.sample_10k)
        financials = self.processor.extract_financial_data(self.sample_10k)
        
        # Save to database
        success = self.processor.save_to_database(metadata, sections, financials)
        self.assertTrue(success)
        
        # Verify data was saved
        submission = self.db_session.query(Sec10KSubmission).filter_by(
            accession_number=metadata['accession_number']
        ).first()
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.company_name, metadata['company_name'])
        self.assertEqual(submission.form_type, metadata['form_type'])
        
        # Check sections were saved
        doc_sections = self.db_session.query(Sec10KDocument).filter_by(
            accession_number=metadata['accession_number']
        ).all()
        self.assertGreaterEqual(len(doc_sections), 3)  # At least 3 sections
        
        # Check financial data was saved
        fin_data = self.db_session.query(Sec10KFinancials).filter_by(
            accession_number=metadata['accession_number']
        ).all()
        self.assertGreaterEqual(len(fin_data), 1)  # At least 1 financial metric
    
    @patch('processor_10k.requests.Session.get')
    def test_download_filing(self, mock_get):
        """Test downloading a 10-K filing from SEC EDGAR."""
        # Mock the response from SEC EDGAR
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'Test filing content'
        mock_get.return_value = mock_response
        
        # Test download
        accession_number = '0000320193-20-000096'
        cik = '0000320193'
        form_type = '10-K'
        
        # Call the method
        result = self.processor.download_filing(accession_number, cik, form_type)
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        self.assertIn(accession_number, result)
        
        # Clean up
        if os.path.exists(result):
            os.remove(result)
    
    def test_process_filing(self):
        """Test end-to-end processing of a 10-K filing."""
        # Process the test filing
        success = self.processor.process_filing(self.sample_10k)
        self.assertTrue(success)
        
        # Verify data was saved to the database
        submission = self.db_session.query(Sec10KSubmission).filter_by(
            accession_number='0000320193-20-000096'
        ).first()
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.company_name, 'APPLE INC')
        
        # Check sections were saved
        sections = self.db_session.query(Sec10KDocument).filter_by(
            accession_number='0000320193-20-000096'
        ).all()
        self.assertGreaterEqual(len(sections), 3)
        
        # Check financial data was saved
        financials = self.db_session.query(Sec10KFinancials).filter_by(
            accession_number='0000320193-20-000096'
        ).all()
        self.assertGreaterEqual(len(financials), 1)

if __name__ == '__main__':
    unittest.main()
