"""
Modular processor orchestrator for GameCock AI.
This module coordinates calls to specialized processor modules.
"""

import logging
from typing import List, Dict, Any, Optional

# Import database models
try:
    from database import SessionLocal
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import SessionLocal

# Import specialized processors
from .processor_10k import SEC10KProcessor
from .processor_8k import SEC8KProcessor
from .processor_cftc_swaps import process_all_swap_data
from .processor_dtcc import DTCCProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_zip_files(source_dir: str, target_companies: Optional[List[Dict]] = None, 
                     search_term: Optional[str] = None, load_to_db: bool = False):
    """
    Process zip files from a directory.
    This is a placeholder that delegates to appropriate specialized processors.
    """
    logging.info(f"Processing zip files from {source_dir}")
    # This would delegate to appropriate specialized processors based on file type
    # For now, return None as this is handled by specialized processors
    return None

def process_sec_insider_data(source_dir: str, db_session=None):
    """Process SEC insider trading data."""
    logging.info(f"Processing SEC insider data from {source_dir}")
    # Delegate to specialized SEC processor
    # Implementation would go here
    pass

def process_form13f_data(source_dir: str, db_session=None):
    """Process Form 13F data."""
    logging.info(f"Processing Form 13F data from {source_dir}")
    # Delegate to specialized 13F processor
    # Implementation would go here
    pass

def process_exchange_metrics_data(source_dir: str, db_session=None):
    """Process SEC exchange metrics data."""
    logging.info(f"Processing exchange metrics data from {source_dir}")
    # Delegate to specialized exchange metrics processor
    # Implementation would go here
    pass

def process_ncen_data(source_dir: str, db_session=None, **kwargs):
    """Process N-CEN filing data."""
    logging.info(f"Processing N-CEN data from {source_dir}")
    # Delegate to specialized N-CEN processor
    # Implementation would go here
    pass

def process_nport_data(source_dir: str, db_session=None, **kwargs):
    """Process N-PORT filing data."""
    logging.info(f"Processing N-PORT data from {source_dir}")
    # Delegate to specialized N-PORT processor
    # Implementation would go here
    pass

def process_formd_data(source_dir: str, db_session=None):
    """Process Form D data."""
    logging.info(f"Processing Form D data from {source_dir}")
    # Delegate to specialized Form D processor
    # Implementation would go here
    pass

def process_formd_quarter(quarter_dir: str, db_session=None):
    """Process Form D data for a specific quarter."""
    logging.info(f"Processing Form D quarter data from {quarter_dir}")
    # Implementation for processing a single quarter of Form D data
    pass

def process_nmfp_data(source_dir: str, db_session=None):
    """Process NMFP (Net Monthly Fund Performance) data."""
    logging.info(f"Processing NMFP data from {source_dir}")
    # Implementation for processing NMFP data
    pass

def process_10k_filings(source_dir: str, db_session=None, force: bool = False):
    """Process 10-K and 10-Q SEC filings."""
    logging.info(f"Processing 10-K/10-Q filings from {source_dir}")
    db = db_session if db_session else SessionLocal()
    processor = SEC10KProcessor(db_session=db)
    
    try:
        import os
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
        if not db_session:
            db.close()

def process_8k_filings(source_dir: str, db_session=None, force: bool = False):
    """Process 8-K SEC filings."""
    logging.info(f"Processing 8-K filings from {source_dir}")
    db = db_session if db_session else SessionLocal()
    processor = SEC8KProcessor(db_session=db)
    
    try:
        import os
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
        if not db_session:
            db.close()

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
    elif filing_type.upper() == '8-K':
        return process_8k_filings(source_dir, **kwargs)
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
