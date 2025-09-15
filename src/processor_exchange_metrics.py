"""
Exchange Metrics Processor Module

This module handles processing of SEC Exchange Metrics data from ZIP archives.
Exchange Metrics data contains trading statistics and market data.
"""

import glob
import logging
import os
import pandas as pd
from zipfile import ZipFile
from database import SecExchangeMetrics, SessionLocal

logger = logging.getLogger(__name__)

def sanitize_column_names(df):
    """Sanitizes DataFrame column names to be valid Python identifiers."""
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
    df.columns = df.columns.str.replace(r'^_+|_+$', '', regex=True)
    df.columns = [''.join(c if c.isalnum() or c == '_' else '_' for c in col) for col in df.columns]
    return df

def process_exchange_metrics_data(source_dir, db_session=None):
    """Processes SEC Exchange Metrics data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))
    db = db_session if db_session else SessionLocal()

    numeric_columns = [
        'mcap_rank', 'turn_rank', 'volatility_rank', 'price_rank', 'cancels',
        'trades', 'lit_trades', 'odd_lots', 'hidden', 'trades_for_hidden',
        'order_vol', 'trade_vol', 'lit_vol', 'odd_lot_vol', 'hidden_vol',
        'trade_vol_for_hidden'
    ]
    date_columns = ['date']

    try:
        for zip_file in zip_files:
            logging.info(f"Processing Exchange Metrics file: {zip_file}")
            try:
                with ZipFile(zip_file, 'r') as zip_ref:
                    for csv_filename in zip_ref.namelist():
                        if not csv_filename.endswith('.csv'):
                            continue
                        
                        with zip_ref.open(csv_filename) as csv_file:
                            df = pd.read_csv(csv_file, low_memory=False)
                            df = sanitize_column_names(df)

                            # Manual column name corrections for exchange metrics
                            column_renames = {
                                'mcfrank': 'mcap_rank',
                                'turnrank': 'turn_rank',
                                'volatilityrank': 'volatility_rank',
                                'pricerank': 'price_rank',
                                'littrades': 'lit_trades',
                                'oddlots': 'odd_lots',
                                'tradesforhidden': 'trades_for_hidden',
                                'ordervol': 'order_vol',
                                'tradevol': 'trade_vol',
                                'litvol': 'lit_vol',
                                'oddlotvol': 'odd_lot_vol',
                                'hiddenvol': 'hidden_vol',
                                'tradevolforhidden': 'trade_vol_for_hidden'
                            }
                            df.rename(columns=column_renames, inplace=True)

                            for col in date_columns:
                                if col in df.columns:
                                    df[col] = pd.to_datetime(df[col], errors='coerce')
                            
                            for col in numeric_columns:
                                if col in df.columns:
                                    df[col] = pd.to_numeric(df[col], errors='coerce')

                            records = df.where(pd.notna(df), None).to_dict(orient='records')
                            db.bulk_insert_mappings(SecExchangeMetrics, records)
                            logging.info(f"Loading {len(records)} records into {SecExchangeMetrics.__tablename__} from {csv_filename}")
                db.commit()
            except Exception as e:
                logging.error(f"Error processing file {zip_file}: {e}")
                db.rollback()
    finally:
        if not db_session:
            db.close()
