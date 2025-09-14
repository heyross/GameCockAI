import os
import unittest
import zipfile
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Import from the correct database module (GameCockAI/database.py)
from database import Base, SecSubmission
from processor import process_sec_insider_data

class TestSecProcessor(unittest.TestCase):
    def setUp(self):
        """Set up a temporary database and test data."""
        self.db_path = "test_sec_db.db"
        self.source_dir = "test_sec_source"
        os.makedirs(self.source_dir, exist_ok=True)

        # Setup database
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Create a dummy zip file with sample data
        self.zip_path = os.path.join(self.source_dir, "sample_sec.zip")
        with zipfile.ZipFile(self.zip_path, 'w') as zf:
            submission_data = (
                b"ACCESSION_NUMBER\tFILING_DATE\tPERIOD_OF_REPORT\tDOCUMENT_TYPE\tISSUERCIK\tISSUERNAME\tISSUERTRADINGSYMBOL\n"
                b"00012345-67-890123\t01-Jan-2023\t01-Jan-2023\t4\t1234567890\tTest Corp\tTEST\n"
            )
            zf.writestr("SUBMISSION.tsv", submission_data)

    def tearDown(self):
        """Clean up the temporary database and test files."""
        # Ensure all connections are closed before trying to delete the file
        self.engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.source_dir):
            os.rmdir(self.source_dir)

    def test_process_sec_insider_data(self):
        """Test that SEC insider data is processed and loaded correctly."""
        session = self.Session()
        process_sec_insider_data(self.source_dir, db_session=session)
        try:
            # Verify that the data was loaded
            submission = session.query(SecSubmission).first()
            self.assertIsNotNone(submission)
            self.assertEqual(submission.accession_number, "00012345-67-890123")
            self.assertEqual(submission.issuercik, "1234567890")
            self.assertEqual(submission.issuername, "Test Corp")
            self.assertEqual(submission.filing_date, datetime(2023, 1, 1))
        finally:
            session.close()

if __name__ == '__main__':
    unittest.main()
