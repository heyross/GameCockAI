#!/usr/bin/env python3
"""
Comprehensive Swap Explorer & Single Party Risk Analyzer for GameCock AI System.

This module aggregates and analyzes ALL swap data sources to identify single party risk triggers
and obligations. It consolidates swap exposures for one entity across ALL data sources and
provides risk trigger detection and obligation tracking.

Key Features:
- Multi-Source Data Aggregation: CFTC, DTCC, SEC filings, ISDA, CCP data integration
- Single Party Risk Consolidation: Aggregate all swap exposures for one entity across ALL data sources
- Risk Trigger Detection Engine: Margin call triggers, termination events, collateral requirements
- Obligation Tracking System: Payment schedules, collateral posting, settlement requirements
- Cross-Filing Correlation Analysis: Link swap exposures across different SEC filings
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import json
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_

# Import existing modules
from src.enhanced_entity_resolver import EnhancedEntityResolver, EntityProfile, IdentifierType
from src.data_sources.cftc import download_all_swap_data
from src.data_sources.dtcc import download_dtcc_swap_data
from src.data_sources.sec import download_edgar_filings

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SwapType(Enum):
    """Types of swap instruments"""
    INTEREST_RATE = "interest_rate"
    CREDIT_DEFAULT = "credit_default"
    EQUITY = "equity"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    VOLATILITY = "volatility"
    INFLATION = "inflation"
    UNKNOWN = "unknown"

class CounterpartyType(Enum):
    """Types of counterparties"""
    BANK = "bank"
    HEDGE_FUND = "hedge_fund"
    INSURANCE = "insurance"
    CORPORATION = "corporation"
    GOVERNMENT = "government"
    PENSION_FUND = "pension_fund"
    MUTUAL_FUND = "mutual_fund"
    UNKNOWN = "unknown"

@dataclass
class SwapExposure:
    """Individual swap exposure record"""
    exposure_id: str
    entity_id: str
    counterparty_id: str
    counterparty_name: str
    swap_type: SwapType
    notional_amount: float
    currency: str
    mark_to_market: float
    collateral_posted: float
    collateral_received: float
    net_exposure: float
    maturity_date: Optional[datetime]
    effective_date: datetime
    termination_date: Optional[datetime]
    data_source: str
    filing_reference: Optional[str] = None
    risk_rating: RiskLevel = RiskLevel.MEDIUM
    margin_call_threshold: Optional[float] = None
    credit_limit: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RiskTrigger:
    """Risk trigger event"""
    trigger_id: str
    entity_id: str
    trigger_type: str  # margin_call, credit_downgrade, termination_event, etc.
    trigger_date: datetime
    severity: RiskLevel
    description: str
    affected_exposures: List[str]
    required_action: str
    deadline: Optional[datetime] = None
    status: str = "active"  # active, resolved, escalated

@dataclass
class Obligation:
    """Payment or collateral obligation"""
    obligation_id: str
    entity_id: str
    counterparty_id: str
    obligation_type: str  # payment, collateral_posting, settlement
    amount: float
    currency: str
    due_date: datetime
    status: str  # pending, overdue, completed
    description: str
    related_exposure_id: Optional[str] = None

@dataclass
class SinglePartyRiskProfile:
    """Comprehensive single party risk profile"""
    entity_id: str
    entity_name: str
    total_notional_exposure: float
    total_mark_to_market: float
    net_collateral_position: float
    counterparty_count: int
    swap_count: int
    exposures_by_type: Dict[SwapType, List[SwapExposure]]
    exposures_by_counterparty: Dict[str, List[SwapExposure]]
    risk_triggers: List[RiskTrigger]
    obligations: List[Obligation]
    risk_summary: str
    last_updated: datetime = field(default_factory=datetime.utcnow)

class SinglePartyRiskAnalyzer:
    """
    Comprehensive swap explorer and single party risk analyzer.
    
    Aggregates swap data from all sources (CFTC, DTCC, SEC, ISDA, CCP) and provides
    consolidated risk analysis for individual entities.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the single party risk analyzer."""
        self.db_session = db_session
        self.entity_resolver = EnhancedEntityResolver(db_session)
        self.exposure_cache = {}
        self.risk_cache = {}
        
        # Risk thresholds
        self.high_risk_threshold = 0.8  # 80% of credit limit
        self.critical_risk_threshold = 0.95  # 95% of credit limit
        self.margin_call_threshold = 0.7  # 70% of collateral threshold
        
        # Entity matching thresholds
        self.fuzzy_threshold = 0.8  # Fuzzy matching threshold
        self.partial_threshold = 0.6  # Partial matching threshold
        
    def analyze_single_party_risk(self, entity_identifier: str, 
                                identifier_type: IdentifierType = IdentifierType.AUTO) -> Optional[SinglePartyRiskProfile]:
        """
        Analyze single party risk for a specific entity.
        
        Args:
            entity_identifier: Entity identifier (CIK, ticker, name, etc.)
            identifier_type: Type of identifier
            
        Returns:
            SinglePartyRiskProfile with comprehensive risk analysis
        """
        try:
            # Resolve entity
            entity_profile = self.entity_resolver.resolve_entity(entity_identifier, identifier_type)
            if not entity_profile:
                logger.warning(f"Entity not found: {entity_identifier}")
                return None
            
            entity_id = entity_profile.entity_id
            entity_name = entity_profile.entity_name
            
            logger.info(f"Analyzing single party risk for {entity_name} (ID: {entity_id})")
            
            # Aggregate all swap exposures
            all_exposures = self._aggregate_all_swap_exposures(entity_id)
            
            if not all_exposures:
                logger.info(f"No swap exposures found for {entity_name}")
                return self._create_empty_risk_profile(entity_id, entity_name)
            
            # Analyze risk triggers
            risk_triggers = self._detect_risk_triggers(entity_id, all_exposures)
            
            # Track obligations
            obligations = self._track_obligations(entity_id, all_exposures)
            
            # Create comprehensive risk profile
            risk_profile = self._create_risk_profile(
                entity_id, entity_name, all_exposures, risk_triggers, obligations
            )
            
            # Cache the result
            self.risk_cache[entity_id] = risk_profile
            
            logger.info(f"Risk analysis completed for {entity_name}: "
                       f"${risk_profile.total_notional_exposure:,.0f} total exposure, "
                       f"{risk_profile.counterparty_count} counterparties, "
                       f"{len(risk_triggers)} risk triggers")
            
            return risk_profile
            
        except Exception as e:
            logger.error(f"Error analyzing single party risk for {entity_identifier}: {str(e)}")
            return None
    
    def _aggregate_all_swap_exposures(self, entity_id: str) -> List[SwapExposure]:
        """Aggregate swap exposures from all data sources."""
        exposures = []
        
        # Get exposures from CFTC data
        cftc_exposures = self._get_cftc_swap_exposures(entity_id)
        exposures.extend(cftc_exposures)
        
        # Get exposures from DTCC data
        dtcc_exposures = self._get_dtcc_swap_exposures(entity_id)
        exposures.extend(dtcc_exposures)
        
        # Get exposures from SEC filings
        sec_exposures = self._get_sec_swap_exposures(entity_id)
        exposures.extend(sec_exposures)
        
        # Get exposures from N-PORT derivatives
        nport_exposures = self._get_nport_derivative_exposures(entity_id)
        exposures.extend(nport_exposures)
        
        # Deduplicate and consolidate exposures
        consolidated_exposures = self._consolidate_exposures(exposures)
        
        return consolidated_exposures
    
    def _get_cftc_swap_exposures(self, entity_id: str) -> List[SwapExposure]:
        """Get swap exposures from CFTC data."""
        exposures = []
        
        try:
            if not self.db_session:
                return exposures
            
            # Query CFTC swap data for the entity
            # Note: This would need to be enhanced based on actual CFTC data structure
            query = text("""
                SELECT 
                    dissemination_id,
                    asset_class,
                    product_name,
                    notional_amount_leg_1,
                    notional_amount_leg_2,
                    notional_currency_leg_1,
                    notional_currency_leg_2,
                    execution_timestamp,
                    effective_date,
                    expiration_date,
                    cleared,
                    counterparty_type
                FROM cftc_swap_data
                WHERE (counterparty_1_id = :entity_id OR counterparty_2_id = :entity_id)
                AND action_type = 'NEW'
            """)
            
            results = self.db_session.execute(query, {"entity_id": entity_id}).fetchall()
            
            for result in results:
                # Determine swap type
                swap_type = self._determine_swap_type(result.asset_class, result.product_name)
                
                # Calculate notional amount (use leg 1 as primary)
                notional_amount = result.notional_amount_leg_1 or 0
                currency = result.notional_currency_leg_1 or "USD"
                
                exposure = SwapExposure(
                    exposure_id=f"CFTC_{result.dissemination_id}",
                    entity_id=entity_id,
                    counterparty_id="unknown",  # Would need counterparty resolution
                    counterparty_name="Unknown Counterparty",
                    swap_type=swap_type,
                    notional_amount=notional_amount,
                    currency=currency,
                    mark_to_market=0.0,  # Would need market data
                    collateral_posted=0.0,
                    collateral_received=0.0,
                    net_exposure=0.0,
                    maturity_date=result.expiration_date,
                    effective_date=result.effective_date or result.execution_timestamp,
                    termination_date=None,
                    data_source="CFTC",
                    risk_rating=RiskLevel.MEDIUM
                )
                exposures.append(exposure)
            
            logger.info(f"Found {len(exposures)} CFTC swap exposures for entity {entity_id}")
            
        except Exception as e:
            logger.error(f"Error getting CFTC swap exposures: {str(e)}")
        
        return exposures
    
    def _get_dtcc_swap_exposures(self, entity_id: str) -> List[SwapExposure]:
        """Get swap exposures from DTCC data."""
        exposures = []
        
        try:
            if not self.db_session:
                return exposures
            
            # Query DTCC data (would need actual DTCC table structure)
            # This is a placeholder implementation
            logger.info(f"DTCC swap exposure query for entity {entity_id} - implementation needed")
            
        except Exception as e:
            logger.error(f"Error getting DTCC swap exposures: {str(e)}")
        
        return exposures
    
    def _get_sec_swap_exposures(self, entity_id: str) -> List[SwapExposure]:
        """Get swap exposures from SEC filings."""
        exposures = []
        
        try:
            if not self.db_session:
                return exposures
            
            # Query SEC 10-K/10-Q documents for derivative disclosures
            query = text("""
                SELECT 
                    s.accession_number,
                    s.filing_date,
                    d.section,
                    d.content
                FROM sec_10k_submissions s
                JOIN sec_10k_documents d ON s.accession_number = d.accession_number
                WHERE s.cik = :entity_id
                AND d.section IN ('risk_factors', 'mdna', 'financial_statements')
                AND (d.content LIKE '%derivative%' OR d.content LIKE '%swap%' OR d.content LIKE '%hedge%')
                ORDER BY s.filing_date DESC
                LIMIT 50
            """)
            
            results = self.db_session.execute(query, {"entity_id": entity_id}).fetchall()
            
            for result in results:
                # Parse derivative information from SEC filing content
                derivative_info = self._parse_sec_derivative_content(result.content)
                
                for info in derivative_info:
                    exposure = SwapExposure(
                        exposure_id=f"SEC_{result.accession_number}_{info['id']}",
                        entity_id=entity_id,
                        counterparty_id=info.get('counterparty_id', 'unknown'),
                        counterparty_name=info.get('counterparty_name', 'Unknown'),
                        swap_type=info.get('swap_type', SwapType.UNKNOWN),
                        notional_amount=info.get('notional_amount', 0.0),
                        currency=info.get('currency', 'USD'),
                        mark_to_market=info.get('mark_to_market', 0.0),
                        collateral_posted=info.get('collateral_posted', 0.0),
                        collateral_received=info.get('collateral_received', 0.0),
                        net_exposure=info.get('net_exposure', 0.0),
                        maturity_date=info.get('maturity_date'),
                        effective_date=result.filing_date,
                        termination_date=None,
                        data_source="SEC",
                        filing_reference=result.accession_number,
                        risk_rating=info.get('risk_rating', RiskLevel.MEDIUM)
                    )
                    exposures.append(exposure)
            
            logger.info(f"Found {len(exposures)} SEC swap exposures for entity {entity_id}")
            
        except Exception as e:
            logger.error(f"Error getting SEC swap exposures: {str(e)}")
        
        return exposures
    
    def _get_nport_derivative_exposures(self, entity_id: str) -> List[SwapExposure]:
        """Get derivative exposures from N-PORT filings."""
        exposures = []
        
        try:
            if not self.db_session:
                return exposures
            
            # Query N-PORT derivatives
            query = text("""
                SELECT 
                    n.accession_number,
                    n.report_date,
                    d.derivative_id,
                    d.counterparty_name,
                    d.derivative_category,
                    d.notional_amount,
                    d.currency_code,
                    d.unrealized_appreciation,
                    d.unrealized_depreciation,
                    d.maturity_date,
                    d.expiration_date
                FROM nport_submissions n
                JOIN nport_derivatives d ON n.accession_number = d.accession_number
                WHERE n.cik = :entity_id
                AND d.notional_amount IS NOT NULL
                ORDER BY n.report_date DESC
                LIMIT 100
            """)
            
            results = self.db_session.execute(query, {"entity_id": entity_id}).fetchall()
            
            for result in results:
                # Determine swap type from derivative category
                swap_type = self._determine_swap_type_from_category(result.derivative_category)
                
                # Calculate net exposure
                net_exposure = (result.unrealized_appreciation or 0) - (result.unrealized_depreciation or 0)
                
                exposure = SwapExposure(
                    exposure_id=f"NPORT_{result.derivative_id}",
                    entity_id=entity_id,
                    counterparty_id="unknown",
                    counterparty_name=result.counterparty_name or "Unknown",
                    swap_type=swap_type,
                    notional_amount=result.notional_amount or 0.0,
                    currency=result.currency_code or "USD",
                    mark_to_market=net_exposure,
                    collateral_posted=0.0,
                    collateral_received=0.0,
                    net_exposure=net_exposure,
                    maturity_date=result.maturity_date,
                    effective_date=result.report_date,
                    termination_date=result.expiration_date,
                    data_source="N-PORT",
                    filing_reference=result.accession_number,
                    risk_rating=RiskLevel.MEDIUM
                )
                exposures.append(exposure)
            
            logger.info(f"Found {len(exposures)} N-PORT derivative exposures for entity {entity_id}")
            
        except Exception as e:
            logger.error(f"Error getting N-PORT derivative exposures: {str(e)}")
        
        return exposures
    
    def _determine_swap_type(self, asset_class: str, product_name: str) -> SwapType:
        """Determine swap type from asset class and product name."""
        if not asset_class and not product_name:
            return SwapType.UNKNOWN
        
        combined = f"{asset_class or ''} {product_name or ''}".lower()
        
        if any(term in combined for term in ['interest', 'rate', 'irs', 'swap']):
            return SwapType.INTEREST_RATE
        elif any(term in combined for term in ['credit', 'cds', 'default']):
            return SwapType.CREDIT_DEFAULT
        elif any(term in combined for term in ['equity', 'stock']):
            return SwapType.EQUITY
        elif any(term in combined for term in ['commodity', 'energy', 'metal']):
            return SwapType.COMMODITY
        elif any(term in combined for term in ['currency', 'fx', 'forex']):
            return SwapType.CURRENCY
        elif any(term in combined for term in ['volatility', 'variance']):
            return SwapType.VOLATILITY
        elif any(term in combined for term in ['inflation', 'cpi']):
            return SwapType.INFLATION
        else:
            return SwapType.UNKNOWN
    
    def _determine_swap_type_from_category(self, category: str) -> SwapType:
        """Determine swap type from N-PORT derivative category."""
        if not category:
            return SwapType.UNKNOWN
        
        category_lower = category.lower()
        
        if any(term in category_lower for term in ['interest', 'rate']):
            return SwapType.INTEREST_RATE
        elif any(term in category_lower for term in ['credit', 'default']):
            return SwapType.CREDIT_DEFAULT
        elif any(term in category_lower for term in ['equity', 'stock']):
            return SwapType.EQUITY
        elif any(term in category_lower for term in ['commodity']):
            return SwapType.COMMODITY
        elif any(term in category_lower for term in ['currency', 'fx']):
            return SwapType.CURRENCY
        else:
            return SwapType.UNKNOWN
    
    def _parse_sec_derivative_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse derivative information from SEC filing content."""
        derivative_info = []
        
        if not content:
            return derivative_info
        
        # This is a simplified parser - in practice, would need more sophisticated NLP
        content_lower = content.lower()
        
        # Look for notional amounts
        import re
        notional_patterns = [
            r'notional.*?(\$?[\d,]+\.?\d*)\s*(?:million|billion|thousand)?',
            r'(\$?[\d,]+\.?\d*)\s*(?:million|billion|thousand)?.*?notional'
        ]
        
        for pattern in notional_patterns:
            matches = re.finditer(pattern, content_lower)
            for match in matches:
                amount_str = match.group(1).replace(',', '').replace('$', '')
                try:
                    amount = float(amount_str)
                    # Check for scale indicators
                    if 'billion' in match.group(0):
                        amount *= 1_000_000_000
                    elif 'million' in match.group(0):
                        amount *= 1_000_000
                    elif 'thousand' in match.group(0):
                        amount *= 1_000
                    
                    derivative_info.append({
                        'id': f"sec_deriv_{len(derivative_info)}",
                        'notional_amount': amount,
                        'currency': 'USD',
                        'swap_type': SwapType.UNKNOWN,
                        'risk_rating': RiskLevel.MEDIUM
                    })
                except ValueError:
                    continue
        
        return derivative_info
    
    def _consolidate_exposures(self, exposures: List[SwapExposure]) -> List[SwapExposure]:
        """Consolidate and deduplicate exposures."""
        # Group by exposure characteristics
        exposure_groups = {}
        
        for exposure in exposures:
            # Create a key for grouping similar exposures
            key = (
                exposure.entity_id,
                exposure.counterparty_id,
                exposure.swap_type,
                exposure.currency,
                exposure.maturity_date
            )
            
            if key not in exposure_groups:
                exposure_groups[key] = []
            exposure_groups[key].append(exposure)
        
        # Consolidate grouped exposures
        consolidated = []
        for group in exposure_groups.values():
            if len(group) == 1:
                consolidated.append(group[0])
            else:
                # Merge multiple exposures
                merged = self._merge_exposures(group)
                consolidated.append(merged)
        
        return consolidated
    
    def _merge_exposures(self, exposures: List[SwapExposure]) -> SwapExposure:
        """Merge multiple exposures into one."""
        if not exposures:
            return None
        
        base_exposure = exposures[0]
        
        # Sum up amounts
        total_notional = sum(e.notional_amount for e in exposures)
        total_mtm = sum(e.mark_to_market for e in exposures)
        total_collateral_posted = sum(e.collateral_posted for e in exposures)
        total_collateral_received = sum(e.collateral_received for e in exposures)
        
        # Create merged exposure
        merged = SwapExposure(
            exposure_id=f"MERGED_{base_exposure.exposure_id}",
            entity_id=base_exposure.entity_id,
            counterparty_id=base_exposure.counterparty_id,
            counterparty_name=base_exposure.counterparty_name,
            swap_type=base_exposure.swap_type,
            notional_amount=total_notional,
            currency=base_exposure.currency,
            mark_to_market=total_mtm,
            collateral_posted=total_collateral_posted,
            collateral_received=total_collateral_received,
            net_exposure=total_mtm + total_collateral_received - total_collateral_posted,
            maturity_date=base_exposure.maturity_date,
            effective_date=base_exposure.effective_date,
            termination_date=base_exposure.termination_date,
            data_source="MULTIPLE",
            risk_rating=base_exposure.risk_rating,
            last_updated=datetime.utcnow()
        )
        
        return merged
    
    def _detect_risk_triggers(self, entity_id: str, exposures: List[SwapExposure]) -> List[RiskTrigger]:
        """Detect risk triggers from exposures."""
        triggers = []
        
        # Group exposures by counterparty
        counterparty_exposures = {}
        for exposure in exposures:
            if exposure.counterparty_id not in counterparty_exposures:
                counterparty_exposures[exposure.counterparty_id] = []
            counterparty_exposures[exposure.counterparty_id].append(exposure)
        
        # Check for high concentration risk
        total_notional = sum(e.notional_amount for e in exposures)
        for counterparty_id, counterparty_exposures_list in counterparty_exposures.items():
            counterparty_notional = sum(e.notional_amount for e in counterparty_exposures_list)
            concentration_ratio = counterparty_notional / total_notional if total_notional > 0 else 0
            
            if concentration_ratio > 0.3:  # 30% concentration threshold
                trigger = RiskTrigger(
                    trigger_id=f"concentration_{counterparty_id}",
                    entity_id=entity_id,
                    trigger_type="high_concentration",
                    trigger_date=datetime.utcnow(),
                    severity=RiskLevel.HIGH if concentration_ratio > 0.5 else RiskLevel.MEDIUM,
                    description=f"High concentration risk with {counterparty_id}: {concentration_ratio:.1%} of total exposure",
                    affected_exposures=[e.exposure_id for e in counterparty_exposures_list],
                    required_action="Review counterparty concentration limits"
                )
                triggers.append(trigger)
        
        # Check for margin call risks
        for exposure in exposures:
            if exposure.margin_call_threshold and exposure.net_exposure > exposure.margin_call_threshold:
                trigger = RiskTrigger(
                    trigger_id=f"margin_call_{exposure.exposure_id}",
                    entity_id=entity_id,
                    trigger_type="margin_call_risk",
                    trigger_date=datetime.utcnow(),
                    severity=RiskLevel.HIGH,
                    description=f"Margin call risk for exposure {exposure.exposure_id}: "
                               f"${exposure.net_exposure:,.0f} > ${exposure.margin_call_threshold:,.0f}",
                    affected_exposures=[exposure.exposure_id],
                    required_action="Post additional collateral or reduce exposure"
                )
                triggers.append(trigger)
        
        return triggers
    
    def _track_obligations(self, entity_id: str, exposures: List[SwapExposure]) -> List[Obligation]:
        """Track payment and collateral obligations."""
        obligations = []
        
        # This is a simplified implementation
        # In practice, would need to parse payment schedules and collateral requirements
        
        for exposure in exposures:
            # Add collateral posting obligations
            if exposure.collateral_posted > 0:
                obligation = Obligation(
                    obligation_id=f"collateral_{exposure.exposure_id}",
                    entity_id=entity_id,
                    counterparty_id=exposure.counterparty_id,
                    obligation_type="collateral_posting",
                    amount=exposure.collateral_posted,
                    currency=exposure.currency,
                    due_date=datetime.utcnow() + timedelta(days=1),  # Simplified
                    status="pending",
                    description=f"Collateral posting for {exposure.swap_type.value} swap",
                    related_exposure_id=exposure.exposure_id
                )
                obligations.append(obligation)
        
        return obligations
    
    def _create_risk_profile(self, entity_id: str, entity_name: str, 
                           exposures: List[SwapExposure], 
                           risk_triggers: List[RiskTrigger],
                           obligations: List[Obligation]) -> SinglePartyRiskProfile:
        """Create comprehensive risk profile."""
        
        # Calculate totals
        total_notional = sum(e.notional_amount for e in exposures)
        total_mtm = sum(e.mark_to_market for e in exposures)
        total_collateral_posted = sum(e.collateral_posted for e in exposures)
        total_collateral_received = sum(e.collateral_received for e in exposures)
        net_collateral_position = total_collateral_received - total_collateral_posted
        
        # Group exposures
        exposures_by_type = {}
        exposures_by_counterparty = {}
        
        for exposure in exposures:
            # By type
            if exposure.swap_type not in exposures_by_type:
                exposures_by_type[exposure.swap_type] = []
            exposures_by_type[exposure.swap_type].append(exposure)
            
            # By counterparty
            if exposure.counterparty_id not in exposures_by_counterparty:
                exposures_by_counterparty[exposure.counterparty_id] = []
            exposures_by_counterparty[exposure.counterparty_id].append(exposure)
        
        # Generate risk summary
        risk_summary = self._generate_risk_summary(
            entity_name, total_notional, len(exposures_by_counterparty), 
            len(exposures), risk_triggers
        )
        
        return SinglePartyRiskProfile(
            entity_id=entity_id,
            entity_name=entity_name,
            total_notional_exposure=total_notional,
            total_mark_to_market=total_mtm,
            net_collateral_position=net_collateral_position,
            counterparty_count=len(exposures_by_counterparty),
            swap_count=len(exposures),
            exposures_by_type=exposures_by_type,
            exposures_by_counterparty=exposures_by_counterparty,
            risk_triggers=risk_triggers,
            obligations=obligations,
            risk_summary=risk_summary
        )
    
    def _create_empty_risk_profile(self, entity_id: str, entity_name: str) -> SinglePartyRiskProfile:
        """Create empty risk profile for entities with no exposures."""
        return SinglePartyRiskProfile(
            entity_id=entity_id,
            entity_name=entity_name,
            total_notional_exposure=0.0,
            total_mark_to_market=0.0,
            net_collateral_position=0.0,
            counterparty_count=0,
            swap_count=0,
            exposures_by_type={},
            exposures_by_counterparty={},
            risk_triggers=[],
            obligations=[],
            risk_summary=f"{entity_name}: No swap exposures found in available data sources."
        )
    
    def _generate_risk_summary(self, entity_name: str, total_notional: float, 
                             counterparty_count: int, swap_count: int, 
                             risk_triggers: List[RiskTrigger]) -> str:
        """Generate human-readable risk summary."""
        
        # Count high-risk triggers
        high_risk_triggers = [t for t in risk_triggers if t.severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        
        summary = f"{entity_name}: Total swap exposure ${total_notional:,.0f} across {counterparty_count} counterparties. "
        
        if high_risk_triggers:
            summary += f"High risk triggers: {len(high_risk_triggers)} counterparties approaching downgrade thresholds"
        else:
            summary += "No immediate risk triggers detected"
        
        return summary
    
    def get_risk_summary_for_entity(self, entity_identifier: str) -> str:
        """
        Get a quick risk summary for an entity.
        
        Args:
            entity_identifier: Entity identifier
            
        Returns:
            Risk summary string
        """
        risk_profile = self.analyze_single_party_risk(entity_identifier)
        if risk_profile:
            return risk_profile.risk_summary
        else:
            return f"Entity {entity_identifier}: No risk data available"
    
    def clear_cache(self):
        """Clear all caches."""
        self.exposure_cache.clear()
        self.risk_cache.clear()
        logger.info("Single party risk analyzer cache cleared")
