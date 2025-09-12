import unittest
import os
import shutil
import pandas as pd
from zipfile import ZipFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base, CFTCSwap, get_db_stats, export_db_to_csv, reset_database
from processor import process_zip_files, load_cftc_data_to_db

class TestProcessorDatabase(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory SQLite database and a temporary directory for test files."""
        self.test_dir = "test_temp_processor"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Use an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Monkey-patch the database session in the modules we're testing
        self.patcher_db = patch('database.SessionLocal', self.SessionLocal)
        self.patcher_proc = patch('processor.SessionLocal', self.SessionLocal)
        self.patcher_db.start()
        self.patcher_proc.start()

    def tearDown(self):
        """Clean up the temporary directory and stop the patchers."""
        shutil.rmtree(self.test_dir)
        self.patcher_db.stop()
        self.patcher_proc.stop()
        Base.metadata.drop_all(self.engine)

    def test_process_and_load(self):
        """Test processing a zip file and loading its data into the database."""
        # 1. Create a mock zip file with CSV data
        csv_data = "dissemination_id,notional_amount,asset_class\n1,1000,Credit"
        zip_path = os.path.join(self.test_dir, "test.zip")
        with ZipFile(zip_path, 'w') as zf:
            zf.writestr("test.csv", csv_data)

        # 2. Process the zip file
        df = process_zip_files(self.test_dir, target_companies=[])
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['asset_class'], 'Credit')

        # 3. Load the DataFrame into the database
        load_cftc_data_to_db(df)

        # 4. Verify the data in the database
        db = self.SessionLocal()
        count = db.query(CFTCSwap).count()
        self.assertEqual(count, 1)
        record = db.query(CFTCSwap).first()
        self.assertEqual(record.notional_amount, 1000)
        db.close()

    def test_db_stats_and_reset(self):
        """Test the database statistics and reset functionality."""
        # 1. Load some data
        db = self.SessionLocal()
        db.add(CFTCSwap(dissemination_id='123', notional_amount=500))
        db.commit()
        db.close()

        # 2. Check stats
        # We need to patch the global engine used by get_db_stats
        with patch('database.engine', self.engine):
            stats = get_db_stats()
            self.assertEqual(stats['cftc_swap_data'], 1)

            # 3. Reset the database
            reset_database()
            stats_after_reset = get_db_stats()
            self.assertEqual(stats_after_reset['cftc_swap_data'], 0)

if __name__ == '__main__':
    unittest.main()
