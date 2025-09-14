import os
import unittest
import zipfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Import from the correct database module (GameCockAI/database.py)
from database import Base, Form13FSubmission, Form13FInfoTable
from processor import process_form13f_data

class TestForm13FProcessor(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_13f_db.db"
        self.source_dir = "test_13f_source"
        os.makedirs(self.source_dir, exist_ok=True)

        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.zip_path = os.path.join(self.source_dir, "sample_13f.zip")
        with zipfile.ZipFile(self.zip_path, 'w') as zf:
            submission_data = (
                b"ACCESSION_NUMBER\tFILING_DATE\tSUBMISSIONTYPE\tCIK\tPERIODOFREPORT\n"
                b"00011111-11-111111\t01-Jan-2023\t13F-HR\t1234567890\t31-Dec-2022\n"
            )
            infotable_data = (
                b"ACCESSION_NUMBER\tINFOTABLE_SK\tNAMEOFISSUER\tTITLEOFCLASS\tCUSIP\tVALUE\tSSHPRNAMT\tSSHPRNAMTTYPE\tINVESTMENTDISCRETION\tVOTING_AUTH_SOLE\tVOTING_AUTH_SHARED\tVOTING_AUTH_NONE\n"
                b"00011111-11-111111\t1\tTEST INC\tCOM\t123456789\t5000\t100\tSH\tSOLE\t100\t0\t0\n"
            )
            zf.writestr("SUBMISSION.tsv", submission_data)
            zf.writestr("INFOTABLE.tsv", infotable_data)

    def tearDown(self):
        self.engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.source_dir):
            os.rmdir(self.source_dir)

    def test_process_form13f_data(self):
        session = self.Session()
        try:
            process_form13f_data(self.source_dir, db_session=session)

            submission = session.query(Form13FSubmission).first()
            self.assertIsNotNone(submission)
            self.assertEqual(submission.cik, "1234567890")
            self.assertEqual(submission.filing_date, datetime(2023, 1, 1))

            infotable = session.query(Form13FInfoTable).first()
            self.assertIsNotNone(infotable)
            self.assertEqual(infotable.nameofissuer, "TEST INC")
            self.assertEqual(infotable.cusip, "123456789")
            self.assertEqual(infotable.value, 5000)
        finally:
            session.close()

if __name__ == '__main__':
    unittest.main()
