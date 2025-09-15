"""
SEC Insider Trading Processor Module

This module handles processing of SEC insider trading data from ZIP archives.
SEC insider trading data includes Form 4, 3, and 5 filings.
"""

import glob
import logging
import os
import pandas as pd
from zipfile import ZipFile
from database import (
    SecSubmission, SecReportingOwner, SecNonDerivTrans, SecNonDerivHolding,
    SecDerivTrans, SecDerivHolding, SecFootnote, SecOwnerSignature, SessionLocal
)

logger = logging.getLogger(__name__)

def sanitize_column_names(df):
    """Sanitizes DataFrame column names to be valid Python identifiers."""
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
    df.columns = df.columns.str.replace(r'^_+|_+$', '', regex=True)
    df.columns = [''.join(c if c.isalnum() or c == '_' else '_' for c in col) for col in df.columns]
    return df

def process_sec_insider_data(source_dir, db_session=None):
    """Processes SEC insider trading data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))
    db = db_session if db_session else SessionLocal()

    table_map = {
        'SUBMISSION.tsv': SecSubmission,
        'REPORTINGOWNER.tsv': SecReportingOwner,
        'NONDERIV_TRANS.tsv': SecNonDerivTrans,
        'NONDERIV_HOLDING.tsv': SecNonDerivHolding,
        'DERIV_TRANS.tsv': SecDerivTrans,
        'DERIV_HOLDING.tsv': SecDerivHolding,
        'FOOTNOTES.tsv': SecFootnote,
        'OWNER_SIGNATURE.tsv': SecOwnerSignature,
    }

    date_columns = [
        'filing_date', 'period_of_report', 'date_of_orig_sub', 'trans_date',
        'deemed_execution_date', 'excercise_date', 'expiration_date', 'ownersignaturedate'
    ]

    try:
        for zip_file in zip_files:
            logging.info(f"Processing SEC insider file: {zip_file}")
            try:
                with ZipFile(zip_file, 'r') as zip_ref:
                    for file_name, model in table_map.items():
                        if file_name in zip_ref.namelist():
                            with zip_ref.open(file_name) as table_file:
                                df = pd.read_csv(table_file, sep='\t', low_memory=False, dtype=str)
                                df = sanitize_column_names(df)

                                # Manual column name corrections for insider data
                                column_renames = {
                                    'rptownercik': 'rptownercik',
                                    'rptownername': 'rptownername',
                                    'ownersignaturename': 'ownersignaturename',
                                    'ownersignaturedate': 'ownersignaturedate',
                                }
                                df.rename(columns=column_renames, inplace=True)

                                # Convert date columns
                                for col in date_columns:
                                    if col in df.columns:
                                        df[col] = pd.to_datetime(df[col], format='%d-%b-%Y', errors='coerce')

                                # Load data into the database
                                records = df.where(pd.notna(df), None).to_dict(orient='records')
                                db.bulk_insert_mappings(model, records)
                                logging.info(f"Loading {len(records)} records into {model.__tablename__}")
                db.commit()
            except Exception as e:
                logging.error(f"Error processing file {zip_file}: {e}")
                db.rollback()
    finally:
        if not db_session:
            db.close()
