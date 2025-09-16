"""
Modular processor orchestrator for GameCock AI.
This module coordinates calls to specialized processor modules.
"""

import os
import sys
from typing import List, Dict, Any, Optional

# Set up logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logging_utils import get_processor_logger

logger = get_processor_logger('processor')

# Import database models
try:
    from database import SessionLocal
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import SessionLocal

# Import specialized processors
from src.processor_10k import SEC10KProcessor
from src.processor_8k import SEC8KProcessor
from src.processor_cftc_swaps import process_all_swap_data
from src.processor_dtcc import DTCCProcessor
from src.processor_ncen import process_ncen_data
from src.processor_nport import process_nport_data
from src.processor_formd import process_formd_data
from src.processor_form13f import process_form13f_data
from src.processor_sec import process_sec_insider_data
from src.processor_exchange_metrics import process_exchange_metrics_data
from src.processor_nmfp import process_nmfp_data

# Logging is now configured in logging_utils.py

def process_zip_files(source_dir: str, target_companies: Optional[List[Dict]] = None, 
                     search_term: Optional[str] = None, load_to_db: bool = False):
    """
    Process zip files from a directory by delegating to appropriate specialized processors.
    
    Args:
        source_dir: Directory containing zip files to process
        target_companies: Optional list of target companies to filter by
        search_term: Optional search term to filter data
        load_to_db: If True, loads the data into the database
        
    Returns:
        DataFrame containing the processed data, or None if no data was found
    """
    import glob
    import pandas as pd
    from zipfile import ZipFile
    
    logger.info(f"Processing zip files from {source_dir}")
    
    if not os.path.exists(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")
        return None
    
    zip_files = sorted(glob.glob(os.path.join(source_dir, '**/*.zip'), recursive=True))
    if not zip_files:
        logger.warning(f"No zip files found in {source_dir}")
        return None
    
    all_data = []
    
    for zip_file in zip_files:
        try:
            with ZipFile(zip_file, 'r') as zip_ref:
                # Get list of files in the zip
                file_list = zip_ref.namelist()
                
                # Determine file type based on contents
                file_type = _detect_file_type(file_list)
                logger.info(f"Detected file type: {file_type} for {zip_file}")
                
                # Delegate to appropriate specialized processor
                if file_type == 'CFTC':
                    result = process_cftc_swap_data(source_dir, load_to_db=load_to_db)
                elif file_type == 'N-CEN':
                    result = process_ncen_data(source_dir, load_to_db=load_to_db)
                elif file_type == 'N-PORT':
                    result = process_nport_data(source_dir, load_to_db=load_to_db)
                elif file_type == 'FORM-D':
                    result = process_formd_data(source_dir, load_to_db=load_to_db)
                elif file_type == '13F':
                    result = process_form13f_data(source_dir, load_to_db=load_to_db)
                elif file_type == 'SEC-INSIDER':
                    result = process_sec_insider_data(source_dir, load_to_db=load_to_db)
                elif file_type == 'EXCHANGE-METRICS':
                    result = process_exchange_metrics_data(source_dir, load_to_db=load_to_db)
                elif file_type == 'N-MFP':
                    result = process_nmfp_data(source_dir, load_to_db=load_to_db)
                else:
                    logger.warning(f"Unknown file type for {zip_file}, skipping")
                    continue
                
                # Only append DataFrame results, skip dictionaries or other types
                if result is not None and hasattr(result, 'shape'):  # Check if it's a DataFrame
                    all_data.append(result)
                elif result is not None:
                    logger.info(f"Processor returned non-DataFrame result: {type(result)}")
                    
        except Exception as e:
            logger.error(f"Error processing {zip_file}: {e}", exc_info=True)
            continue
    
    # Combine all results into a single DataFrame if any data was processed
    if all_data:
        try:
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Processed {len(all_data)} records from {len(zip_files)} zip files")
            return combined_df
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            return None
    else:
        logger.warning("No data was processed from any zip files")
        logger.warning("No data was processed from any zip files")
        return None

def _detect_file_type(file_list):
    """Detect the type of data based on file names in the zip."""
    file_list_lower = [f.lower() for f in file_list]
    
    # CFTC swap data detection
    if any('cftc' in f or 'swap' in f for f in file_list_lower):
        return 'CFTC'
    
    # N-CEN detection
    if any('ncen' in f or 'submission' in f or 'registrant' in f for f in file_list_lower):
        return 'N-CEN'
    
    # N-PORT detection
    if any('nport' in f or 'holding' in f or 'derivative' in f for f in file_list_lower):
        return 'N-PORT'
    
    # Form D detection
    if any('formd' in f or 'form_d' in f for f in file_list_lower):
        return 'FORM-D'
    
    # 13F detection
    if any('13f' in f or 'form13f' in f for f in file_list_lower):
        return '13F'
    
    # SEC insider trading detection
    if any('insider' in f or 'form345' in f for f in file_list_lower):
        return 'SEC-INSIDER'
    
    # Exchange metrics detection
    if any('exchange' in f or 'metrics' in f for f in file_list_lower):
        return 'EXCHANGE-METRICS'
    
    # N-MFP detection
    if any('nmfp' in f or 'n-mfp' in f for f in file_list_lower):
        return 'N-MFP'
    
    # Default to CFTC for generic CSV files
    if any(f.endswith('.csv') for f in file_list):
        return 'CFTC'
    
    return 'UNKNOWN'

def process_sec_insider_data(source_dir: str, db_session=None):
    """Process SEC insider trading data."""
    from src.processor_sec import process_sec_insider_data as _process_sec_insider_data
    return _process_sec_insider_data(source_dir, db_session)

def process_form13f_data(source_dir: str, db_session=None):
    """Process Form 13F data."""
    from src.processor_form13f import process_form13f_data as _process_form13f_data
    return _process_form13f_data(source_dir, db_session)

def process_exchange_metrics_data(source_dir: str, db_session=None):
    """Process SEC exchange metrics data."""
    from src.processor_exchange_metrics import process_exchange_metrics_data as _process_exchange_metrics_data
    return _process_exchange_metrics_data(source_dir, db_session)

def process_ncen_data(source_dir: str, db_session=None, **kwargs):
    """Process N-CEN filing data."""
    from src.processor_ncen import process_ncen_data as _process_ncen_data
    return _process_ncen_data(source_dir, db_session, **kwargs)

def process_nport_data(source_dir: str, db_session=None, **kwargs):
    """Process N-PORT filing data."""
    from src.processor_nport import process_nport_data as _process_nport_data
    return _process_nport_data(source_dir, db_session, **kwargs)

def process_formd_data(source_dir: str, db_session=None):
    """Process Form D data."""
    from src.processor_formd import process_formd_data as _process_formd_data
    return _process_formd_data(source_dir, db_session)

def process_formd_quarter(quarter_dir: str, db_session=None):
    """Process Form D data for a specific quarter."""
    from src.processor_formd import process_formd_quarter as _process_formd_quarter
    return _process_formd_quarter(quarter_dir, db_session)

def process_nmfp_data(source_dir: str, db_session=None):
    """Process NMFP (Net Monthly Fund Performance) data."""
    from src.processor_nmfp import process_nmfp_data as _process_nmfp_data
    return _process_nmfp_data(source_dir, db_session)

def process_10k_filings(source_dir: str, db_session=None, force: bool = False):
    """Process 10-K and 10-Q SEC filings with section extraction."""
    logging.info(f"Processing 10-K/10-Q filings from {source_dir}")
    db = db_session if db_session else SessionLocal()
    
    # Use enhanced processor for section extraction
    from enhanced_sec_processor import EnhancedSECProcessor
    enhanced_processor = EnhancedSECProcessor(db_session=db)
    
    try:
        import os
        processed_count = 0
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.txt') and ('10-K' in file or '10-Q' in file):
                    file_path = os.path.join(root, file)
                    try:
                        # Extract accession number from filename
                        # Format: year_filing_type_date_accession_title.txt
                        filename_parts = file.replace('.txt', '').split('_')
                        if len(filename_parts) >= 4:
                            accession_number = filename_parts[3]
                            
                            # Determine form type
                            form_type = '10-K' if '10-K' in file else '10-Q'
                            
                            # Process with section extraction
                            sections = enhanced_processor.process_filing_with_sections(
                                file_path, accession_number, form_type
                            )
                            
                            if sections:
                                processed_count += 1
                                logging.info(f"Extracted {len(sections)} sections from {file}")
                            else:
                                logging.warning(f"No sections extracted from {file}")
                        else:
                            logging.warning(f"Could not parse filename: {file}")
                            
                    except Exception as e:
                        logging.error(f"Error processing {file_path}: {e}")
                        continue
        
        logging.info(f"Processed {processed_count} 10-K/10-Q filings with section extraction")
        return processed_count
    finally:
        if not db_session:
            db.close()

def process_8k_filings(source_dir: str, db_session=None, force: bool = False):
    """Process 8-K SEC filings with item extraction."""
    logging.info(f"Processing 8-K filings from {source_dir}")
    db = db_session if db_session else SessionLocal()
    
    # Use enhanced processor for item extraction
    from enhanced_sec_processor import EnhancedSECProcessor
    enhanced_processor = EnhancedSECProcessor(db_session=db)
    
    try:
        import os
        processed_count = 0
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.txt') and '8-K' in file:
                    file_path = os.path.join(root, file)
                    try:
                        # Extract accession number from filename
                        # Format: year_filing_type_date_accession_title.txt
                        filename_parts = file.replace('.txt', '').split('_')
                        if len(filename_parts) >= 4:
                            accession_number = filename_parts[3]
                            
                            # Process with item extraction
                            items = enhanced_processor.process_filing_with_sections(
                                file_path, accession_number, '8-K'
                            )
                            
                            if items:
                                processed_count += 1
                                logging.info(f"Extracted {len(items)} items from {file}")
                            else:
                                logging.warning(f"No items extracted from {file}")
                        else:
                            logging.warning(f"Could not parse filename: {file}")
                            
                    except Exception as e:
                        logging.error(f"Error processing {file_path}: {e}")
                        continue
        
        logging.info(f"Processed {processed_count} 8-K filings with item extraction")
        return processed_count
    finally:
        if not db_session:
            db.close()

def process_s4_filings(source_dir: str, db_session=None, force: bool = False):
    """Process S-4 SEC filings (Registration Statements)."""
    logging.info(f"Processing S-4 filings from {source_dir}")
    db = db_session if db_session else SessionLocal()
    
    try:
        import os
        processed_count = 0
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.txt') and 'S-4' in file:
                    file_path = os.path.join(root, file)
                    try:
                        # For now, use a generic document processor
                        # In the future, this could be specialized for S-4 content
                        process_generic_sec_filing(file_path, 'S-4', db, force=force)
                        processed_count += 1
                    except Exception as e:
                        logging.error(f"Error processing {file_path}: {e}")
                        continue
        
        logging.info(f"Processed {processed_count} S-4 filings")
        return processed_count
    finally:
        if not db_session:
            db.close()

def process_def14a_filings(source_dir: str, db_session=None, force: bool = False):
    """Process DEF 14A SEC filings (Proxy Statements)."""
    logging.info(f"Processing DEF 14A filings from {source_dir}")
    db = db_session if db_session else SessionLocal()
    
    try:
        import os
        processed_count = 0
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.txt') and 'DEF 14A' in file:
                    file_path = os.path.join(root, file)
                    try:
                        # For now, use a generic document processor
                        # In the future, this could be specialized for DEF 14A content
                        process_generic_sec_filing(file_path, 'DEF 14A', db, force=force)
                        processed_count += 1
                    except Exception as e:
                        logging.error(f"Error processing {file_path}: {e}")
                        continue
        
        logging.info(f"Processed {processed_count} DEF 14A filings")
        return processed_count
    finally:
        if not db_session:
            db.close()

def process_generic_sec_filing(file_path: str, filing_type: str, db_session, force: bool = False):
    """Generic processor for SEC filings that don't have specialized processors."""
    try:
        # Extract company information from file path
        # File path format: EDGAR_SOURCE_DIR/CIK/year_filing_type_date_accession_title.txt
        import os
        filename = os.path.basename(file_path)
        path_parts = file_path.split(os.sep)
        
        # Find CIK in path (should be in EDGAR_SOURCE_DIR/CIK/...)
        cik = None
        for i, part in enumerate(path_parts):
            if part == 'EDGAR' and i + 2 < len(path_parts):
                cik = path_parts[i + 2]
                break
        
        # Parse filename for additional metadata
        # Format: year_filing_type_date_accession_title.txt
        filename_parts = filename.replace('.txt', '').split('_')
        year = filename_parts[0] if len(filename_parts) > 0 else 'unknown'
        filing_date = filename_parts[2] if len(filename_parts) > 2 else 'unknown'
        accession = filename_parts[3] if len(filename_parts) > 3 else 'unknown'
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Store in a generic SEC filings table (if it exists)
        # For now, just log the processing
        logging.info(f"Processed {filing_type} filing: {filename}")
        logging.info(f"  CIK: {cik}, Year: {year}, Date: {filing_date}, Accession: {accession}")
        logging.info(f"  Content length: {len(content)} characters")
        
        # TODO: Implement database storage for generic SEC filings
        # This would require creating a generic SEC filings table
        
        return True
        
    except Exception as e:
        logging.error(f"Error processing generic SEC filing {file_path}: {e}")
        return False

def process_cftc_swap_data(source_dir: str, db_session=None, **kwargs):
    """Process CFTC swap data."""
    logging.info(f"Processing CFTC swap data from {source_dir}")
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True
    
    try:
        results = process_all_swap_data()
        logging.info(f"Completed CFTC swap data processing. Results: {results}")
        return results
    except Exception as e:
        logging.error(f"Error processing CFTC swap data: {e}", exc_info=True)
        if db_session:
            db_session.rollback()
        raise
    finally:
        if close_session and db_session:
            db_session.close()

def process_sec_filings(filing_type: str, source_dir: str, **kwargs):
    """Process SEC filings based on filing type."""
    if filing_type.upper() == '10-K':
        return process_10k_filings(source_dir, **kwargs)
    elif filing_type.upper() == '10-Q':
        return process_10k_filings(source_dir, **kwargs)  # 10-Q uses same processor as 10-K
    elif filing_type.upper() == '8-K':
        return process_8k_filings(source_dir, **kwargs)
    elif filing_type.upper() == 'S-4':
        return process_s4_filings(source_dir, **kwargs)
    elif filing_type.upper() == 'DEF 14A':
        return process_def14a_filings(source_dir, **kwargs)
    elif filing_type.upper() == '13F':
        return process_form13f_data(source_dir, **kwargs)
    elif filing_type.upper() == 'N-CEN':
        return process_ncen_data(source_dir, **kwargs)
    elif filing_type.upper() == 'N-PORT':
        return process_nport_data(source_dir, **kwargs)
    elif filing_type.upper() == 'FORM-D':
        return process_formd_data(source_dir, **kwargs)
    else:
        logging.warning(f"Unsupported filing type: {filing_type}")
        return None

def load_cftc_data_to_db(df, db_session=None):
    """Load CFTC data to database."""
    logging.info("Loading CFTC data to database")
    # This would delegate to specialized CFTC processor
    # Implementation would go here
    pass

def sanitize_column_names(df):
    """Sanitize DataFrame column names."""
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
    df.columns = df.columns.str.replace(r'^_+|_+$', '', regex=True)
    df.columns = [''.join(c if c.isalnum() or c == '_' else '_' for c in col) for col in df.columns]
    return df

def load_data_to_db(data, table_name: str, db_session=None):
    """Load data to database table."""
    try:
        if db_session is None:
            db_session = SessionLocal()
        
        # Convert DataFrame to list of dictionaries
        if hasattr(data, 'to_dict'):
            records = data.to_dict('records')
        else:
            records = data if isinstance(data, list) else [data]
        
        # Use bulk insert for efficiency
        if records:
            db_session.bulk_insert_mappings(table_name, records)
            db_session.commit()
            logger.info(f"Loaded {len(records)} records to {table_name}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error loading data to {table_name}: {e}")
        if db_session:
            db_session.rollback()
        return False
    finally:
        if db_session:
            db_session.close()
