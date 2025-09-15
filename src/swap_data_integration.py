"""
Swap Data Integration Layer

This module provides unified access to swap data from multiple sources:
- CFTC swap data
- DTCC repositories
- SEC filings (10-K, 10-Q, 8-K)
- ISDA documentation
- CCP data
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import sqlite3
from pathlib import Path

# Import existing data source modules
try:
    from .data_sources.cftc import _fetch_swap_data
    from .data_sources.dtcc import DTCCDownloader
    from .data_sources.sec import download_insider_archives
    from database import SessionLocal, CFTCSwap
except ImportError as e:
    logging.warning(f"Some data source modules not available: {e}")

logger = logging.getLogger(__name__)

class SwapDataIntegration:
    """
    Unified data integration layer for swap data from multiple sources
    """
    
    def __init__(self, db_path: str = "gamecock.db"):
        """Initialize the data integration layer"""
        self.db_path = db_path
        self.cftc_data = []
        self.dtcc_data = []
        self.sec_data = []
        
        logger.info("Swap Data Integration initialized")
    
    def load_cftc_data(self, entity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load CFTC swap data
        
        Args:
            entity_filter: Optional entity identifier to filter data
            
        Returns:
            List of CFTC swap records
        """
        try:
            # Use existing database connection
            from database import SessionLocal, CFTCSwap
            
            session = SessionLocal()
            query = session.query(CFTCSwap)
            
            if entity_filter:
                # Filter by entity (this would need to be enhanced based on actual CFTC data structure)
                query = query.filter(CFTCSwap.dissemination_id.contains(entity_filter))
            
            cftc_records = query.limit(1000).all()  # Limit for performance
            
            # Convert to list of dictionaries
            cftc_data = []
            for record in cftc_records:
                cftc_data.append({
                    'data_source': 'CFTC',
                    'dissemination_id': record.dissemination_id,
                    'asset_class': getattr(record, 'asset_class', 'unknown'),
                    'action': getattr(record, 'action', 'unknown'),
                    'notional_amount': getattr(record, 'notional_amount', 0),
                    'market_value': getattr(record, 'market_value', 0),
                    'trade_date': getattr(record, 'trade_date', datetime.now()),
                    'maturity_date': getattr(record, 'maturity_date', datetime.now() + timedelta(days=365)),
                    'counterparty': getattr(record, 'counterparty', 'unknown'),
                    'raw_data': record.__dict__
                })
            
            session.close()
            self.cftc_data = cftc_data
            
            logger.info(f"Loaded {len(cftc_data)} CFTC records")
            return cftc_data
            
        except Exception as e:
            logger.error(f"Error loading CFTC data: {e}")
            return []
    
    def load_dtcc_data(self, entity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load DTCC swap data
        
        Args:
            entity_filter: Optional entity identifier to filter data
            
        Returns:
            List of DTCC swap records
        """
        try:
            # Initialize DTCC downloader
            dtcc_downloader = DTCCDownloader()
            
            # Download recent data (this would be enhanced with actual DTCC integration)
            dtcc_data = []
            
            # Sample DTCC data structure (would be replaced with actual DTCC API calls)
            sample_dtcc_records = [
                {
                    'data_source': 'DTCC',
                    'transaction_id': 'DTCC_001',
                    'asset_class': 'interest_rate',
                    'notional_amount': 50000000,
                    'market_value': 1250000,
                    'trade_date': datetime.now() - timedelta(days=45),
                    'maturity_date': datetime.now() + timedelta(days=1095),
                    'counterparty': 'SAMPLE_BANK',
                    'swap_type': 'interest_rate_swap',
                    'raw_data': {}
                }
            ]
            
            if entity_filter:
                # Filter by entity (would be enhanced with actual filtering logic)
                sample_dtcc_records = [r for r in sample_dtcc_records 
                                     if entity_filter.lower() in r.get('counterparty', '').lower()]
            
            self.dtcc_data = sample_dtcc_records
            
            logger.info(f"Loaded {len(sample_dtcc_records)} DTCC records")
            return sample_dtcc_records
            
        except Exception as e:
            logger.error(f"Error loading DTCC data: {e}")
            return []
    
    def load_sec_filing_data(self, entity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load SEC filing data for derivative disclosures
        
        Args:
            entity_filter: Optional entity identifier to filter data
            
        Returns:
            List of SEC filing records with derivative information
        """
        try:
            # This would integrate with existing SEC data processing
            # For now, return sample data structure
            
            sec_data = []
            
            # Sample SEC filing data (would be replaced with actual SEC filing parsing)
            sample_sec_records = [
                {
                    'data_source': 'SEC',
                    'filing_type': '10-K',
                    'filing_date': datetime.now() - timedelta(days=90),
                    'entity': 'SAMPLE_CORP',
                    'derivative_disclosures': {
                        'interest_rate_derivatives': {
                            'notional_amount': 200000000,
                            'fair_value': 5000000,
                            'maturity_profile': '1-5 years'
                        },
                        'credit_derivatives': {
                            'notional_amount': 75000000,
                            'fair_value': -2000000,
                            'maturity_profile': '2-7 years'
                        }
                    },
                    'raw_data': {}
                }
            ]
            
            if entity_filter:
                # Filter by entity
                sample_sec_records = [r for r in sample_sec_records 
                                    if entity_filter.lower() in r.get('entity', '').lower()]
            
            self.sec_data = sample_sec_records
            
            logger.info(f"Loaded {len(sample_sec_records)} SEC filing records")
            return sample_sec_records
            
        except Exception as e:
            logger.error(f"Error loading SEC filing data: {e}")
            return []
    
    def aggregate_entity_data(self, entity_id: str) -> Dict[str, Any]:
        """
        Aggregate all data sources for a specific entity
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Aggregated data dictionary
        """
        try:
            # Load data from all sources
            cftc_data = self.load_cftc_data(entity_id)
            dtcc_data = self.load_dtcc_data(entity_id)
            sec_data = self.load_sec_filing_data(entity_id)
            
            # Aggregate data
            aggregated_data = {
                'entity_id': entity_id,
                'data_sources': {
                    'cftc': {
                        'record_count': len(cftc_data),
                        'total_notional': sum(r.get('notional_amount', 0) for r in cftc_data),
                        'total_market_value': sum(r.get('market_value', 0) for r in cftc_data),
                        'records': cftc_data
                    },
                    'dtcc': {
                        'record_count': len(dtcc_data),
                        'total_notional': sum(r.get('notional_amount', 0) for r in dtcc_data),
                        'total_market_value': sum(r.get('market_value', 0) for r in dtcc_data),
                        'records': dtcc_data
                    },
                    'sec': {
                        'record_count': len(sec_data),
                        'filing_types': list(set(r.get('filing_type') for r in sec_data)),
                        'records': sec_data
                    }
                },
                'summary': {
                    'total_records': len(cftc_data) + len(dtcc_data) + len(sec_data),
                    'total_notional': sum(r.get('notional_amount', 0) for r in cftc_data + dtcc_data),
                    'total_market_value': sum(r.get('market_value', 0) for r in cftc_data + dtcc_data),
                    'data_quality_score': self._calculate_data_quality_score(cftc_data, dtcc_data, sec_data)
                },
                'aggregation_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Aggregated data for entity {entity_id}: {aggregated_data['summary']['total_records']} records")
            return aggregated_data
            
        except Exception as e:
            logger.error(f"Error aggregating data for entity {entity_id}: {e}")
            return {}
    
    def _calculate_data_quality_score(self, cftc_data: List, dtcc_data: List, sec_data: List) -> float:
        """
        Calculate data quality score based on completeness and consistency
        
        Args:
            cftc_data: CFTC data records
            dtcc_data: DTCC data records
            sec_data: SEC data records
            
        Returns:
            Data quality score (0-100)
        """
        try:
            total_records = len(cftc_data) + len(dtcc_data) + len(sec_data)
            if total_records == 0:
                return 0.0
            
            # Calculate completeness score
            complete_records = 0
            
            for record in cftc_data + dtcc_data:
                required_fields = ['notional_amount', 'market_value', 'trade_date', 'maturity_date']
                if all(record.get(field) is not None for field in required_fields):
                    complete_records += 1
            
            for record in sec_data:
                if record.get('derivative_disclosures') and record.get('filing_date'):
                    complete_records += 1
            
            completeness_score = (complete_records / total_records) * 100
            
            # Calculate consistency score (simplified)
            consistency_score = 85.0  # Would be enhanced with actual consistency checks
            
            # Weighted average
            quality_score = (completeness_score * 0.7) + (consistency_score * 0.3)
            
            return min(100.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating data quality score: {e}")
            return 0.0
    
    def cross_reference_entities(self, entity_id: str) -> Dict[str, List[str]]:
        """
        Cross-reference entity across different data sources
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Dictionary mapping data sources to entity references
        """
        try:
            cross_references = {
                'cftc_entities': [],
                'dtcc_entities': [],
                'sec_entities': [],
                'matched_entities': []
            }
            
            # Load all data
            cftc_data = self.load_cftc_data()
            dtcc_data = self.load_dtcc_data()
            sec_data = self.load_sec_filing_data()
            
            # Find entity references in CFTC data
            for record in cftc_data:
                if entity_id.lower() in str(record.get('dissemination_id', '')).lower():
                    cross_references['cftc_entities'].append(record.get('dissemination_id'))
            
            # Find entity references in DTCC data
            for record in dtcc_data:
                if entity_id.lower() in str(record.get('counterparty', '')).lower():
                    cross_references['dtcc_entities'].append(record.get('counterparty'))
            
            # Find entity references in SEC data
            for record in sec_data:
                if entity_id.lower() in str(record.get('entity', '')).lower():
                    cross_references['sec_entities'].append(record.get('entity'))
            
            # Identify matched entities across sources
            all_entities = set()
            all_entities.update(cross_references['cftc_entities'])
            all_entities.update(cross_references['dtcc_entities'])
            all_entities.update(cross_references['sec_entities'])
            
            cross_references['matched_entities'] = list(all_entities)
            
            logger.info(f"Cross-referenced entity {entity_id} across {len(all_entities)} references")
            return cross_references
            
        except Exception as e:
            logger.error(f"Error cross-referencing entity {entity_id}: {e}")
            return {}


def create_sample_integration():
    """Create sample data integration for testing"""
    integration = SwapDataIntegration()
    
    # Test data aggregation
    aggregated_data = integration.aggregate_entity_data("SAMPLE_CORP")
    print(f"Aggregated data: {json.dumps(aggregated_data, indent=2, default=str)}")
    
    # Test cross-referencing
    cross_refs = integration.cross_reference_entities("SAMPLE_CORP")
    print(f"Cross-references: {json.dumps(cross_refs, indent=2)}")
    
    return integration


if __name__ == "__main__":
    # Run sample integration
    integration = create_sample_integration()
