import glob
import logging
import os
import pandas as pd
from zipfile import ZipFile
from downloader import extract_formd_filings
from config import FORMD_SOURCE_DIR
from database import (
    SessionLocal, CFTCSwap, SecSubmission, SecReportingOwner, SecNonDerivTrans, SecNonDerivHolding,
    SecDerivTrans, SecDerivHolding, SecFootnote, SecOwnerSignature, Form13FSubmission,
    Form13FCoverPage, Form13FOtherManager, Form13FSignature, Form13FSummaryPage,
    Form13FOtherManager2, Form13FInfoTable, SecExchangeMetrics, NCENSubmission,
    NCENRegistrant, NCENFundReportedInfo, NCENAdviser, NPORTSubmission, NPORTGeneralInfo,
    NPORTHolding, NPORTDerivative, NMFPSubmission, NMFPFund, NMFPSeriesLevelInfo,
    FormDSubmission, FormDIssuer, FormDOffering, FormDRecipient, FormDRelatedPerson,
    FormDSignature, NMFPAdministrator, NMFPTransferAgent, NMFPSeriesShadowPriceL, NMFPClassLevelInfo,
    NMFPNetAssetValuePerShareL, NMFPSchPortfolioSecurities, NMFPCollateralIssuers,
    NMFPNrsro, NMFPDemandFeature, NMFPGuarantor, NMFPEnhancementProvider,
    NMFPLiquidAssetsDetails, NMFPSevenDayGrossYield, NMFPDlyNetAssetValuePerShars,
    NMFPLiquidityFeeReportingPer, NMFPDlyNetAssetValuePerSharc, NMFPDlyShareholderFlowReport,
    NMFPSevenDayNetYield, NMFPBeneficialRecordOwnerCat, NMFPCancelledSharesPerBusDay,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_zip_files(source_dir, target_companies=None, search_term=None, load_to_db=False):
    """
    Processes data from zip files and optionally loads it into the database.
    
    Args:
        source_dir: Directory containing zip files to process
        target_companies: Optional list of target companies to filter by
        search_term: Optional search term to filter data
        load_to_db: If True, loads the data into the database. Default is False.
        
    Returns:
        DataFrame containing the processed data, or None if no data was found
    """
    zip_files = sorted(glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True))
    chunk_size = 100000  # Process 100,000 rows at a time
    all_data = []

    for zip_file in zip_files:
        try:
            with ZipFile(zip_file, 'r') as zip_ref:
                for csv_filename in zip_ref.namelist():
                    if not csv_filename.endswith('.csv'):
                        continue

                    with zip_ref.open(csv_filename) as csv_file:
                        # Use chunksize to read the CSV in parts
                        for chunk_df in pd.read_csv(csv_file, chunksize=chunk_size, low_memory=False):
                            # Make a copy to avoid modifying the original
                            chunk_df = chunk_df.copy()
                            
                            # Filter by target companies if a list is provided and a CIK column exists
                            if target_companies:
                                target_ciks = {str(c['cik_str']) for c in target_companies}
                                cik_col = next((col for col in chunk_df.columns if 'cik' in col.lower()), None)

                                if cik_col:
                                    chunk_df[cik_col] = chunk_df[cik_col].astype(str).str.zfill(10)
                                    chunk_df = chunk_df[chunk_df[cik_col].isin(target_ciks)]
                                    if chunk_df.empty:
                                        continue
                                else:
                                    logging.warning(f"No CIK column in {csv_filename}, processing all data.")

                            if search_term:
                                mask = chunk_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
                                chunk_df = chunk_df[mask]
                            
                            if not chunk_df.empty:
                                if load_to_db:
                                    load_cftc_data_to_db(chunk_df)
                                all_data.append(chunk_df)

        except Exception as e:
            logging.error(f"Error processing {zip_file}: {e}")
    
    # Combine all chunks into a single DataFrame if any data was found
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return None

def process_sec_insider_data(source_dir, db_session=None):
    """Processes SEC insider trading data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True))
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
        db.close()

def process_form13f_data(source_dir, db_session=None):
    """Processes Form 13F data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True))
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

                                # Convert all NaN values to None for database insertion
                                # Use replace to handle both NaN and NaT values properly
                                import numpy as np
                                df = df.replace({np.nan: None, pd.NaT: None})
                                records = df.to_dict(orient='records')
                                db.bulk_insert_mappings(model, records)
                                logging.info(f"Loading {len(records)} records into {model.__tablename__}")
                db.commit()
            except Exception as e:
                logging.error(f"Error processing file {zip_file}: {e}")
                db.rollback()
    finally:
        if not db_session:
            db.close()

def process_exchange_metrics_data(source_dir, db_session=None):
    """Processes SEC Exchange Metrics data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True))
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


def process_formd_data(source_dir, db_session=None):
    """
    Process Form D data by extracting quarterly archives and loading TSV files into database.
    """
    logging.info("Starting processing of Form D data...")
    
    # Get all zip files in the source directory
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))
    
    if not zip_files:
        logging.warning(f"No zip files found in {source_dir}")
        return
    
    # Extract each archive first
    for zip_file in zip_files:
        logging.info(f"Processing archive: {zip_file}")
        extract_formd_filings(zip_file)
    
    # Now process the extracted quarterly directories
    db = db_session if db_session else SessionLocal()
    try:
        # Find all quarterly directories
        quarterly_dirs = []
        for item in os.listdir(source_dir):
            item_path = os.path.join(source_dir, item)
            if os.path.isdir(item_path) and item.endswith('_d'):
                quarterly_dirs.append(item_path)
        
        quarterly_dirs.sort()
        
        for quarter_dir in quarterly_dirs:
            logging.info(f"Processing quarterly data from: {quarter_dir}")
            process_formd_quarter(quarter_dir, db)
            
        db.commit()
        logging.info("Finished processing all Form D data.")
        
    except Exception as e:
        logging.error(f"Error processing Form D data: {e}")
        db.rollback()
        raise
    finally:
        if not db_session:
            db.close()

def process_formd_quarter(quarter_dir, db_session):
    """
    Process TSV files from a single quarterly directory.
    """
    # Define the table mapping for Form D TSV files
    table_map = {
        'FORMDSUBMISSION.tsv': FormDSubmission,
        'ISSUERS.tsv': FormDIssuer,
        'OFFERING.tsv': FormDOffering,
        'RECIPIENTS.tsv': FormDRecipient,
        'RELATEDPERSONS.tsv': FormDRelatedPerson,
        'SIGNATURES.tsv': FormDSignature
    }
    
    # Find the actual quarterly subdirectory (e.g., 2024Q3_d)
    quarter_subdir = None
    for item in os.listdir(quarter_dir):
        item_path = os.path.join(quarter_dir, item)
        if os.path.isdir(item_path):
            quarter_subdir = item_path
            break
    
    if not quarter_subdir:
        logging.warning(f"No quarterly subdirectory found in {quarter_dir}")
        return
    
    # Process each TSV file
    for file_name, model in table_map.items():
        file_path = os.path.join(quarter_subdir, file_name)
        
        if not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            continue
            
        logging.info(f"Processing {file_name}...")
        
        try:
            # Read TSV file
            df = pd.read_csv(file_path, sep='\t', low_memory=False, 
                           dtype=str, na_values=['', 'nan', 'NaN', 'NULL'])
            
            if df.empty:
                logging.info(f"No data found in {file_name}")
                continue
            
            # Sanitize column names to match database schema
            sanitized_columns = df.columns.str.strip().str.lower()
            sanitized_columns = sanitized_columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
            df.columns = sanitized_columns
            
            # Convert DataFrame to records and bulk insert
            records = df.to_dict('records')
            
            # Handle special cases for different tables
            if model == FormDIssuer:
                # Add auto-increment key for issuers
                for i, record in enumerate(records):
                    record.pop('formd_issuer_sk', None)  # Remove if exists
            elif model == FormDOffering:
                # Add auto-increment key for offerings
                for i, record in enumerate(records):
                    record.pop('formd_offering_sk', None)
            elif model == FormDRecipient:
                # Add auto-increment key for recipients
                for i, record in enumerate(records):
                    record.pop('formd_recipient_sk', None)
            elif model == FormDRelatedPerson:
                # Add auto-increment key for related persons
                for i, record in enumerate(records):
                    record.pop('formd_related_person_sk', None)
            elif model == FormDSignature:
                # Add auto-increment key for signatures
                for i, record in enumerate(records):
                    record.pop('formd_signature_sk', None)
            
            # Bulk insert records
            if records:
                db_session.bulk_insert_mappings(model, records)
                logging.info(f"Inserted {len(records)} records from {file_name}")
            
        except Exception as e:
            logging.error(f"Error processing {file_name}: {e}")
            continue

def process_nmfp_data(source_dir, db_session=None):
    """Processes Form N-MFP data from zip files and loads it into the database."""
    zip_files = sorted(glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True))
    db = db_session if db_session else SessionLocal()

    column_maps = {
        'SUBMISSION.tsv': {'ACCESSION_NUMBER': 'accession_number', 'FILING_DATE': 'filing_date', 'SUBMISSIONTYPE': 'submission_type', 'CIK': 'cik', 'REPORTDATE': 'report_date', 'REGISTRANTFULLNAME': 'registrant_full_name', 'FILER_CIK': 'filer_cik', 'REGISTRANTLEIID': 'registrant_leiid', 'SERIES_NAME': 'series_name', 'NAMEOFSERIES': 'nameofseries', 'LEIOFSERIES': 'leiofseries', 'SERIESID': 'seriesid', 'TOTALSHARECLASSESINSERIES': 'total_share_classes_in_series', 'FINALFILINGFLAG': 'final_filing_flag', 'FUNDLIQUIDATINGFLAG': 'fund_liquidating_flag', 'FUNDMRGORACQRDBYOTHRFLAG': 'fund_mrg_or_acqrd_by_othr_flag', 'FUNDACQRDORMRGDWTHANTHRFLAG': 'fund_acqrd_or_mrgd_wth_anthr_flag', 'REGISTRANT': 'registrant', 'SIGNATUREDATE': 'signature_date', 'SIGNATURE': 'signature', 'NAMEOFSIGNINGOFFICER': 'nameofsigning_officer', 'TITLEOFSIGNINGOFFICER': 'titleofsigning_officer'},
        'FUND.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CIK': 'cik', 'FILENUMBER': 'file_number', 'SERIESID': 'seriesid', 'FUND_TYPE': 'fund_type'},
        'SERIESLEVELINFO.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SECURITIESACTFILENUMBER': 'securities_act_file_number', 'INDPPUBACCTNAME': 'ind_pub_acct_name', 'INDPPUBACCTCITY': 'ind_pub_acct_city', 'INDPPUBACCTSTATECOUNTRY': 'ind_pub_acct_state_country', 'FEEDERFUNDFLAG': 'feeder_fund_flag', 'MASTERFUNDFLAG': 'master_fund_flag', 'SERIESFUNDINSUCMPNYSEPACCNTFLA': 'series_fund_insu_cmpny_sep_accnt_fla', 'MONEYMARKETFUNDCATEGORY': 'money_market_fund_category', 'FUNDEXEMPTRETAILFLAG': 'fund_exempt_retail_flag', 'FUNDRETAILMONEYMARKETFLAG': 'fund_retail_money_market_flag', 'GOVMONEYMRKTFUNDFLAG': 'gov_money_mrkt_fund_flag', 'AVERAGEPORTFOLIOMATURITY': 'average_portfolio_maturity', 'AVERAGELIFEMATURITY': 'average_life_maturity', 'TOTDLYLIQUIDASSETFRIDAYWEEK1': 'tot_dly_liquid_asset_friday_week1', 'TOTDLYLIQUIDASSETFRIDAYWEEK2': 'tot_dly_liquid_asset_friday_week2', 'TOTDLYLIQUIDASSETFRIDAYWEEK3': 'tot_dly_liquid_asset_friday_week3', 'TOTDLYLIQUIDASSETFRIDAYWEEK4': 'tot_dly_liquid_asset_friday_week4', 'TOTDLYLIQUIDASSETFRIDAYWEEK5': 'tot_dly_liquid_asset_friday_week5', 'TOTWLYLIQUIDASSETFRIDAYWEEK1': 'tot_wly_liquid_asset_friday_week1', 'TOTWLYLIQUIDASSETFRIDAYWEEK2': 'tot_wly_liquid_asset_friday_week2', 'TOTWLYLIQUIDASSETFRIDAYWEEK3': 'tot_wly_liquid_asset_friday_week3', 'TOTWLYLIQUIDASSETFRIDAYWEEK4': 'tot_wly_liquid_asset_friday_week4', 'TOTWLYLIQUIDASSETFRIDAYWEEK5': 'tot_wly_liquid_asset_friday_week5', 'PCTDLYLIQUIDASSETFRIDAYWEEK1': 'pct_dly_liquid_asset_friday_week1', 'PCTDLYLIQUIDASSETFRIDAYWEEK2': 'pct_dly_liquid_asset_friday_week2', 'PCTDLYLIQUIDASSETFRIDAYWEEK3': 'pct_dly_liquid_asset_friday_week3', 'PCTDLYLIQUIDASSETFRIDAYWEEK4': 'pct_dly_liquid_asset_friday_week4', 'PCTDLYLIQUIDASSETFRIDAYWEEK5': 'pct_dly_liquid_asset_friday_week5', 'PCTWKLYLIQUIDASSETFRIDAYWEEK1': 'pct_wkly_liquid_asset_friday_week1', 'PCTWKLYLIQUIDASSETFRIDAYWEEK2': 'pct_wkly_liquid_asset_friday_week2', 'PCTWKLYLIQUIDASSETFRIDAYWEEK3': 'pct_wkly_liquid_asset_friday_week3', 'PCTWKLYLIQUIDASSETFRIDAYWEEK4': 'pct_wkly_liquid_asset_friday_week4', 'PCTWKLYLIQUIDASSETFRIDAYWEEK5': 'pct_wkly_liquid_asset_friday_week5', 'CASH': 'cash', 'TOTALVALUEPORTFOLIOSECURITIES': 'total_value_portfolio_securities', 'AMORTIZEDCOSTPORTFOLIOSECURITI': 'amortized_cost_portfolio_securiti', 'TOTALVALUEOTHERASSETS': 'total_value_other_assets', 'TOTALVALUELIABILITIES': 'total_value_liabilities', 'NETASSETOFSERIES': 'net_asset_of_series', 'NUMBEROFSHARESOUTSTANDING': 'number_of_shares_outstanding', 'SEEKSSTABLEPRICEPERSHARE': 'seeks_stable_price_per_share', 'STABLEPRICEPERSHARE': 'stable_price_per_share', 'SEVENDAYGROSSYIELD': 'seven_day_gross_yield', 'NETASSETVALUEFRIDAYWEEK1': 'net_asset_value_friday_week1', 'NETASSETVALUEFRIDAYWEEK2': 'net_asset_value_friday_week2', 'NETASSETVALUEFRIDAYWEEK3': 'net_asset_value_friday_week3', 'NETASSETVALUEFRIDAYWEEK4': 'net_asset_value_friday_week4', 'NETASSETVALUEFRIDAYWEEK5': 'net_asset_value_friday_week5', 'CASHMGMTVEHICLEAFFLIATEDFUNDF': 'cash_mgmt_vehicle_affliated_fund_f', 'LIQUIDITYFEEFUNDAPPLYFLAG': 'liquidity_fee_fund_apply_flag'},
        'MASTERFEEDERFUND.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CIK': 'cik', 'NAME': 'name', 'FILENUMBER': 'file_number', 'SERIESID': 'seriesid', 'FUND_TYPE': 'fund_type'},
        'ADVISER.tsv': {'ACCESSION_NUMBER': 'accession_number', 'ADVISERNAME': 'adviser_name', 'ADVISERFILENUMBER': 'adviser_file_number', 'ADVISER_TYPE': 'adviser_type'},
        'ADMINISTRATOR.tsv': {'ACCESSION_NUMBER': 'accession_number', 'ADMINISTRATORNAME': 'administrator_name'},
        'TRANSFERAGENT.tsv': {'ACCESSION_NUMBER': 'accession_number', 'NAME': 'name', 'CIK': 'cik', 'FILENUMBER': 'file_number'},
        'SERIESSHADOWPRICE_L.tsv': {'ACCESSION_NUMBER': 'accession_number', 'NETVALUEPERSHAREINCLUDINGCAPIT': 'net_value_per_share_including_capit', 'NETVALUEPERSHAREINCAPCALCDATE': 'net_value_per_share_incap_calc_date', 'NETVALUEPERSHAREEXCLUDINGCAPIT': 'net_value_per_share_excluding_capit', 'NETVALUEPERSHAREEXCAPCALCDATE': 'net_value_per_share_excap_calc_date'},
        'CLASSLEVELINFO.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CLASS_NAME': 'class_name', 'CLASSFULLNAME': 'class_full_name', 'CLASSESID': 'classesid', 'MININITIALINVESTMENT': 'min_initial_investment', 'NETASSETSOFCLASS': 'net_assets_of_class', 'NUMBEROFSHARESOUTSTANDING': 'number_of_shares_outstanding', 'NETASSETPERSHAREFRIDAYWEEK1': 'net_asset_per_share_friday_week1', 'NETASSETPERSHAREFRIDAYWEEK2': 'net_asset_per_share_friday_week2', 'NETASSETPERSHAREFRIDAYWEEK3': 'net_asset_per_share_friday_week3', 'NETASSETPERSHAREFRIDAYWEEK4': 'net_asset_per_share_friday_week4', 'NETASSETPERSHAREFRIDAYWEEK5': 'net_asset_per_share_friday_week5', 'GROSSSUBSCRIPTIONFRIDAYWEEK1': 'gross_subscription_friday_week1', 'GROSSREDEMPTIONFRIDAYWEEK1': 'gross_redemption_friday_week1', 'GROSSSUBSCRIPTIONFRIDAYWEEK2': 'gross_subscription_friday_week2', 'GROSSREDEMPTIONFRIDAYWEEK2': 'gross_redemption_friday_week2', 'GROSSSUBSCRIPTIONFRIDAYWEEK3': 'gross_subscription_friday_week3', 'GROSSREDEMPTIONFRIDAYWEEK3': 'gross_redemption_friday_week3', 'GROSSSUBSCRIPTIONFRIDAYWEEK4': 'gross_subscription_friday_week4', 'GROSSREDEMPTIONFRIDAYWEEK4': 'gross_redemption_friday_week4', 'GROSSSUBSCRIPTIONFRIDAYWEEK5': 'gross_subscription_friday_week5', 'GROSSREDEMPTIONFRIDAYWEEK5': 'gross_redemption_friday_week5', 'TOTFORMNTHWLYGROSSSUBSCRIPTION': 'tot_form_nthwly_gross_subscription', 'TOTALGROSSSUBSCRIPTIONS': 'total_gross_subscriptions', 'TOTFORMNTHWLYGROSSREDEMPTION': 'tot_form_nthwly_gross_redemption', 'TOTALGROSSREDEMPTIONS': 'total_gross_redemptions', 'NETASSETVALUEPERSHARE_L': 'net_asset_value_per_share_l', 'NETSHAREHOLDERFLOWACTIVITYFO_L': 'net_shareholder_flow_activity_fo_l', 'SEVENDAYNETYIELD': 'seven_day_net_yield', 'PERSONPAYFORFUNDFLAG': 'person_pay_for_fund_flag', 'NAMEOFPERSONDESCEXPENSEPAY': 'name_of_person_desc_expense_pay', 'NAMEOFPERSONDESCEXPENSEPAY_AMOUNT': 'name_of_person_desc_expense_pay_amount', 'PCTSHAREHOLDERCOMPNONFINANCIAL': 'pct_shareholder_comp_non_financial', 'PCTSHAREHOLDERCOMPPENSIONPLAN': 'pct_shareholder_comp_pension_plan', 'PCTSHAREHOLDERCOMPNONPROFIT': 'pct_shareholder_comp_non_profit', 'PCTSHAREHOLDERCOMPMUNICIPAL': 'pct_shareholder_comp_municipal', 'PCTSHAREHOLDERCOMPREGINVESTME': 'pct_shareholder_comp_reg_investme', 'PCTSHAREHOLDERCOMPPRIVATEFUND': 'pct_shareholder_comp_private_fund', 'PCTSHAREHOLDERCOMPDEPOSITORYI': 'pct_shareholder_comp_depository_i', 'PCTSHAREHOLDERCOMPSOVEREIGNFU': 'pct_shareholder_comp_sovereign_fu', 'PCTSHAREHOLDERCOMPBROKERDEALE': 'pct_shareholder_comp_broker_deale', 'PCTSHAREHOLDERCOMPINSURANCE': 'pct_shareholder_comp_insurance', 'PCTSHAREHOLDERCOMPOTHER': 'pct_shareholder_comp_other', 'OTHERINVESTORTYPEDESCRIPTION': 'other_investor_type_description', 'SHARECANCELLATIONREPORTPERIOD': 'share_cancellation_report_period'},
        'NETASSETVALUEPERSHARE_L.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CLASSESID': 'classesid', 'VALUE': 'value', 'DATEASOFWHICHVALUEWASCALCULATE': 'date_as_of_which_value_was_calculate', 'TYPE': 'type'},
        'SCHPORTFOLIOSECURITIES.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SECURITY_ID': 'security_id', 'NAMEOFISSUER': 'name_of_issuer', 'TITLEOFISSUER': 'title_of_issuer', 'COUPON': 'coupon', 'CUSIP_NUMBER': 'cusip_number', 'LEI': 'lei', 'ISIN': 'isin', 'CIK': 'cik', 'RSSDID': 'rssdid', 'OTHERUNIQUEID': 'other_unique_id', 'INVESTMENTCATEGORY': 'investment_category', 'BRIEFDESCRIPTION': 'brief_description', 'FUNDACQSTNUNDRLYNGSECURITYFLAG': 'fund_acqstn_undrlyng_security_flag', 'REPURCHASEAGREEMENTOPENFLAG': 'repurchase_agreement_open_flag', 'REPURCHASEAGREEMENTCLEAREDFLA': 'repurchase_agreement_cleared_fla', 'NAMEOFCCP': 'name_of_ccp', 'REPURCHASEAGREEMENTTRIPARTYFL': 'repurchase_agreement_triparty_fl', 'SECURITYELIGIBILITYFLAG': 'security_eligibility_flag', 'INVESTMENTMATURITYDATEWAM': 'investment_maturity_date_wam', 'INVESTMENTMATURITYDATEWAL': 'investment_maturity_date_wal', 'FINALLEGALINVESTMENTMATURITYDA': 'final_legal_investment_maturity_da', 'SECURITYDEMANDFEATUREFLAG': 'security_demand_feature_flag', 'SECURITYGUARANTEEFLAG': 'security_guarantee_flag', 'SECURITYENHANCEMENTSFLAG': 'security_enhancements_flag', 'YIELDOFTHESECURITYASOFREPORTIN': 'yield_of_the_security_as_of_reportin', 'INCLUDINGVALUEOFANYSPONSORSUPP': 'including_value_of_any_sponsor_supp', 'EXCLUDINGVALUEOFANYSPONSORSUPP': 'excluding_value_of_any_sponsor_supp', 'PERCENTAGEOFMONEYMARKETFUNDNET': 'percentage_of_money_market_fund_net', 'SECURITYCATEGORIZEDATLEVEL3FLA': 'security_categorized_at_level3_fla', 'DAILYLIQUIDASSETSECURITYFLAG': 'daily_liquid_asset_security_flag', 'WEEKLYLIQUIDASSETSECURITYFLAG': 'weekly_liquid_asset_security_flag', 'ILLIQUIDSECURITYFLAG': 'illiquid_security_flag', 'EXPLANATORYNOTES': 'explanatory_notes', 'RATING_L': 'rating_l', 'INVESTMENTOWNEDBALANCEPRINCI_L': 'investment_owned_balance_princi_l', 'AVAILABLEFORSALESECURITIESAM_L': 'available_for_sale_securities_am_l'},
        'COLLATERALISSUERS.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SECURITY_ID': 'security_id', 'NAMEOFCOLLATERALISSUER': 'name_of_collateral_issuer', 'LEI': 'lei', 'CUSIPMEMBER': 'cusip_member', 'COLLATERALMATURITYDATE': 'collateral_maturity_date', 'TFROM': 't_from', 'TTO': 't_to', 'COUPONORYIELD': 'coupon_or_yield', 'COUPON': 'coupon', 'YIELD': 'yield_', 'PRINCIPALAMOUNTTOTHENEARESTCEN': 'principal_amount_to_the_nearest_cen', 'VALUEOFCOLLATERALTOTHENEARESTC': 'value_of_collateral_to_the_nearest_c', 'CTGRYINVESTMENTSRPRSNTSCOLLATE': 'ctgry_investments_rprsnts_collate', 'OTHERINSTRUMENTBRIEFDESC': 'other_instrument_brief_desc'},
        'NRSRO.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SECURITY_ID': 'security_id', 'IDENTITY': 'identity', 'TYPE': 'type', 'NAMEOFNRSRO': 'name_of_nrsro', 'RATING': 'rating'},
        'DEMANDFEATURE.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SECURITY_ID': 'security_id', 'IDENTITYOFDEMANDFEATUREISSUER': 'identity_of_demand_feature_issuer', 'AMOUNTPROVIDEDBYDEMANDFEATUREI': 'amount_provided_by_demand_feature_i', 'REMAININGPERIODDEMANDFEATURE': 'remaining_period_demand_feature', 'DEMANDFEATURECONDITIONALFLAG': 'demand_feature_conditional_flag'},
        'GUARANTOR.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SECURITY_ID': 'security_id', 'IDENTITYOFTHEGUARANTOR': 'identity_of_the_guarantor', 'AMOUNTPROVIDEDBYGUARANTOR': 'amount_provided_by_guarantor'},
        'ENHANCEMENTPROVIDER.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SECURITY_ID': 'security_id', 'IDENTITYOFENHANCEMENTPROVIDER': 'identity_of_enhancement_provider', 'TYPEOFENHANCEMENT': 'type_of_enhancement', 'AMOUNTPROVIDEDBYENHANCEMENT': 'amount_provided_by_enhancement'},
        'LIQUIDASSETSDETAILS.tsv': {'ACCESSION_NUMBER': 'accession_number', 'TOTVALUEDAILYLIQUIDASSETS': 'tot_value_daily_liquid_assets', 'TOTVALUEWEEKLYLIQUIDASSETS': 'tot_value_weekly_liquid_assets', 'PCTDAILYLIQUIDASSETS': 'pct_daily_liquid_assets', 'PCTWEEKLYLIQUIDASSETS': 'pct_weekly_liquid_assets', 'TOTLIQUIDASSETSNEARPCTDATE': 'tot_liquid_assets_near_pct_date'},
        'SEVENDAYGROSSYIELD.tsv': {'ACCESSION_NUMBER': 'accession_number', 'SEVENDAYGROSSYIELDVALUE': 'seven_day_gross_yield_value', 'SEVENDAYGROSSYIELDDATE': 'seven_day_gross_yield_date'},
        'DLYNETASSETVALUEPERSHARS.tsv': {'ACCESSION_NUMBER': 'accession_number', 'DLYNETASSETVALUEPERSHARESER': 'dly_net_asset_value_per_share_ser', 'DLYNETASSETVALPERSHAREDATES': 'dly_net_asset_val_per_share_dates'},
        'LIQUIDITYFEEREPORTINGPER.tsv': {'ACCESSION_NUMBER': 'accession_number', 'LIQUIDITYFEEAPPLYDATE': 'liquidity_fee_apply_date', 'LIQUIDITYFEETYPEFORREPTNGPERI': 'liquidity_fee_type_for_reptng_peri', 'LIQUIDITYFEEAMTAPPLYTOREDEMPT': 'liquidity_fee_amt_apply_to_redempt', 'LIQUIDITYFEEPCTSHARESREDEEMED': 'liquidity_fee_pct_shares_redeemed'},
        'DLYNETASSETVALUEPERSHARC.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CLASSESID': 'classesid', 'DLYNETASSETVALUEPERSHARECLASS': 'dly_net_asset_value_per_share_class', 'DLYNETASSETVALUEPERSHAREDATEC': 'dly_net_asset_value_per_share_datec'},
        'DLYSHAREHOLDERFLOWREPORT.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CLASSESID': 'classesid', 'DAILYGROSSSUBSCRIPTIONS': 'daily_gross_subscriptions', 'DAILYGROSSREDEMPTIONS': 'daily_gross_redemptions', 'DAILYSHAREHOLDERFLOWDATE': 'daily_shareholder_flow_date'},
        'SEVENDAYNETYIELD.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CLASSESID': 'classesid', 'SEVENDAYNETYIELDVALUE': 'seven_day_net_yield_value', 'SEVENDAYNETYIELDDATE': 'seven_day_net_yield_date'},
        'BENEFICIALRECORDOWNERCAT.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CLASSESID': 'classesid', 'BENEFICIALRECORDOWNERCATETYPE': 'beneficial_record_owner_cate_type', 'OTHERINVESTORCATEGORY': 'other_investor_category', 'PCTOUTSTANDINGSHARESRECORD': 'pct_outstanding_shares_record', 'PCTOUTSTANDINGSHARESBENEFICIA': 'pct_outstanding_shares_beneficia'},
        'CANCELLEDSHARESPERBUSDAY.tsv': {'ACCESSION_NUMBER': 'accession_number', 'CLASSESID': 'classesid', 'CANCELLEDSHAREDOLLARVALUE': 'cancelled_share_dollar_value', 'CANCELLEDSHARENUMBER': 'cancelled_share_number', 'CANCELLEDSHAREDATE': 'cancelled_share_date'},
        'DISPOSITIONOFPORTFOLIOSE.tsv': {'ACCESSION_NUMBER': 'accession_number', 'DEPOSITIONUSTREASURYDEBTAMT': 'deposition_us_treasury_debt_amt', 'GOVTAGENCYCOUPONPAYINGDEBTAMT': 'gov_t_agency_coupon_paying_debt_amt', 'GOVTAGENONCOUPONPAYINGDEBTAMT': 'gov_t_agen_on_coupon_paying_debt_amt', 'NONUSSOVEREIGNSUPRANATDEBTAMT': 'non_us_sovereign_supranat_debt_amt', 'CERTIFICATEDEPOSITAMT': 'certificate_deposit_amt', 'NONNEGOTIABLETIMEDEPOSITAMT': 'non_negotiable_time_deposit_amt', 'VARIABLERATEDEMANDNOTEAMT': 'variable_rate_demand_note_amt', 'OTHERMUNICIPALSECURITYAMT': 'other_municipal_security_amt', 'ASSETBACKEDCOMMERCIALPAPERAMT': 'asset_backed_commercial_paper_amt', 'OTHERASSETBACKEDSECURITIESAMT': 'other_asset_backed_securities_amt', 'USTREASURYREPURCHASEAGREEMAMT': 'us_treasury_repurchase_agreem_amt', 'USGOVTAGENCYREPURCHASEAGREAMT': 'us_govt_agency_repurchase_agreamt', 'OTHERREPURCHASEAGREEMENTAMT': 'other_repurchase_agreement_amt', 'INSURANCECOMPANYFUNDAGREEMAMT': 'insurance_company_fund_agreem_amt', 'INVESTMENTCOMPANYAMT': 'investment_company_amt', 'FINANCIALCOMPANYCOMMERCIALAMT': 'financial_company_commercial_amt', 'NONFINANCIALCOMPCOMMERCIALAMT': 'non_financial_comp_commercial_amt', 'TENDEROPTIONBONDAMT': 'tender_option_bond_amt', 'OTHERINSTRUMENTAMT': 'other_instrument_amt', 'OTHERINSTRUMENTBRIEFDESCRIPTI': 'other_instrument_brief_descripti'},
    }

    table_map = {
        'SUBMISSION.tsv': NMFPSubmission,
        'FUND.tsv': NMFPFund,
        'SERIESLEVELINFO.tsv': NMFPSeriesLevelInfo,
        'MASTERFEEDERFUND.tsv': NMFPMasterFeederFund,
        'ADVISER.tsv': NMFPAdviser,
        'ADMINISTRATOR.tsv': NMFPAdministrator,
        'TRANSFERAGENT.tsv': NMFPTransferAgent,
        'SERIESSHADOWPRICE_L.tsv': NMFPSeriesShadowPriceL,
        'CLASSLEVELINFO.tsv': NMFPClassLevelInfo,
        'NETASSETVALUEPERSHARE_L.tsv': NMFPNetAssetValuePerShareL,
        'SCHPORTFOLIOSECURITIES.tsv': NMFPSchPortfolioSecurities,
        'COLLATERALISSUERS.tsv': NMFPCollateralIssuers,
        'NRSRO.tsv': NMFPNrsro,
        'DEMANDFEATURE.tsv': NMFPDemandFeature,
        'GUARANTOR.tsv': NMFPGuarantor,
        'ENHANCEMENTPROVIDER.tsv': NMFPEnhancementProvider,
        'LIQUIDASSETSDETAILS.tsv': NMFPLiquidAssetsDetails,
        'SEVENDAYGROSSYIELD.tsv': NMFPSevenDayGrossYield,
        'DLYNETASSETVALUEPERSHARS.tsv': NMFPDlyNetAssetValuePerShars,
        'LIQUIDITYFEEREPORTINGPER.tsv': NMFPLiquidityFeeReportingPer,
        'DLYNETASSETVALUEPERSHARC.tsv': NMFPDlyNetAssetValuePerSharc,
        'DLYSHAREHOLDERFLOWREPORT.tsv': NMFPDlyShareholderFlowReport,
        'SEVENDAYNETYIELD.tsv': NMFPSevenDayNetYield,
        'BENEFICIALRECORDOWNERCAT.tsv': NMFPBeneficialRecordOwnerCat,
        'CANCELLEDSHARESPERBUSDAY.tsv': NMFPCancelledSharesPerBusDay,
        'DISPOSITIONOFPORTFOLIOSE.tsv': NMFPDispositionOfPortfolioSecurities,
    }

    date_columns = ['filing_date', 'report_date', 'signature_date', 'net_value_per_share_incap_calc_date', 
                    'net_value_per_share_excap_calc_date', 'date_as_of_which_value_was_calculate', 
                    'investment_maturity_date_wam', 'investment_maturity_date_wal', 
                    'final_legal_investment_maturity_da', 'tot_liquid_assets_near_pct_date', 
                    'seven_day_gross_yield_date', 'dly_net_asset_val_per_share_dates', 
                    'liquidity_fee_apply_date', 'dly_net_asset_value_per_share_datec', 
                    'daily_shareholder_flow_date', 'seven_day_net_yield_date', 'cancelled_share_date']

    numeric_columns = [
        'total_share_classes_in_series', 'average_portfolio_maturity', 'average_life_maturity',
        'tot_dly_liquid_asset_friday_week1', 'tot_dly_liquid_asset_friday_week2', 'tot_dly_liquid_asset_friday_week3', 'tot_dly_liquid_asset_friday_week4', 'tot_dly_liquid_asset_friday_week5',
        'tot_wly_liquid_asset_friday_week1', 'tot_wly_liquid_asset_friday_week2', 'tot_wly_liquid_asset_friday_week3', 'tot_wly_liquid_asset_friday_week4', 'tot_wly_liquid_asset_friday_week5',
        'pct_dly_liquid_asset_friday_week1', 'pct_dly_liquid_asset_friday_week2', 'pct_dly_liquid_asset_friday_week3', 'pct_dly_liquid_asset_friday_week4', 'pct_dly_liquid_asset_friday_week5',
        'pct_wkly_liquid_asset_friday_week1', 'pct_wkly_liquid_asset_friday_week2', 'pct_wkly_liquid_asset_friday_week3', 'pct_wkly_liquid_asset_friday_week4', 'pct_wkly_liquid_asset_friday_week5',
        'cash', 'total_value_portfolio_securities', 'amortized_cost_portfolio_securiti', 'total_value_other_assets', 'total_value_liabilities', 'net_asset_of_series',
        'number_of_shares_outstanding', 'stable_price_per_share', 'seven_day_gross_yield', 'net_asset_value_friday_week1', 'net_asset_value_friday_week2', 'net_asset_value_friday_week3', 'net_asset_value_friday_week4', 'net_asset_value_friday_week5',
        'min_initial_investment', 'net_assets_of_class', 'net_asset_per_share_friday_week1', 'net_asset_per_share_friday_week2', 'net_asset_per_share_friday_week3', 'net_asset_per_share_friday_week4', 'net_asset_per_share_friday_week5',
        'gross_subscription_friday_week1', 'gross_redemption_friday_week1', 'gross_subscription_friday_week2', 'gross_redemption_friday_week2', 'gross_subscription_friday_week3', 'gross_redemption_friday_week3', 'gross_subscription_friday_week4', 'gross_redemption_friday_week4', 'gross_subscription_friday_week5', 'gross_redemption_friday_week5',
        'tot_form_nthwly_gross_subscription', 'total_gross_subscriptions', 'tot_form_nthwly_gross_redemption', 'total_gross_redemptions', 'net_asset_value_per_share_l', 'net_shareholder_flow_activity_fo_l', 'seven_day_net_yield',
        'name_of_person_desc_expense_pay_amount', 'pct_shareholder_comp_non_financial', 'pct_shareholder_comp_pension_plan', 'pct_shareholder_comp_non_profit', 'pct_shareholder_comp_municipal', 'pct_shareholder_comp_reg_investme',
        'pct_shareholder_comp_private_fund', 'pct_shareholder_comp_depository_i', 'pct_shareholder_comp_sovereign_fu', 'pct_shareholder_comp_broker_deale', 'pct_shareholder_comp_insurance', 'pct_shareholder_comp_other',
        'value', 'yield_of_the_security_as_of_reportin', 'including_value_of_any_sponsor_supp', 'excluding_value_of_any_sponsor_supp', 'percentage_of_money_market_fund_net', 'investment_owned_balance_princi_l', 'available_for_sale_securities_am_l',
        'principal_amount_to_the_nearest_cen', 'value_of_collateral_to_the_nearest_c', 'amount_provided_by_demand_feature_i', 'remaining_period_demand_feature', 'amount_provided_by_guarantor', 'amount_provided_by_enhancement',
        'tot_value_daily_liquid_assets', 'tot_value_weekly_liquid_assets', 'pct_daily_liquid_assets', 'pct_weekly_liquid_assets', 'seven_day_gross_yield_value', 'dly_net_asset_value_per_share_ser', 'liquidity_fee_amt_apply_to_redempt',
        'liquidity_fee_pct_shares_redeemed', 'dly_net_asset_value_per_share_class', 'daily_gross_subscriptions', 'daily_gross_redemptions', 'seven_day_net_yield_value', 'pct_outstanding_shares_record', 'pct_outstanding_shares_beneficia',
        'cancelled_share_dollar_value', 'cancelled_share_number', 'deposition_us_treasury_debt_amt', 'gov_t_agency_coupon_paying_debt_amt', 'gov_t_agen_on_coupon_paying_debt_amt', 'non_us_sovereign_supranat_debt_amt',
        'certificate_deposit_amt', 'non_negotiable_time_deposit_amt', 'variable_rate_demand_note_amt', 'other_municipal_security_amt', 'asset_backed_commercial_paper_amt', 'other_asset_backed_securities_amt',
        'us_treasury_repurchase_agreem_amt', 'us_govt_agency_repurchase_agreamt', 'other_repurchase_agreement_amt', 'insurance_company_fund_agreem_amt', 'investment_company_amt', 'financial_company_commercial_amt',
        'non_financial_comp_commercial_amt', 'tender_option_bond_amt', 'other_instrument_amt'
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
                                
                                if file_name in column_maps:
                                    df.rename(columns=column_maps[file_name], inplace=True)


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

def load_cftc_data_to_db(df, db_session=None):
    """
    Loads CFTC swap data from a DataFrame into the database.
    
    Args:
        df: DataFrame containing CFTC swap data
        db_session: Optional database session. If not provided, a new one will be created.
    """
    db = db_session or SessionLocal()
    
    try:
        # Convert column names to match database model
        df = sanitize_column_names(df)
        
        # Convert date columns to datetime
        date_columns = [
            'event_timestamp', 'execution_timestamp', 'effective_date', 
            'expiration_date', 'maturity_date_of_the_underler',
            'effective_date_of_the_notional_amount_leg_1',
            'effective_date_of_the_notional_amount_leg_2',
            'end_date_of_the_notional_amount_leg_1',
            'end_date_of_the_notional_amount_leg_2'
        ]
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns to float
        numeric_columns = [
            'notional_amount_leg_1', 'notional_amount_leg_2',
            'notional_quantity_leg_1', 'notional_quantity_leg_2',
            'total_notional_quantity_leg_1', 'total_notional_quantity_leg_2',
            'quantity_frequency_multiplier_leg_1', 'quantity_frequency_multiplier_leg_2',
            'notional_amount_in_effect_on_associated_effective_date_leg_1',
            'notional_amount_in_effect_on_associated_effective_date_leg_2',
            'call_amount_leg_1', 'call_amount_leg_2',
            'put_amount_leg_1', 'put_amount_leg_2'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert all remaining columns to string and handle NaN/None
        for col in df.columns:
            if col not in date_columns + numeric_columns:
                df[col] = df[col].astype(str).replace({'nan': None, 'None': None, '': None})
        
        # Convert DataFrame to list of dictionaries for bulk insert
        records = df.to_dict('records')
        
        # Insert data in chunks to avoid memory issues
        chunk_size = 1000
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            db.bulk_insert_mappings(CFTCSwap, chunk)
            db.commit()
            logging.info(f"Inserted {min(i + len(chunk), len(records))}/{len(records)} records into CFTC swap data")
        
        return True
    except Exception as e:
        db.rollback()
        logging.error(f"Error loading CFTC data to database: {e}")
        return False
    finally:
        if not db_session:  # Only close if we created the session
            db.close()

def sanitize_column_names(df):
    """Sanitizes DataFrame column names to be valid Python identifiers."""
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
    df.columns = df.columns.str.replace(r'^_+|_+$', '', regex=True)
    df.columns = [''.join(c if c.isalnum() or c == '_' else '_' for c in col) for col in df.columns]
    return df


def load_data_to_db(df, model_class, table_name, db_session=None):
    """
    Generic function to load DataFrame data into database using SQLAlchemy model.
    
    Args:
        df: DataFrame containing the data
        model_class: SQLAlchemy model class
        table_name: Name of the table (for logging)
        db_session: Optional database session
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if df.empty:
        logger.info(f"No data to load for {table_name}")
        return
        
    db = db_session or SessionLocal()
    
    try:
        # Sanitize column names
        df = sanitize_column_names(df)
        
        # Convert data types
        # Get columns of the target model
        model_columns = [c.name for c in model_class.__table__.columns]
        
        # Filter DataFrame to only include columns that exist in the model
        df = df.loc[:, [col for col in df.columns if col in model_columns]].copy()
        potential_date_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'period'])]
        potential_numeric_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['amount', 'value', 'fee', 'assets', 'series', 'percentage', 'delta', 'gamma', 'balance', 'usd', 'held', 'shares', 'units', 'notional'])]
        potential_bool_cols = [col for col in df.columns if col.lower().startswith('is_') or any(k in col.lower() for k in ['flag', 'restricted', 'etf', 'money_market'])]

        # Convert data types using .loc to avoid SettingWithCopyWarning
        for col in potential_date_cols:
            if col in df.columns:
                df.loc[:, col] = pd.to_datetime(df[col], errors='coerce')

        for col in potential_numeric_cols:
            if col in df.columns:
                df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')

        for col in potential_bool_cols:
            if col in df.columns:
                df.loc[:, col] = df[col].map({'Y': True, 'N': False, 'YES': True, 'NO': False, '1': True, '0': False}).fillna(False)
        
        # Replace NaN and NaT with None for database insertion
        df = df.where(pd.notnull(df), None)
        
        # Convert to records and insert
        records = df.to_dict(orient='records')
        logger.info(f"Loading {len(records)} records into {table_name}")
        
        # Bulk insert
        db.bulk_insert_mappings(model_class, records)
        db.commit()
        
    except Exception as e:
        logger.error(f"Error loading data to {table_name}: {str(e)}")
        db.rollback()
        raise
    finally:
        if not db_session:  # Only close if we created the session
            db.close()

def process_10k_filings(source_dir: str, db_session=None, force: bool = False) -> None:
    """Process 10-K and 10-Q SEC filings from a directory.
    
    Args:
        source_dir: Directory containing 10-K/10-Q filings
        db_session: Optional database session
        force: If True, reprocess even if already in database
    """
    from processor_10k import SEC10KProcessor
    import os
    
    db = db_session if db_session else SessionLocal()
    processor = SEC10KProcessor(db_session=db)
    
    try:
        # Find all .txt files in the source directory and subdirectories
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        processor.process_filing(file_path, force=force)
                    except Exception as e:
                        logging.error(f"Error processing {file_path}: {e}")
                        continue
    finally:
        if not db_session:  # Only close if we created the session
            db.close()

def process_sec_filings(filing_type: str, source_dir: str, **kwargs):
    """Process SEC filings based on filing type.
    
    Args:
        filing_type: Type of SEC filing ('10-K', '10-Q', '13F', 'N-MFP', etc.)
        source_dir: Directory containing the filing data
        **kwargs: Additional arguments specific to the filing type
    """
    if filing_type in ['10-K', '10-Q']:
        return process_10k_filings(source_dir, **kwargs)
    elif filing_type == '13F':
        return process_form13f_data(source_dir, **kwargs)
    elif filing_type == 'N-MFP':
        return process_nmfp_data(source_dir, **kwargs)
    elif filing_type == 'insider':
        return process_sec_insider_data(source_dir, **kwargs)
    elif filing_type == 'exchange_metrics':
        return process_exchange_metrics_data(source_dir, **kwargs)
    elif filing_type == 'N-CEN':
        return process_ncen_data(source_dir, **kwargs)
    elif filing_type == 'N-PORT':
        return process_nport_data(source_dir, **kwargs)
    else:
        raise ValueError(f"Unsupported filing type: {filing_type}")


def process_ncen_data(source_dir, db_session=None, **kwargs):
    """
    Process N-CEN (Form N-CEN) filing data from ZIP archives.
    
    Args:
        source_dir (str): Directory containing N-CEN ZIP files
        db_session: Optional database session
        **kwargs: Additional processing options
        
    Returns:
        dict: Processing results summary
    """
    import zipfile
    import logging
    from database import (NCENSubmission, NCENRegistrant, NCENFundReportedInfo, 
                         NCENAdviser, SessionLocal)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Processing N-CEN files from {source_dir}")
    
    if not os.path.exists(source_dir):
        logger.error(f"N-CEN source directory does not exist: {source_dir}")
        return {"error": "Source directory not found"}
    
    zip_files = glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True)
    if not zip_files:
        logger.warning(f"No ZIP files found in {source_dir}")
        return {"processed": 0, "errors": 0}
    
    results = {"processed": 0, "errors": 0, "files": []}
    
    for zip_file in zip_files:
        logger.info(f"Processing N-CEN file: {zip_file}")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                # Process each TSV file in the ZIP
                tsv_files = [name for name in zf.namelist() if name.endswith('.tsv')]
                
                # Check if this ZIP contains N-CEN data by looking for N-CEN specific files
                has_ncen_data = any('submission' in name.lower() or 'registrant' in name.lower() or 'fund_reported_info' in name.lower() for name in tsv_files)
                if not has_ncen_data:
                    logger.debug(f"Skipping {zip_file} - no N-CEN data found")
                    results["processed"] += 1  # Still count as processed even if no relevant data
                    results["files"].append(zip_file)
                    continue
                
                db = db_session if db_session else SessionLocal()
                try:
                    for tsv_name in tsv_files:
                        # Read TSV data
                        with zf.open(tsv_name) as tsv_file:
                            df = pd.read_csv(tsv_file, sep='\t', dtype=str, low_memory=False)
                        
                        if df.empty:
                            continue
                            
                        # Sanitize column names
                        df = sanitize_column_names(df)
                        
                        # Route to appropriate table based on TSV file name
                        table_name = tsv_name.lower().replace('.tsv', '')
                        
                        try:
                            if 'submission' in table_name:
                                load_data_to_db(df, NCENSubmission, 'ncen_submissions', db_session=db)
                            elif 'registrant' in table_name and 'website' not in table_name:
                                load_data_to_db(df, NCENRegistrant, 'ncen_registrants', db_session=db)
                            elif 'fund_reported_info' in table_name:
                                load_data_to_db(df, NCENFundReportedInfo, 'ncen_fund_reported_info', db_session=db)
                            elif 'adviser' in table_name:
                                load_data_to_db(df, NCENAdviser, 'ncen_advisers', db_session=db)
                        except Exception as e:
                            logger.error(f"Error processing N-CEN TSV {tsv_name}: {str(e)}")
                            results["errors"] += 1
                            db.rollback() # Rollback on a per-file error
                            # Continue to next file
                    db.commit() # Commit after all files in zip are processed
                except Exception as e:
                    logger.error(f"A critical error occurred during N-CEN processing: {e}")
                    db.rollback()
                finally:
                    if not db_session:
                        db.close()
                        
            results["processed"] += 1
            results["files"].append(zip_file)
            
        except Exception as e:
            logger.error(f"Error processing N-CEN file {zip_path}: {str(e)}")
            results["errors"] += 1
    
    logger.info(f"N-CEN processing completed. Processed: {results['processed']}, Errors: {results['errors']}")
    return results


def process_nport_data(source_dir, db_session=None, **kwargs):
    """
    Process N-PORT (Form N-PORT) filing data from ZIP archives.
    
    Args:
        source_dir (str): Directory containing N-PORT ZIP files
        db_session: Optional database session
        **kwargs: Additional processing options
        
    Returns:
        dict: Processing results summary
    """
    import zipfile
    import logging
    from database import (NPORTSubmission, NPORTGeneralInfo, NPORTHolding,
                         NPORTDerivative, SessionLocal)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Processing N-PORT files from {source_dir}")
    
    if not os.path.exists(source_dir):
        logger.error(f"N-PORT source directory does not exist: {source_dir}")
        return {"error": "Source directory not found"}
    
    zip_files = glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True)
    if not zip_files:
        logger.warning(f"No ZIP files found in {source_dir}")
        return {"processed": 0, "errors": 0}
    
    results = {"processed": 0, "errors": 0, "files": []}
    
    for zip_file in zip_files:
        logger.info(f"Processing N-PORT file: {zip_file}")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                # Process each TSV file in the ZIP
                tsv_files = [name for name in zf.namelist() if name.endswith('.tsv')]
                
                # Check if this ZIP contains N-PORT data by looking for N-PORT specific files
                has_nport_data = any('holding' in name.lower() or 'derivative' in name.lower() or 'general_info' in name.lower() for name in tsv_files)
                if not has_nport_data:
                    logger.debug(f"Skipping {zip_file} - no N-PORT data found")
                    results["processed"] += 1  # Still count as processed even if no relevant data
                    results["files"].append(zip_file)
                    continue
                
                db = db_session if db_session else SessionLocal()
                try:
                    for tsv_name in tsv_files:
                        # Read TSV data
                        with zf.open(tsv_name) as tsv_file:
                            df = pd.read_csv(tsv_file, sep='\t', dtype=str, low_memory=False)
                        
                        if df.empty:
                            continue
                            
                        # Sanitize column names
                        df = sanitize_column_names(df)

                        # Route to appropriate table based on TSV file name
                        table_name = tsv_name.lower().replace('.tsv', '')
                        
                        try:
                            if 'submission' in table_name:
                                load_data_to_db(df, NPORTSubmission, 'nport_submissions', db_session=db)
                            elif 'general' in table_name or 'geninfo' in table_name:
                                load_data_to_db(df, NPORTGeneralInfo, 'nport_general_info', db_session=db)
                            elif 'holding' in table_name:
                                load_data_to_db(df, NPORTHolding, 'nport_holdings', db_session=db)
                            elif 'derivative' in table_name:
                                load_data_to_db(df, NPORTDerivative, 'nport_derivatives', db_session=db)
                        except Exception as e:
                            logger.error(f"Error processing N-PORT TSV {tsv_name}: {str(e)}")
                            results["errors"] += 1
                            db.rollback()
                            # Continue to next file
                    db.commit()
                except Exception as e:
                    logger.error(f"A critical error occurred during N-PORT processing: {e}")
                    db.rollback()
                finally:
                    if not db_session:
                        db.close()
                        
            results["processed"] += 1
            results["files"].append(zip_file)
            
        except Exception as e:
            logger.error(f"Error processing N-PORT file {zip_path}: {str(e)}")
            results["errors"] += 1
    
    logger.info(f"N-PORT processing completed. Processed: {results['processed']}, Errors: {results['errors']}")
    return results
