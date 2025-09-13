import os
import unittest
import zipfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from database import Base, NMFPSubmission, NMFPSeriesLevelInfo
from processor import process_nmfp_data

class TestNMFPProcessor(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_nmfp_db.db"
        self.source_dir = "test_nmfp_source"
        os.makedirs(self.source_dir, exist_ok=True)

        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.zip_path = os.path.join(self.source_dir, "sample_nmfp.zip")
        with zipfile.ZipFile(self.zip_path, 'w') as zf:
            submission_data = (
                b"ACCESSION_NUMBER\tFILING_DATE\tSUBMISSIONTYPE\tCIK\tREPORTDATE\tFILER_CIK\tSERIESID\tTOTALSHARECLASSESINSERIES\tFINALFILINGFLAG\n"
                b"000111-11-111111\t01-Jan-2023\tN-MFP\t12345\t31-Dec-2022\t12345\tS12345\t2\tN\n"
            )
            series_info_data = (
                b"ACCESSION_NUMBER\tFEEDERFUNDFLAG\tMASTERFUNDFLAG\tMONEYMARKETFUNDCATEGORY\tAVERAGEPORTFOLIOMATURITY\tAVERAGELIFEMATURITY\tTOTALVALUEOTHERASSETS\tTOTALVALUELIABILITIES\tNETASSETOFSERIES\tSEVENDAYGROSSYIELD\n"
                b"000111-11-111111\tN\tN\tGovernment\t30\t60\t1000.0\t500.0\t1000000.0\t1.23\n"
            )
            zf.writestr("SUBMISSION.tsv", submission_data)
            zf.writestr("SERIESLEVELINFO.tsv", series_info_data)

    def tearDown(self):
        self.engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.source_dir):
            os.rmdir(self.source_dir)

    def test_process_nmfp_data(self):
        session = self.Session()
        try:
            process_nmfp_data(self.source_dir, db_session=session)

            submission = session.query(NMFPSubmission).first()
            self.assertIsNotNone(submission)
            self.assertEqual(submission.cik, '12345')
            self.assertEqual(submission.filing_date, datetime(2023, 1, 1))

            series_info = session.query(NMFPSeriesLevelInfo).first()
            self.assertIsNotNone(series_info)
            self.assertEqual(series_info.money_market_fund_category, "Government")
            self.assertEqual(series_info.average_portfolio_maturity, 30)
        finally:
            session.close()

if __name__ == '__main__':
    unittest.main()
