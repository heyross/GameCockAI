"""
Form D Processor Module

This module handles processing of Form D filing data from ZIP archives.
Form D is used for notice of sales of securities under Regulation D.
"""

# Standard library imports
import glob
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from zipfile import ZipFile

# Third-party imports
import pandas as pd

# Add parent directory to path for local imports
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Local application imports
try:
    from config import FORMD_SOURCE_DIR
    from database import (
        FormDSubmission, FormDIssuer, FormDOffering, FormDRecipient,
        FormDRelatedPerson, FormDSignature, SessionLocal
    )
    from src.downloader import extract_formd_filings
    logger = logging.getLogger('processor_formd')
    logger.setLevel(logging.INFO)
except ImportError as e:
    try:
        from GameCockAI.config import FORMD_SOURCE_DIR
        from GameCockAI.database import (
            FormDSubmission, FormDIssuer, FormDOffering, FormDRecipient,
            FormDRelatedPerson, FormDSignature, SessionLocal
        )
        from GameCockAI.src.downloader import extract_formd_filings
        logger = logging.getLogger('processor_formd')
        logger.setLevel(logging.INFO)
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('processor_formd')
        logger.warning('Failed to import some modules: %s', e)

def sanitize_column_names(df):
    """Sanitizes DataFrame column names to be valid Python identifiers."""
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(r'[^0-9a-zA-Z_]+', '_', regex=True)
    df.columns = df.columns.str.replace(r'^_+|_+$', '', regex=True)
    df.columns = [''.join(c if c.isalnum() or c == '_' else '_' for c in col) for col in df.columns]
    return df

def process_formd_data(source_dir, db_session=None):
    """
    Process Form D data by extracting quarterly archives and loading TSV files into database.
    """
    logger.info("Starting processing of Form D data...")
    
    # Get all zip files in the source directory
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))
    
    if not zip_files:
        logger.warning(f"No zip files found in {source_dir}")
        return
    
    # Extract each archive first
    for zip_file in zip_files:
        logger.info(f"Processing archive: {zip_file}")
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
            logger.info(f"Processing quarterly data from: {quarter_dir}")
            process_formd_quarter(quarter_dir, db)
            
        db.commit()
        logger.info("Finished processing all Form D data.")
        
    except Exception as e:
        logger.error(f"Error processing Form D data: {e}")
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
        logger.warning(f"No quarterly subdirectory found in {quarter_dir}")
        return
    
    # Process each TSV file
    for file_name, model in table_map.items():
        file_path = os.path.join(quarter_subdir, file_name)
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue
            
        logger.info(f"Processing {file_name}...")
        
        try:
            # Read TSV file
            df = pd.read_csv(file_path, sep='\t', low_memory=False, 
                           dtype=str, na_values=['', 'nan', 'NaN', 'NULL'])
            
            if df.empty:
                logger.info(f"No data found in {file_name}")
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
                logger.info(f"Inserted {len(records)} records from {file_name}")

        except Exception as e:
            logger.error(f"Error processing {file_name}: {e}")
            continue
    
    # Commit all changes for this quarter
    db_session.commit()
    logger.info(f"Committed all changes for quarter: {os.path.basename(quarter_dir)}")
