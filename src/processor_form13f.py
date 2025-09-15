"""
Form 13F Processor Module

This module handles processing of Form 13F filing data from ZIP archives.
Form 13F is used for quarterly institutional investment manager holdings reports.
"""

import glob
import logging
import os
import pandas as pd
from zipfile import ZipFile
from database import (
    Form13FSubmission, Form13FCoverPage, Form13FOtherManager, 
    Form13FSignature, Form13FSummaryPage, Form13FOtherManager2, 
    Form13FInfoTable, SessionLocal
)

logger = logging.getLogger(__name__)

def sanitize_column_names(df):
    """Sanitizes DataFrame column names to be valid Python identifiers."""
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
    df.columns = df.columns.str.replace(r'^_+|_+$', '', regex=True)
    df.columns = [''.join(c if c.isalnum() or c == '_' else '_' for c in col) for col in df.columns]
    return df

def process_form13f_data(source_dir, db_session=None):
    """Processes Form 13F data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))
    db = db_session if db_session else SessionLocal()

    table_map = {
        'SUBMISSION.tsv': Form13FSubmission,
        'COVERPAGE.tsv': Form13FCoverPage,
        'OTHERMANAGER.tsv': Form13FOtherManager,
        'SIGNATURE.tsv': Form13FSignature,
        'SUMMARYPAGE.tsv': Form13FSummaryPage,
        'OTHERMANAGER2.tsv': Form13FOtherManager2,
        'INFOTABLE.tsv': Form13FInfoTable,
    }

    date_columns = [
        'filing_date', 'period_of_report', 'report_calendar_or_quarter',
        'date_denied_expired', 'date_reported', 'signature_date'
    ]
    numeric_columns = [
        'amendment_no', 'other_included_managers_count', 'table_entry_total',
        'table_value_total', 'value', 'sshprnamt', 'voting_auth_sole',
        'voting_auth_shared', 'voting_auth_none'
    ]

    try:
        for zip_file in zip_files:
            logging.info(f"Processing Form 13F file: {zip_file}")
            try:
                with ZipFile(zip_file, 'r') as zip_ref:
                    for file_name, model in table_map.items():
                        if file_name in zip_ref.namelist():
                            with zip_ref.open(file_name) as table_file:
                                df = pd.read_csv(table_file, sep='\t', low_memory=False, dtype=str)
                                df = sanitize_column_names(df)

                                # Manual column name corrections for 13F data
                                column_renames = {
                                    'submissiontype': 'submission_type',
                                    'periodofreport': 'period_of_report',
                                    'reportcalendarorquarter': 'report_calendar_or_quarter',
                                    'is_amendment': 'is_amendment',
                                    'amendmentno': 'amendment_no',
                                    'amendmenttype': 'amendment_type',
                                    'datedeniedexpired': 'date_denied_expired',
                                    'datereported': 'date_reported',
                                    'filingmanager_name': 'filing_manager_name',
                                    'filingmanager_street1': 'filing_manager_street1',
                                    'filingmanager_street2': 'filing_manager_street2',
                                    'filingmanager_city': 'filing_manager_city',
                                    'filingmanager_stateorcountry': 'filing_manager_state_or_country',
                                    'filingmanager_zipcode': 'filing_manager_zipcode',
                                    'reporttype': 'report_type',
                                    'form13ffilenumber': 'form13f_file_number',
                                    'provideinfoforinstruction5': 'provide_info_for_instruction5',
                                    'additionalinformation': 'additional_information',
                                    'othermanagersk': 'other_manager_sk',
                                    'sequencenumber': 'sequence_number',
                                    'nameofissuer': 'nameofissuer',
                                    'titleofclass': 'titleofclass',
                                    'sshprnamt': 'sshprnamt',
                                    'sshprnamttype': 'sshprnamttype',
                                    'putcall': 'putcall',
                                    'investmentdiscretion': 'investmentdiscretion',
                                    'othermanager': 'othermanager',
                                    'voting_auth_sole': 'voting_auth_sole',
                                    'voting_auth_shared': 'voting_auth_shared',
                                    'voting_auth_none': 'voting_auth_none',
                                    'signaturedate': 'signature_date',
                                }
                                df.rename(columns=column_renames, inplace=True)

                                for col in date_columns:
                                    if col in df.columns:
                                        df[col] = pd.to_datetime(df[col], format='%d-%b-%Y', errors='coerce')
                                
                                for col in numeric_columns:
                                    if col in df.columns:
                                        df[col] = pd.to_numeric(df[col], errors='coerce')

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
