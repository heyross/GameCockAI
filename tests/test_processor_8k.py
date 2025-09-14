"""Tests for the 8-K processor module."""

import os
import unittest
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the processor and database models
# Import from the correct database module (GameCockAI/database.py)
from database import Base, Sec8KSubmission, Sec8KItem
from processor_8k import SEC8KProcessor

class TestSEC8KProcessor(unittest.TestCase):
    """Test cases for the SEC8KProcessor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and sample data."""
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        
        # Create a test data directory
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data', 'sec', '8k')
        os.makedirs(cls.test_data_dir, exist_ok=True)
        
        # Create a sample 8-K filing
        cls.sample_8k = os.path.join(cls.test_data_dir, 'sample-8k.txt')
        sample_content = (
            '<SEC-HEADER>\n'
            '    <ACCEPTANCE-DATETIME>20230101120000</ACCEPTANCE-DATETIME>\n'
            '    <FILING-DATE>2023-01-01</FILING-DATE>\n'
            '    <PERIOD>20230101</PERIOD>\n'
            '    <COMPANY-CONFORMED-NAME>TEST CORP</COMPANY-CONFORMED-NAME>\n'
            '    <CIK>0001234567</CIK>\n'
            '    <TYPE>8-K</TYPE>\n'
            '    <ITEMS>1.01</ITEMS>\n'
            '</SEC-HEADER>\n'
            '<DOCUMENT>\n'
            '<TYPE>8-K</TYPE>\n'
            '<TEXT>\n'
            '<html><body>\n'
            '<p>Item 1.01 Entry into a Material Definitive Agreement.</p>\n'
            '<p>On January 1, 2023, the Company entered into a material definitive agreement.</p>\n'
            '</body></html>\n'
            '</TEXT>\n'
            '</DOCUMENT>\n'
        )
        with open(cls.sample_8k, 'w', encoding='utf-8') as f:
            f.write(sample_content)
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_session = self.Session()
        self.processor = SEC8KProcessor(db_session=self.db_session)
    
    def tearDown(self):
        """Clean up after each test method."""
        self.db_session.rollback()
        self.db_session.close()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data after all tests."""
        if os.path.exists(os.path.dirname(cls.test_data_dir)):
            shutil.rmtree(os.path.dirname(cls.test_data_dir))

    def test_extract_filing_metadata(self):
        """Test extraction of metadata from an 8-K filing."""
        metadata = self.processor.extract_filing_metadata(self.sample_8k)
        self.assertEqual(metadata['cik'], '0001234567')
        self.assertEqual(metadata['company_name'], 'TEST CORP')
        self.assertEqual(metadata['form_type'], '8-K')
        self.assertIsNotNone(metadata['filing_date'])

    def test_parse_filing_items(self):
        """Test parsing of 8-K filing items."""
        items = self.processor.parse_filing_items(self.sample_8k)
        self.assertGreater(len(items), 0)
        self.assertEqual(items[0]['item_number'], '1.01')
        self.assertIn('Material Definitive Agreement', items[0]['content'])

    def test_save_to_database(self):
        """Test saving extracted 8-K data to the database."""
        metadata = self.processor.extract_filing_metadata(self.sample_8k)
        items = self.processor.parse_filing_items(self.sample_8k)
        success = self.processor.save_to_database(metadata, items)
        self.assertTrue(success)

        submission = self.db_session.query(Sec8KSubmission).filter_by(accession_number=metadata['accession_number']).first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.company_name, 'TEST CORP')

        db_items = self.db_session.query(Sec8KItem).filter_by(accession_number=metadata['accession_number']).all()
        self.assertGreater(len(db_items), 0)
        self.assertEqual(db_items[0].item_number, '1.01')

    def test_process_filing(self):
        """Test end-to-end processing of an 8-K filing."""
        success = self.processor.process_filing(self.sample_8k)
        self.assertTrue(success)

        accession_number = os.path.basename(self.sample_8k).replace('.txt', '')
        submission = self.db_session.query(Sec8KSubmission).filter_by(accession_number=accession_number).first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.company_name, 'TEST CORP')

if __name__ == '__main__':
    unittest.main()
