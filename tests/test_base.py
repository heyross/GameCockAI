"""
Base test class for integration tests, providing common setup and fixtures.
"""

import unittest
import tempfile
import os
import zipfile
import pandas as pd
import shutil
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adjust path to import from the root directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from database import create_db_and_tables, SessionLocal

class BaseIntegrationTest(unittest.TestCase):
    """Base class for integration tests with database setup and teardown."""

    @classmethod
    def setUpClass(cls):
        """Set up a temporary database for the entire test class."""
        cls.test_db_path = tempfile.mktemp(suffix='.db')
        cls.original_db_url = database.DATABASE_URL
        database.DATABASE_URL = f"sqlite:///{cls.test_db_path}"
        
        database.engine = create_engine(database.DATABASE_URL, connect_args={"check_same_thread": False})
        database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)
        
        create_db_and_tables()

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary database."""
        # It's crucial to dispose of the engine to release the file lock
        if hasattr(database.engine, 'dispose'):
            database.engine.dispose()

        database.DATABASE_URL = cls.original_db_url
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except PermissionError:
                print(f"Warning: Could not remove test database {cls.test_db_path}. It may still be in use.")

    def setUp(self):
        """Create a temporary directory and clear tables before each test."""
        self.test_dir = tempfile.mkdtemp()
        self.clear_all_tables()

    def tearDown(self):
        """Remove the temporary directory after each test."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def clear_all_tables(self):
        """Clear all data from tables to ensure test isolation."""
        db = SessionLocal()
        try:
            table_names = [
                'ncen_advisers', 'ncen_fund_reported_info', 'ncen_registrants', 'ncen_submissions',
                'nport_derivatives', 'nport_holdings', 'nport_general_info', 'nport_submissions'
            ]
            for table in table_names:
                db.execute(text(f"DELETE FROM {table}"))
            # Reset autoincrement counters for SQLite
            db.execute(text(f"DELETE FROM sqlite_sequence WHERE name IN ({', '.join([f'{chr(39)}{t}{chr(39)}' for t in table_names])})"))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    def create_ncen_test_data(self, file_name="2023q1_ncen.zip"):
        """Create a realistic N-CEN test data ZIP file."""
        ncen_zip_path = os.path.join(self.test_dir, file_name)
        timestamp = str(int(__import__('time').time() * 1000))[-6:]

        submission_data = {
            'ACCESSION_NUMBER': [f'000123456{timestamp}-23-000001'],
            'SUBMISSION_TYPE': ['N-CEN'], 'CIK': ['0001234567'], 'IS_ETF': ['Y'],
            'FILING_DATE': ['2023-04-15']
        }
        registrant_data = {
            'ACCESSION_NUMBER': [f'000123456{timestamp}-23-000001'],
            'REGISTRANT_NAME': ['Test ETF Company'], 'IS_FIRST_FILING': ['N']
        }
        fund_data = {
            'ACCESSION_NUMBER': [f'000123456{timestamp}-23-000001'],
            'FUND_ID': ['F001'],
            'FUND_NAME': ['Tech ETF'], 'IS_ETF': ['Y'], 'IS_MONEY_MARKET': ['N']
        }

        with zipfile.ZipFile(ncen_zip_path, 'w') as zf:
            zf.writestr('SUBMISSION.tsv', pd.DataFrame(submission_data).to_csv(sep='\t', index=False))
            zf.writestr('REGISTRANT.tsv', pd.DataFrame(registrant_data).to_csv(sep='\t', index=False))
            zf.writestr('FUND_REPORTED_INFO.tsv', pd.DataFrame(fund_data).to_csv(sep='\t', index=False))
        return ncen_zip_path

    def create_nport_test_data(self, file_name="2023q1_nport.zip"):
        """Create a realistic N-PORT test data ZIP file."""
        nport_zip_path = os.path.join(self.test_dir, file_name)
        timestamp = str(int(__import__('time').time() * 1000))[-6:]

        submission_data = {
            'ACCESSION_NUMBER': [f'000987654{timestamp}-23-000001'],
            'SUBMISSION_TYPE': ['N-PORT'], 'CIK': ['0009876543'], 'REGISTRANT_NAME': ['Large Cap Fund'],
            'FILING_DATE': ['2023-05-30']
        }
        holdings_data = {
            'ACCESSION_NUMBER': [f'000987654{timestamp}-23-000001'] * 2,
            'ISSUER_NAME': ['Apple Inc.', 'Tesla Inc.'],
            'BALANCE_HELD': ['100000', '25000'],
            'IS_RESTRICTED_SECURITY': ['N', 'Y']
        }

        with zipfile.ZipFile(nport_zip_path, 'w') as zf:
            zf.writestr('SUBMISSION.tsv', pd.DataFrame(submission_data).to_csv(sep='\t', index=False))
            zf.writestr('HOLDING.tsv', pd.DataFrame(holdings_data).to_csv(sep='\t', index=False))
        return nport_zip_path
