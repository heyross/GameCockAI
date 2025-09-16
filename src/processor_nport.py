"""
N-PORT (Form N-PORT) Processor Module

This module handles processing of N-PORT filing data from ZIP archives.
N-PORT is the monthly portfolio holdings report for registered investment companies.
"""

import glob
from src.logging_utils import get_processor_logger

logger = get_processor_logger('processor_nport')
import os
import pandas as pd
import zipfile
from database import (
    NPORTSubmission, NPORTGeneralInfo, NPORTHolding,
    NPORTDerivative, SessionLocal
)

logger = logger

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
    logger.info(f"Processing N-PORT files from {source_dir}")

from src.logging_utils import get_processor_logger

logger = get_processor_logger('processor_nport')

    
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
            logger.error(f"Error processing N-PORT file {zip_file}: {str(e)}")
            results["errors"] += 1
    
    logger.info(f"N-PORT processing completed. Processed: {results['processed']}, Errors: {results['errors']}")
    return results
