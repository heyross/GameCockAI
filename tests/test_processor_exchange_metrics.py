import os
import unittest
import zipfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from database import Base, SecExchangeMetrics
from processor import process_exchange_metrics_data

class TestExchangeMetricsProcessor(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_exchange_metrics.db"
        self.source_dir = "test_exchange_metrics_source"
        os.makedirs(self.source_dir, exist_ok=True)

        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.zip_path = os.path.join(self.source_dir, "sample_exchange_metrics.zip")
        with zipfile.ZipFile(self.zip_path, 'w') as zf:
            metrics_data = (
                b"Date,Ticker,Security,McapRank,TurnRank,VolatilityRank,PriceRank,Cancels,Trades,LitTrades,OddLots,Hidden,TradesForHidden,OrderVol,TradeVol,LitVol,OddLotVol,HiddenVol,TradeVolForHidden\n"
                b"2023-01-01,TEST,Test Security,1,2,3,4,100,50,40,10,5,2,1000.0,500.0,400.0,100.0,50.0,20.0\n"
            )
            zf.writestr("metrics.csv", metrics_data)

    def tearDown(self):
        self.engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.source_dir):
            os.rmdir(self.source_dir)

    def test_process_exchange_metrics_data(self):
        session = self.Session()
        try:
            process_exchange_metrics_data(self.source_dir, db_session=session)

            metric = session.query(SecExchangeMetrics).first()
            self.assertIsNotNone(metric)
            self.assertEqual(metric.ticker, "TEST")
            self.assertEqual(metric.date, datetime(2023, 1, 1))
            self.assertEqual(metric.trades, 50)
            self.assertEqual(metric.trade_vol, 500.0)
        finally:
            session.close()

if __name__ == '__main__':
    unittest.main()
