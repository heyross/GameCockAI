#!/usr/bin/env python3
"""
Swap Obligation & Payment Tracking System for GameCock AI System.

This module tracks all swap-related obligations, payments, and collateral requirements.
It provides payment schedule aggregation, collateral management, settlement tracking,
and regulatory obligation compliance monitoring.

Key Features:
- Payment Schedule Aggregation: Consolidate payment schedules from all swap types and counterparties
- Collateral Obligation Management: Track initial margin, variation margin, collateral posting
- Settlement & Delivery Tracking: Monitor physical and cash settlement obligations
- Regulatory Obligation Compliance: Track regulatory reporting requirements and deadlines
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
from ..enhanced_entity_resolver import EnhancedEntityResolver, EntityProfile, IdentifierType
from ..swap_analysis.single_party_risk_analyzer import SinglePartyRiskAnalyzer, SwapExposure, RiskLevel

logger = logging.getLogger(__name__)

class ObligationType(Enum):
    """Types of obligations"""
    PAYMENT = "payment"
    COLLATERAL_POSTING = "collateral_posting"
    COLLATERAL_RETURN = "collateral_return"
    SETTLEMENT = "settlement"
    DELIVERY = "delivery"
    REGULATORY_REPORTING = "regulatory_reporting"
    MARGIN_CALL = "margin_call"
    TERMINATION_PAYMENT = "termination_payment"

class ObligationStatus(Enum):
    """Status of obligations"""
    PENDING = "pending"
    OVERDUE = "overdue"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    ESCALATED = "escalated"

class CollateralType(Enum):
    """Types of collateral"""
    CASH = "cash"
    GOVERNMENT_SECURITIES = "government_securities"
    CORPORATE_BONDS = "corporate_bonds"
    EQUITY_SECURITIES = "equity_securities"
    LETTER_OF_CREDIT = "letter_of_credit"
    OTHER = "other"

class SettlementType(Enum):
    """Types of settlement"""
    CASH = "cash"
    PHYSICAL = "physical"
    NET_SETTLEMENT = "net_settlement"
    GROSS_SETTLEMENT = "gross_settlement"

@dataclass
class PaymentSchedule:
    """Payment schedule for a swap"""
    schedule_id: str
    swap_exposure_id: str
    payment_date: datetime
    payment_amount: float
    currency: str
    payment_type: str  # fixed, floating, principal, interest
    counterparty_id: str
    is_payer: bool  # True if entity is paying, False if receiving
    status: ObligationStatus = ObligationStatus.PENDING
    actual_payment_date: Optional[datetime] = None
    actual_payment_amount: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CollateralObligation:
    """Collateral obligation"""
    obligation_id: str
    swap_exposure_id: str
    counterparty_id: str
    collateral_type: CollateralType
    required_amount: float
    currency: str
    due_date: datetime
    obligation_type: ObligationType
    status: ObligationStatus = ObligationStatus.PENDING
    actual_amount: Optional[float] = None
    actual_date: Optional[datetime] = None
    collateral_value: Optional[float] = None
    haircut: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SettlementObligation:
    """Settlement obligation"""
    settlement_id: str
    swap_exposure_id: str
    counterparty_id: str
    settlement_type: SettlementType
    settlement_amount: float
    currency: str
    settlement_date: datetime
    underlying_asset: Optional[str] = None
    quantity: Optional[float] = None
    status: ObligationStatus = ObligationStatus.PENDING
    actual_settlement_date: Optional[datetime] = None
    actual_settlement_amount: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RegulatoryObligation:
    """Regulatory reporting obligation"""
    regulatory_id: str
    entity_id: str
    regulation_type: str  # CFTC, SEC, ISDA, etc.
    reporting_requirement: str
    due_date: datetime
    frequency: str  # daily, weekly, monthly, quarterly, annually
    status: ObligationStatus = ObligationStatus.PENDING
    last_filed_date: Optional[datetime] = None
    next_due_date: Optional[datetime] = None
    penalty_risk: RiskLevel = RiskLevel.LOW
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ObligationSummary:
    """Summary of all obligations for an entity"""
    entity_id: str
    entity_name: str
    total_payment_obligations: float
    total_collateral_obligations: float
    total_settlement_obligations: float
    overdue_obligations: int
    upcoming_obligations: int
    payment_schedules: List[PaymentSchedule]
    collateral_obligations: List[CollateralObligation]
    settlement_obligations: List[SettlementObligation]
    regulatory_obligations: List[RegulatoryObligation]
    risk_summary: str
    last_updated: datetime = field(default_factory=datetime.utcnow)

class ObligationTrackingSystem:
    """
    Swap obligation and payment tracking system that monitors all swap-related
    obligations, payments, and collateral requirements.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the obligation tracking system."""
        self.db_session = db_session
        self.entity_resolver = EnhancedEntityResolver(db_session)
        self.risk_analyzer = SinglePartyRiskAnalyzer(db_session)
        self.obligation_cache = {}
        
        # Obligation tracking parameters
        self.overdue_threshold_days = 1
        self.upcoming_threshold_days = 30
        
    def track_entity_obligations(self, entity_identifier: str, 
                               identifier_type: IdentifierType = IdentifierType.AUTO) -> Optional[ObligationSummary]:
        """
        Track all obligations for a specific entity.
        
        Args:
            entity_identifier: Entity identifier
            identifier_type: Type of identifier
            
        Returns:
            ObligationSummary with all tracked obligations
        """
        try:
            # Resolve entity
            entity_profile = self.entity_resolver.resolve_entity(entity_identifier, identifier_type)
            if not entity_profile:
                logger.warning(f"Entity not found: {entity_identifier}")
                return None
            
            entity_id = entity_profile.entity_id
            entity_name = entity_profile.entity_name
            
            logger.info(f"Tracking obligations for {entity_name} (ID: {entity_id})")
            
            # Get swap exposures
            risk_profile = self.risk_analyzer.analyze_single_party_risk(entity_id)
            if not risk_profile:
                logger.info(f"No swap exposures found for {entity_name}")
                return self._create_empty_obligation_summary(entity_id, entity_name)
            
            # Extract all exposures
            all_exposures = []
            for exposures in risk_profile.exposures_by_type.values():
                all_exposures.extend(exposures)
            
            # Track different types of obligations
            payment_schedules = self._track_payment_schedules(entity_id, all_exposures)
            collateral_obligations = self._track_collateral_obligations(entity_id, all_exposures)
            settlement_obligations = self._track_settlement_obligations(entity_id, all_exposures)
            regulatory_obligations = self._track_regulatory_obligations(entity_id)
            
            # Create obligation summary
            obligation_summary = self._create_obligation_summary(
                entity_id, entity_name, payment_schedules, collateral_obligations,
                settlement_obligations, regulatory_obligations
            )
            
            # Cache the result
            self.obligation_cache[entity_id] = obligation_summary
            
            logger.info(f"Obligation tracking completed for {entity_name}: "
                       f"${obligation_summary.total_payment_obligations:,.0f} payment obligations, "
                       f"${obligation_summary.total_collateral_obligations:,.0f} collateral obligations, "
                       f"{obligation_summary.overdue_obligations} overdue")
            
            return obligation_summary
            
        except Exception as e:
            logger.error(f"Error tracking obligations for {entity_identifier}: {str(e)}")
            return None
    
    def _track_payment_schedules(self, entity_id: str, exposures: List[SwapExposure]) -> List[PaymentSchedule]:
        """Track payment schedules from swap exposures."""
        payment_schedules = []
        
        for exposure in exposures:
            # Generate payment schedules based on swap type and terms
            schedules = self._generate_payment_schedules(entity_id, exposure)
            payment_schedules.extend(schedules)
        
        return payment_schedules
    
    def _generate_payment_schedules(self, entity_id: str, exposure: SwapExposure) -> List[PaymentSchedule]:
        """Generate payment schedules for a specific swap exposure."""
        schedules = []
        
        # This is a simplified implementation
        # In practice, would need to parse actual swap terms and payment schedules
        
        if exposure.maturity_date:
            # Generate quarterly payments for the life of the swap
            current_date = exposure.effective_date
            payment_frequency = timedelta(days=90)  # Quarterly
            
            payment_count = 0
            while current_date < exposure.maturity_date:
                # Calculate payment amount (simplified)
                payment_amount = exposure.notional_amount * 0.01  # 1% quarterly payment
                
                # Determine if entity is payer or receiver (simplified logic)
                is_payer = exposure.net_exposure < 0  # If net exposure is negative, entity is paying
                
                schedule = PaymentSchedule(
                    schedule_id=f"PAY_{exposure.exposure_id}_{payment_count}",
                    swap_exposure_id=exposure.exposure_id,
                    payment_date=current_date,
                    payment_amount=payment_amount,
                    currency=exposure.currency,
                    payment_type="interest",
                    counterparty_id=exposure.counterparty_id,
                    is_payer=is_payer,
                    status=ObligationStatus.PENDING if current_date > datetime.utcnow() else ObligationStatus.COMPLETED
                )
                schedules.append(schedule)
                
                current_date += payment_frequency
                payment_count += 1
        
        return schedules
    
    def _track_collateral_obligations(self, entity_id: str, exposures: List[SwapExposure]) -> List[CollateralObligation]:
        """Track collateral obligations from swap exposures."""
        collateral_obligations = []
        
        for exposure in exposures:
            # Initial margin obligations
            if exposure.collateral_posted > 0:
                obligation = CollateralObligation(
                    obligation_id=f"COLL_INIT_{exposure.exposure_id}",
                    swap_exposure_id=exposure.exposure_id,
                    counterparty_id=exposure.counterparty_id,
                    collateral_type=CollateralType.CASH,
                    required_amount=exposure.collateral_posted,
                    currency=exposure.currency,
                    due_date=exposure.effective_date,
                    obligation_type=ObligationType.COLLATERAL_POSTING,
                    status=ObligationStatus.COMPLETED if exposure.effective_date < datetime.utcnow() else ObligationStatus.PENDING,
                    actual_amount=exposure.collateral_posted,
                    actual_date=exposure.effective_date if exposure.effective_date < datetime.utcnow() else None
                )
                collateral_obligations.append(obligation)
            
            # Variation margin obligations (simplified)
            if exposure.mark_to_market != 0:
                # If mark-to-market is negative, entity owes variation margin
                if exposure.mark_to_market < 0:
                    obligation = CollateralObligation(
                        obligation_id=f"COLL_VAR_{exposure.exposure_id}",
                        swap_exposure_id=exposure.exposure_id,
                        counterparty_id=exposure.counterparty_id,
                        collateral_type=CollateralType.CASH,
                        required_amount=abs(exposure.mark_to_market),
                        currency=exposure.currency,
                        due_date=datetime.utcnow() + timedelta(days=1),  # Next business day
                        obligation_type=ObligationType.MARGIN_CALL,
                        status=ObligationStatus.PENDING
                    )
                    collateral_obligations.append(obligation)
        
        return collateral_obligations
    
    def _track_settlement_obligations(self, entity_id: str, exposures: List[SwapExposure]) -> List[SettlementObligation]:
        """Track settlement obligations from swap exposures."""
        settlement_obligations = []
        
        for exposure in exposures:
            if exposure.maturity_date:
                # Final settlement obligation
                settlement = SettlementObligation(
                    settlement_id=f"SETTLE_{exposure.exposure_id}",
                    swap_exposure_id=exposure.exposure_id,
                    counterparty_id=exposure.counterparty_id,
                    settlement_type=SettlementType.CASH,
                    settlement_amount=exposure.notional_amount,
                    currency=exposure.currency,
                    settlement_date=exposure.maturity_date,
                    status=ObligationStatus.PENDING if exposure.maturity_date > datetime.utcnow() else ObligationStatus.COMPLETED
                )
                settlement_obligations.append(settlement)
        
        return settlement_obligations
    
    def _track_regulatory_obligations(self, entity_id: str) -> List[RegulatoryObligation]:
        """Track regulatory reporting obligations."""
        regulatory_obligations = []
        
        # CFTC reporting obligations
        cftc_obligation = RegulatoryObligation(
            regulatory_id=f"CFTC_{entity_id}",
            entity_id=entity_id,
            regulation_type="CFTC",
            reporting_requirement="Daily swap reporting",
            due_date=datetime.utcnow() + timedelta(days=1),
            frequency="daily",
            status=ObligationStatus.PENDING,
            next_due_date=datetime.utcnow() + timedelta(days=1),
            penalty_risk=RiskLevel.HIGH
        )
        regulatory_obligations.append(cftc_obligation)
        
        # SEC reporting obligations
        sec_obligation = RegulatoryObligation(
            regulatory_id=f"SEC_{entity_id}",
            entity_id=entity_id,
            regulation_type="SEC",
            reporting_requirement="Quarterly derivative disclosures",
            due_date=datetime.utcnow() + timedelta(days=45),  # 45 days after quarter end
            frequency="quarterly",
            status=ObligationStatus.PENDING,
            next_due_date=datetime.utcnow() + timedelta(days=45),
            penalty_risk=RiskLevel.MEDIUM
        )
        regulatory_obligations.append(sec_obligation)
        
        # ISDA reporting obligations
        isda_obligation = RegulatoryObligation(
            regulatory_id=f"ISDA_{entity_id}",
            entity_id=entity_id,
            regulation_type="ISDA",
            reporting_requirement="ISDA SIMM margin reporting",
            due_date=datetime.utcnow() + timedelta(days=1),
            frequency="daily",
            status=ObligationStatus.PENDING,
            next_due_date=datetime.utcnow() + timedelta(days=1),
            penalty_risk=RiskLevel.HIGH
        )
        regulatory_obligations.append(isda_obligation)
        
        return regulatory_obligations
    
    def _create_obligation_summary(self, entity_id: str, entity_name: str,
                                 payment_schedules: List[PaymentSchedule],
                                 collateral_obligations: List[CollateralObligation],
                                 settlement_obligations: List[SettlementObligation],
                                 regulatory_obligations: List[RegulatoryObligation]) -> ObligationSummary:
        """Create comprehensive obligation summary."""
        
        # Calculate totals
        total_payment_obligations = sum(s.payment_amount for s in payment_schedules 
                                      if s.status == ObligationStatus.PENDING)
        total_collateral_obligations = sum(c.required_amount for c in collateral_obligations 
                                         if c.status == ObligationStatus.PENDING)
        total_settlement_obligations = sum(s.settlement_amount for s in settlement_obligations 
                                         if s.status == ObligationStatus.PENDING)
        
        # Count overdue obligations
        overdue_threshold = datetime.utcnow() - timedelta(days=self.overdue_threshold_days)
        overdue_count = 0
        
        # Check payment schedules
        for schedule in payment_schedules:
            if schedule.status == ObligationStatus.PENDING and schedule.payment_date < overdue_threshold:
                overdue_count += 1
        
        # Check collateral obligations
        for obligation in collateral_obligations:
            if obligation.status == ObligationStatus.PENDING and obligation.due_date < overdue_threshold:
                overdue_count += 1
        
        # Check settlement obligations
        for settlement in settlement_obligations:
            if settlement.status == ObligationStatus.PENDING and settlement.settlement_date < overdue_threshold:
                overdue_count += 1
        
        # Check regulatory obligations
        for regulatory in regulatory_obligations:
            if regulatory.status == ObligationStatus.PENDING and regulatory.due_date < overdue_threshold:
                overdue_count += 1
        
        # Count upcoming obligations
        upcoming_threshold = datetime.utcnow() + timedelta(days=self.upcoming_threshold_days)
        upcoming_count = 0
        
        for schedule in payment_schedules:
            if (schedule.status == ObligationStatus.PENDING and 
                datetime.utcnow() < schedule.payment_date <= upcoming_threshold):
                upcoming_count += 1
        
        for obligation in collateral_obligations:
            if (obligation.status == ObligationStatus.PENDING and 
                datetime.utcnow() < obligation.due_date <= upcoming_threshold):
                upcoming_count += 1
        
        for settlement in settlement_obligations:
            if (settlement.status == ObligationStatus.PENDING and 
                datetime.utcnow() < settlement.settlement_date <= upcoming_threshold):
                upcoming_count += 1
        
        for regulatory in regulatory_obligations:
            if (regulatory.status == ObligationStatus.PENDING and 
                datetime.utcnow() < regulatory.due_date <= upcoming_threshold):
                upcoming_count += 1
        
        # Generate risk summary
        risk_summary = self._generate_obligation_risk_summary(
            entity_name, total_payment_obligations, total_collateral_obligations,
            total_settlement_obligations, overdue_count, upcoming_count
        )
        
        return ObligationSummary(
            entity_id=entity_id,
            entity_name=entity_name,
            total_payment_obligations=total_payment_obligations,
            total_collateral_obligations=total_collateral_obligations,
            total_settlement_obligations=total_settlement_obligations,
            overdue_obligations=overdue_count,
            upcoming_obligations=upcoming_count,
            payment_schedules=payment_schedules,
            collateral_obligations=collateral_obligations,
            settlement_obligations=settlement_obligations,
            regulatory_obligations=regulatory_obligations,
            risk_summary=risk_summary
        )
    
    def _create_empty_obligation_summary(self, entity_id: str, entity_name: str) -> ObligationSummary:
        """Create empty obligation summary for entities with no obligations."""
        return ObligationSummary(
            entity_id=entity_id,
            entity_name=entity_name,
            total_payment_obligations=0.0,
            total_collateral_obligations=0.0,
            total_settlement_obligations=0.0,
            overdue_obligations=0,
            upcoming_obligations=0,
            payment_schedules=[],
            collateral_obligations=[],
            settlement_obligations=[],
            regulatory_obligations=[],
            risk_summary=f"{entity_name}: No swap obligations found."
        )
    
    def _generate_obligation_risk_summary(self, entity_name: str, 
                                        total_payment_obligations: float,
                                        total_collateral_obligations: float,
                                        total_settlement_obligations: float,
                                        overdue_count: int,
                                        upcoming_count: int) -> str:
        """Generate risk summary for obligations."""
        
        total_obligations = total_payment_obligations + total_collateral_obligations + total_settlement_obligations
        
        summary = f"Total payment obligations: ${total_payment_obligations:,.0f} over next 12 months. "
        summary += f"Collateral requirements: ${total_collateral_obligations:,.0f} initial, "
        summary += f"${total_settlement_obligations:,.0f} variation. "
        
        if overdue_count > 0:
            summary += f"WARNING: {overdue_count} overdue obligations requiring immediate attention. "
        
        if upcoming_count > 0:
            summary += f"{upcoming_count} obligations due within 30 days."
        
        return summary
    
    def get_obligation_summary_for_entity(self, entity_identifier: str) -> str:
        """
        Get a quick obligation summary for an entity.
        
        Args:
            entity_identifier: Entity identifier
            
        Returns:
            Obligation summary string
        """
        obligation_summary = self.track_entity_obligations(entity_identifier)
        if obligation_summary:
            return obligation_summary.risk_summary
        else:
            return f"Entity {entity_identifier}: No obligation data available"
    
    def update_obligation_status(self, obligation_id: str, new_status: ObligationStatus, 
                               actual_amount: Optional[float] = None,
                               actual_date: Optional[datetime] = None) -> bool:
        """
        Update the status of a specific obligation.
        
        Args:
            obligation_id: ID of the obligation to update
            new_status: New status for the obligation
            actual_amount: Actual amount (if applicable)
            actual_date: Actual completion date (if applicable)
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # This would update the database in a real implementation
            logger.info(f"Updated obligation {obligation_id} to status {new_status.value}")
            
            # Clear cache to force refresh
            self.clear_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating obligation status: {str(e)}")
            return False
    
    def get_upcoming_obligations(self, entity_identifier: str, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming obligations for an entity within specified days.
        
        Args:
            entity_identifier: Entity identifier
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming obligations
        """
        try:
            obligation_summary = self.track_entity_obligations(entity_identifier)
            if not obligation_summary:
                return []
            
            upcoming_obligations = []
            cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            # Check payment schedules
            for schedule in obligation_summary.payment_schedules:
                if (schedule.status == ObligationStatus.PENDING and 
                    datetime.utcnow() < schedule.payment_date <= cutoff_date):
                    upcoming_obligations.append({
                        'type': 'payment',
                        'id': schedule.schedule_id,
                        'amount': schedule.payment_amount,
                        'currency': schedule.currency,
                        'due_date': schedule.payment_date,
                        'description': f"Payment to {schedule.counterparty_id}"
                    })
            
            # Check collateral obligations
            for obligation in obligation_summary.collateral_obligations:
                if (obligation.status == ObligationStatus.PENDING and 
                    datetime.utcnow() < obligation.due_date <= cutoff_date):
                    upcoming_obligations.append({
                        'type': 'collateral',
                        'id': obligation.obligation_id,
                        'amount': obligation.required_amount,
                        'currency': obligation.currency,
                        'due_date': obligation.due_date,
                        'description': f"Collateral posting to {obligation.counterparty_id}"
                    })
            
            # Check regulatory obligations
            for regulatory in obligation_summary.regulatory_obligations:
                if (regulatory.status == ObligationStatus.PENDING and 
                    datetime.utcnow() < regulatory.due_date <= cutoff_date):
                    upcoming_obligations.append({
                        'type': 'regulatory',
                        'id': regulatory.regulatory_id,
                        'amount': 0.0,
                        'currency': 'USD',
                        'due_date': regulatory.due_date,
                        'description': f"{regulatory.regulation_type} reporting: {regulatory.reporting_requirement}"
                    })
            
            # Sort by due date
            upcoming_obligations.sort(key=lambda x: x['due_date'])
            
            return upcoming_obligations
            
        except Exception as e:
            logger.error(f"Error getting upcoming obligations: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear all caches."""
        self.obligation_cache.clear()
        logger.info("Obligation tracking system cache cleared")
