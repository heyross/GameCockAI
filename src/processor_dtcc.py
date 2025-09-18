"""
DTCC Data Processor

This module handles the processing of DTCC data files and loading them into the database.
"""

# Standard library imports
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party imports
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

# Add parent directory to path for local imports
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Local application imports
try:
    from database import SessionLocal, DTCCTrade, DTCCPosition
    logger = logging.getLogger('processor_dtcc')
    logger.setLevel(logging.INFO)
except ImportError as e:
    try:
        from GameCockAI.database import SessionLocal, DTCCTrade, DTCCPosition
        logger = logging.getLogger('processor_dtcc')
        logger.setLevel(logging.INFO)
    except ImportError:
        import sys
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('processor_dtcc')
        logger.warning('Failed to import some database modules: %s', e)

class DTCCProcessor:
    """Processes DTCC data files and loads them into the database."""
    
    def __init__(self, session):
        """Initialize the processor with a database session."""
        self.session = session
        
    def process_dtcc_file(self, file_path, file_type, source_entity):
        """
        Process a DTCC data file and load it into the database.
        
        Args:
            file_path (str): Path to the DTCC data file
            file_type (str): Type of DTCC file (e.g., 'OPTION_TRADE', 'INTEREST_RATE_SWAP')
            source_entity (str): The entity that provided the data
            
        Returns:
            dict: Processing results including counts and any errors
        """
        logger.info(f"Processing DTCC {file_type} file: {file_path}")
        
        # Read the file based on extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
            # Process based on file type
            if file_type == 'OPTION_TRADE':
                return self._process_option_trades(df, source_entity)
            elif file_type == 'INTEREST_RATE_SWAP':
                return self._process_interest_rate_swaps(df, source_entity)
            else:
                raise ValueError(f"Unsupported DTCC file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error processing DTCC file {file_path}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'file': file_path,
                'records_processed': 0
            }
    
    def _process_option_trades(self, df, source_entity):
        """Process option trade data."""
        from dtcc_models import DTCCOptionTrade, DTCCEquityOption, DTCCOptionExercise, DTCCOrganization
        
        processed = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Get or create organizations
                reporting_org = self._get_or_create_organization(
                    row.get('reporting_party_lei'),
                    row.get('reporting_party_name')
                )
                
                other_org = self._get_or_create_organization(
                    row.get('other_party_lei'),
                    row.get('other_party_name')
                )
                
                # Create option trade with only valid fields
                trade_data = {
                    'trade_id': row['trade_id'],
                    'execution_timestamp': self._parse_datetime(row.get('execution_timestamp')),
                    'effective_date': self._parse_datetime(row.get('effective_date')),
                    'trade_status': row.get('trade_status', 'NEW'),
                    'clearing_status': row.get('clearing_status', 'PENDING'),
                    'asset_class': row.get('asset_class', 'EQUITY'),
                    'product_type': 'OPTION',
                    'reporting_party_lei': reporting_org.lei,
                    'other_party_lei': other_org.lei,
                    'underlying_asset': row.get('underlying_asset'),
                    'option_type': row.get('option_type'),
                    'strike_price': row.get('strike_price'),
                    'strike_currency': row.get('strike_currency', 'USD'),
                    'expiration_date': self._parse_datetime(row.get('expiration_date')),
                    'premium_amount': row.get('premium_amount'),
                    'premium_currency': row.get('premium_currency', 'USD'),
                    'option_style': row.get('option_style')
                }
                
                # Check if trade already exists
                existing_trade = self.session.query(DTCCOptionTrade).filter_by(trade_id=trade_data['trade_id']).first()
                
                if existing_trade:
                    # Update existing trade
                    for key, value in trade_data.items():
                        if hasattr(existing_trade, key) and value is not None:
                            setattr(existing_trade, key, value)
                    # Update source information
                    existing_trade.source_entity = source_entity
                    existing_trade.source_file = os.path.basename(file_path) if 'file_path' in locals() and file_path else None
                    trade = existing_trade
                else:
                    # Create new trade
                    trade_data = {k: v for k, v in trade_data.items() if v is not None}
                    trade = DTCCOptionTrade(**trade_data)
                    # Add source information
                    trade.source_entity = source_entity
                    trade.source_file = os.path.basename(file_path) if 'file_path' in locals() and file_path else None
                
                self.session.add(trade)
                
                # Add equity option details if available
                if row.get('security_type'):
                    equity_option = DTCCEquityOption(
                        trade_id=trade.trade_id,
                        security_type=row.get('security_type'),
                        security_description=row.get('security_description')
                    )
                    self.session.add(equity_option)
                
                processed += 1
                
                # Commit after each record to maintain data integrity
                self.session.commit()
                
            except Exception as e:
                self.session.rollback()
                errors.append(f"Error processing option trade {row.get('trade_id', 'unknown')}: {str(e)}")
                logger.error(f"Error processing option trade: {str(e)}")
        
        return {
            'status': 'completed',
            'records_processed': processed,
            'errors': errors,
            'file_type': 'OPTION_TRADE'
        }
    
    def _process_interest_rate_swaps(self, df, source_entity):
        """Process interest rate swap data."""
        from dtcc_models import DTCCInterestRateSwap, DTCCOrganization
        
        processed = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Get or create organizations
                reporting_org = self._get_or_create_organization(
                    row.get('reporting_party_lei'),
                    row.get('reporting_party_name')
                )
                
                other_org = self._get_or_create_organization(
                    row.get('other_party_lei'),
                    row.get('other_party_name')
                )
                
                # Prepare swap data with only valid fields
                swap_data = {
                    'trade_id': row['trade_id'],
                    'execution_timestamp': self._parse_datetime(row.get('execution_timestamp')),
                    'effective_date': self._parse_datetime(row.get('effective_date')),
                    'termination_date': self._parse_datetime(row.get('termination_date')),
                    'notional_amount': row.get('notional_amount'),
                    'notional_currency': row.get('notional_currency', 'USD'),
                    'trade_status': row.get('trade_status', 'ACTIVE'),
                    'clearing_status': row.get('clearing_status', 'CLEARED'),
                    'asset_class': 'RATES',
                    'product_type': 'SWAP',
                    'reporting_party_lei': reporting_org.lei,
                    'other_party_lei': other_org.lei,
                    'fixed_rate': row.get('fixed_rate'),
                    'floating_index': row.get('floating_index', 'SOFR'),
                    'day_count_convention': row.get('day_count_convention', 'ACT/360'),
                    'fixed_payment_freq': row.get('payment_frequency', 'QUARTERLY'),
                    'floating_payment_freq': row.get('floating_payment_freq', 'QUARTERLY'),
                    'fixed_rate_day_count': row.get('fixed_rate_day_count', '30/360'),
                    'floating_rate_day_count': row.get('floating_rate_day_count', 'ACT/360')
                }
                
                # Filter out None values
                swap_data = {k: v for k, v in swap_data.items() if v is not None}
                swap = DTCCInterestRateSwap(**swap_data)
                
                # Add source information as metadata if needed
                swap.source_entity = source_entity
                swap.source_file = os.path.basename(file_path) if 'file_path' in locals() and file_path else None
                
                self.session.add(swap)
                processed += 1
                
                # Commit after each record to maintain data integrity
                self.session.commit()
                
            except Exception as e:
                self.session.rollback()
                errors.append(f"Error processing interest rate swap {row.get('trade_id', 'unknown')}: {str(e)}")
                logger.error(f"Error processing interest rate swap: {str(e)}")
        
        return {
            'status': 'completed',
            'records_processed': processed,
            'errors': errors,
            'file_type': 'INTEREST_RATE_SWAP'
        }
    
    def _get_or_create_organization(self, lei, name=None):
        """Get an existing organization or create a new one if it doesn't exist."""
        from dtcc_models import DTCCOrganization
        
        if not lei:
            raise ValueError("LEI is required for organization lookup")
            
        try:
            org = self.session.query(DTCCOrganization).filter_by(lei=lei).one()
        except NoResultFound:
            org = DTCCOrganization(
                lei=lei,
                name=name or f"Unknown Organization ({lei[:8]})",
                created_at=datetime.now(timezone.utc)
            )
            self.session.add(org)
            self.session.commit()
            
        return org
    
    def _parse_datetime(self, dt_str):
        """Parse datetime string to timezone-aware datetime."""
        if pd.isna(dt_str) or not dt_str:
            return None
            
        if isinstance(dt_str, (int, float)):
            # Handle Excel date serial numbers
            return datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(dt_str) - 2)
            
        # Try parsing with common formats
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%Y%m%d'):
            try:
                dt = datetime.strptime(str(dt_str), fmt)
                # Make timezone-aware if not already
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                continue
                
        return None
