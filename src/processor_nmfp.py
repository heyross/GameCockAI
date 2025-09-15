"""
N-MFP (Form N-MFP) Processor Module

This module handles processing of N-MFP filing data from ZIP archives.
N-MFP is the monthly portfolio holdings report for money market funds.
"""

import glob
import logging
import os
import pandas as pd
from zipfile import ZipFile
from database import (
    NMFPSubmission, NMFPFund, NMFPSeriesLevelInfo, NMFPMasterFeederFund, NMFPAdviser,
    NMFPAdministrator, NMFPTransferAgent, NMFPSeriesShadowPriceL, NMFPClassLevelInfo,
    NMFPNetAssetValuePerShareL, NMFPSchPortfolioSecurities, NMFPCollateralIssuers,
    NMFPNrsro, NMFPDemandFeature, NMFPGuarantor, NMFPEnhancementProvider,
    NMFPLiquidAssetsDetails, NMFPSevenDayGrossYield, NMFPDlyNetAssetValuePerShars,
    NMFPLiquidityFeeReportingPer, NMFPDlyNetAssetValuePerSharc, NMFPDlyShareholderFlowReport,
    NMFPSevenDayNetYield, NMFPBeneficialRecordOwnerCat, NMFPCancelledSharesPerBusDay,
    NMFPDispositionOfPortfolioSecurities, SessionLocal
)

logger = logging.getLogger(__name__)

def sanitize_column_names(df):
    """Sanitizes DataFrame column names to be valid Python identifiers."""
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
    df.columns = df.columns.str.replace(r'^_+|_+$', '', regex=True)
    df.columns = [''.join(c if c.isalnum() or c == '_' else '_' for c in col) for col in df.columns]
    return df

def process_nmfp_data(source_dir, db_session=None):
    """Processes Form N-MFP data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))
    db = db_session if db_session else SessionLocal()

    # Simplified table mapping for core N-MFP tables
    table_map = {
        'SUBMISSION.tsv': NMFPSubmission,
        'FUND.tsv': NMFPFund,
        'SERIESLEVELINFO.tsv': NMFPSeriesLevelInfo,
        'ADVISER.tsv': NMFPAdviser,
        'ADMINISTRATOR.tsv': NMFPAdministrator,
        'TRANSFERAGENT.tsv': NMFPTransferAgent,
    }

    # Column mapping for N-MFP data
    column_maps = {
        'SUBMISSION.tsv': {
            'ACCESSION_NUMBER': 'accession_number',
            'FILING_DATE': 'filing_date', 
            'SUBMISSIONTYPE': 'submission_type',
            'CIK': 'cik',
            'REPORTDATE': 'report_date',
            'FILER_CIK': 'filer_cik',
            'SERIESID': 'seriesid',
            'TOTALSHARECLASSESINSERIES': 'total_share_classes_in_series',
            'FINALFILINGFLAG': 'final_filing_flag'
        },
        'SERIESLEVELINFO.tsv': {
            'ACCESSION_NUMBER': 'accession_number',
            'FEEDERFUNDFLAG': 'feeder_fund_flag',
            'MASTERFUNDFLAG': 'master_fund_flag',
            'MONEYMARKETFUNDCATEGORY': 'money_market_fund_category',
            'AVERAGEPORTFOLIOMATURITY': 'average_portfolio_maturity',
            'AVERAGELIFEMATURITY': 'average_life_maturity',
            'TOTALVALUEOTHERASSETS': 'total_value_other_assets',
            'TOTALVALUELIABILITIES': 'total_value_liabilities',
            'NETASSETOFSERIES': 'net_asset_of_series',
            'SEVENDAYGROSSYIELD': 'seven_day_gross_yield'
        }
    }

    date_columns = ['filing_date', 'report_date', 'signature_date']
    numeric_columns = [
        'total_share_classes_in_series', 'average_portfolio_maturity', 'average_life_maturity',
        'cash', 'total_value_portfolio_securities', 'amortized_cost_portfolio_securiti', 
        'total_value_other_assets', 'total_value_liabilities', 'net_asset_of_series',
        'number_of_shares_outstanding', 'stable_price_per_share', 'seven_day_gross_yield'
    ]

    try:
        for zip_file in zip_files:
            logging.info(f"Processing Form N-MFP file: {zip_file}")
            try:
                with ZipFile(zip_file, 'r') as zip_ref:
                    for file_name, model in table_map.items():
                        if file_name in zip_ref.namelist():
                            with zip_ref.open(file_name) as table_file:
                                df = pd.read_csv(table_file, sep='\t', low_memory=False, dtype=str)
                                
                                # Apply column mapping if available
                                if file_name in column_maps:
                                    df.rename(columns=column_maps[file_name], inplace=True)

                                # Convert data types
                                for col in df.columns:
                                    if col in date_columns:
                                        df[col] = pd.to_datetime(df[col], errors='coerce')
                                    elif col in numeric_columns:
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
