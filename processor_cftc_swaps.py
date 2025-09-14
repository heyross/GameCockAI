"""
Processor module for CFTC Swap Data
Handles processing and loading of CFTC swap data into the database.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session

# Import from the correct database module (GameCockAI/database.py)
try:
    from .database import (
        SessionLocal,
        CFTCDerivativesDealer,
        CFTCDerivativesClearingOrganization,
        CFTCSwapExecutionFacility,
        CFTCSwapDataRepository,
        CFTCDailySwapReport
    )
except ImportError:
    # Fallback for when running from GameCockAI directory
    from database import (
        SessionLocal,
        CFTCDerivativesDealer,
        CFTCDerivativesClearingOrganization,
        CFTCSwapExecutionFacility,
        CFTCSwapDataRepository,
        CFTCDailySwapReport
    )
from config import (
    CFTC_SWAP_DEALER_DIR,
    CFTC_SWAP_EXECUTION_DIR,
    CFTC_SWAP_DATA_REPOSITORY_DIR
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_swap_dealer_data(file_path: str, session: Optional[Session] = None) -> int:
    """
    Process and load swap dealer data from a JSON file into the database.
    
    Args:
        file_path: Path to the JSON file containing swap dealer data
        session: Optional SQLAlchemy session. If not provided, a new one will be created.
        
    Returns:
        Number of records processed
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error(f"Expected a list of records in {file_path}, got {type(data)}")
            return 0
        
        count = 0
        for item in data:
            try:
                # Check if record already exists
                existing = session.query(CFTCDerivativesDealer).filter_by(
                    dftc_swap_dealer_id=item.get('dftc_swap_dealer_id')
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in item.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                    existing.last_updated = datetime.utcnow()
                else:
                    # Create new record
                    dealer = CFTCDerivativesDealer(**item)
                    session.add(dealer)
                
                count += 1
                if count % 100 == 0:
                    session.commit()
                    
            except Exception as e:
                logger.error(f"Error processing swap dealer record: {e}")
                session.rollback()
        
        session.commit()
        logger.info(f"Processed {count} swap dealer records from {file_path}")
        return count
        
    except Exception as e:
        logger.error(f"Error processing swap dealer file {file_path}: {e}")
        session.rollback()
        return 0
        
    finally:
        if close_session and session:
            session.close()

def process_swap_execution_facility_data(file_path: str, session: Optional[Session] = None) -> int:
    """
    Process and load swap execution facility data from a JSON file into the database.
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error(f"Expected a list of records in {file_path}, got {type(data)}")
            return 0
        
        count = 0
        for item in data:
            try:
                # Check if record already exists
                existing = session.query(CFTCSwapExecutionFacility).filter_by(
                    sef_id=item.get('sef_id')
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in item.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                    existing.last_updated = datetime.utcnow()
                else:
                    # Create new record
                    facility = CFTCSwapExecutionFacility(**item)
                    session.add(facility)
                
                count += 1
                if count % 100 == 0:
                    session.commit()
                    
            except Exception as e:
                logger.error(f"Error processing swap execution facility record: {e}")
                session.rollback()
        
        session.commit()
        logger.info(f"Processed {count} swap execution facility records from {file_path}")
        return count
        
    except Exception as e:
        logger.error(f"Error processing swap execution facility file {file_path}: {e}")
        session.rollback()
        return 0
        
    finally:
        if close_session and session:
            session.close()

def process_swap_data_repository_data(file_path: str, session: Optional[Session] = None) -> int:
    """
    Process and load swap data repository data from a JSON file into the database.
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error(f"Expected a list of records in {file_path}, got {type(data)}")
            return 0
        
        count = 0
        for item in data:
            try:
                # Check if record already exists
                existing = session.query(CFTCSwapDataRepository).filter_by(
                    sdr_id=item.get('sdr_id')
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in item.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                    existing.last_updated = datetime.utcnow()
                else:
                    # Create new record
                    repo = CFTCSwapDataRepository(**item)
                    session.add(repo)
                
                count += 1
                if count % 100 == 0:
                    session.commit()
                    
            except Exception as e:
                logger.error(f"Error processing swap data repository record: {e}")
                session.rollback()
        
        session.commit()
        logger.info(f"Processed {count} swap data repository records from {file_path}")
        return count
        
    except Exception as e:
        logger.error(f"Error processing swap data repository file {file_path}: {e}")
        session.rollback()
        return 0
        
    finally:
        if close_session and session:
            session.close()

def process_daily_swap_report_data(file_path: str, session: Optional[Session] = None) -> int:
    """
    Process and load daily swap report data from a CSV file into the database.
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert date strings to datetime objects
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
        
        # Convert boolean columns
        bool_columns = ['block_trade', 'block_trade_eligible', 'compression_trade', 'package_trade']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].fillna(False).astype(bool)
        
        # Process each row
        count = 0
        for _, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN/NaT values
                data = {k: (v if pd.notna(v) else None) for k, v in row.to_dict().items()}
                
                # Check if record already exists
                existing = None
                if 'report_date' in data and 'asset_class' in data and 'product_type' in data:
                    existing = session.query(CFTCDailySwapReport).filter(
                        CFTCDailySwapReport.report_date == data['report_date'],
                        CFTCDailySwapReport.asset_class == data['asset_class'],
                        CFTCDailySwapReport.product_type == data['product_type']
                    ).first()
                
                if existing:
                    # Update existing record
                    for key, value in data.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                    existing.last_updated = datetime.utcnow()
                else:
                    # Create new record
                    report = CFTCDailySwapReport(**data)
                    session.add(report)
                
                count += 1
                if count % 100 == 0:
                    session.commit()
                    
            except Exception as e:
                logger.error(f"Error processing daily swap report record: {e}")
                session.rollback()
        
        session.commit()
        logger.info(f"Processed {count} daily swap report records from {file_path}")
        return count
        
    except Exception as e:
        logger.error(f"Error processing daily swap report file {file_path}: {e}")
        session.rollback()
        return 0
        
    finally:
        if close_session and session:
            session.close()

def process_all_swap_data() -> Dict[str, int]:
    """
    Process all swap data files in their respective directories.
    
    Returns:
        Dictionary with counts of processed records by data type
    """
    results = {
        'swap_dealers': 0,
        'swap_execution_facilities': 0,
        'swap_data_repositories': 0,
        'daily_swap_reports': 0
    }
    
    session = SessionLocal()
    
    try:
        # Process swap dealer data
        if os.path.exists(CFTC_SWAP_DEALER_DIR):
            for filename in os.listdir(CFTC_SWAP_DEALER_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(CFTC_SWAP_DEALER_DIR, filename)
                    results['swap_dealers'] += process_swap_dealer_data(file_path, session)
        
        # Process swap execution facility data
        if os.path.exists(CFTC_SWAP_EXECUTION_DIR):
            for filename in os.listdir(CFTC_SWAP_EXECUTION_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(CFTC_SWAP_EXECUTION_DIR, filename)
                    results['swap_execution_facilities'] += process_swap_execution_facility_data(file_path, session)
        
        # Process swap data repository data
        if os.path.exists(CFTC_SWAP_DATA_REPOSITORY_DIR):
            for filename in os.listdir(CFTC_SWAP_DATA_REPOSITORY_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(CFTC_SWAP_DATA_REPOSITORY_DIR, filename)
                    results['swap_data_repositories'] += process_swap_data_repository_data(file_path, session)
        
        # Process daily swap reports (CSV format)
        if os.path.exists(CFTC_SWAP_DATA_REPOSITORY_DIR):
            for filename in os.listdir(CFTC_SWAP_DATA_REPOSITORY_DIR):
                if filename.endswith('.csv') and 'daily_swap_report' in filename.lower():
                    file_path = os.path.join(CFTC_SWAP_DATA_REPOSITORY_DIR, filename)
                    results['daily_swap_reports'] += process_daily_swap_report_data(file_path, session)
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing swap data: {e}")
        session.rollback()
        return results
        
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    # Example usage
    results = process_all_swap_data()
    print(f"Processing complete. Results: {results}")
