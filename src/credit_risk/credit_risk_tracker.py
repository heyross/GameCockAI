#!/usr/bin/env python3
"""
Credit Risk & Default Probability Tracker for GameCock AI System.

This module monitors counterparty credit risk and default probabilities.
It provides credit rating monitoring, CDS spread analysis, default probability models,
and credit limit monitoring with early warning systems.

Key Features:
- Credit Rating Monitoring: Track rating changes across all counterparties
- CDS Spread Analysis: Monitor credit default swap spreads for early warning
- Default Probability Models: Calculate probability of default using multiple models
- Credit Limit Monitoring: Track exposure against established credit limits
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
from src.swap_analysis.single_party_risk_analyzer import SinglePartyRiskAnalyzer, SwapExposure, RiskLevel

logger = logging.getLogger(__name__)

class CreditRating(Enum):
    """Credit rating classifications"""
    AAA = "AAA"
    AA_PLUS = "AA+"
    AA = "AA"
    AA_MINUS = "AA-"
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    BBB_PLUS = "BBB+"
    BBB = "BBB"
    BBB_MINUS = "BBB-"
    BB_PLUS = "BB+"
    BB = "BB"
    BB_MINUS = "BB-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    CCC_PLUS = "CCC+"
    CCC = "CCC"
    CCC_MINUS = "CCC-"
    CC = "CC"
    C = "C"
    D = "D"
    NR = "NR"  # Not Rated

class RatingAgency(Enum):
    """Credit rating agencies"""
    S_P = "S&P"
    MOODY = "Moody's"
    FITCH = "Fitch"
    DBRS = "DBRS"
    KROLL = "Kroll"

class CreditEvent(Enum):
    """Types of credit events"""
    RATING_UPGRADE = "rating_upgrade"
    RATING_DOWNGRADE = "rating_downgrade"
    RATING_WATCH_POSITIVE = "rating_watch_positive"
    RATING_WATCH_NEGATIVE = "rating_watch_negative"
    RATING_OUTLOOK_POSITIVE = "rating_outlook_positive"
    RATING_OUTLOOK_NEGATIVE = "rating_outlook_negative"
    RATING_OUTLOOK_STABLE = "rating_outlook_stable"
    DEFAULT = "default"
    BANKRUPTCY = "bankruptcy"
    RESTRUCTURING = "restructuring"

class DefaultModel(Enum):
    """Default probability models"""
    MERTON = "merton"
    KMV = "kmv"
    REDUCED_FORM = "reduced_form"
    STRUCTURAL = "structural"
    MACHINE_LEARNING = "machine_learning"

@dataclass
class CreditRatingHistory:
    """Credit rating history record"""
    rating_id: str
    entity_id: str
    rating_agency: RatingAgency
    rating: CreditRating
    outlook: str  # positive, negative, stable
    watch_status: str  # positive, negative, developing, none
    rating_date: datetime
    effective_date: datetime
    previous_rating: Optional[CreditRating] = None
    rating_change: Optional[str] = None  # upgrade, downgrade, no_change
    confidence: float = 1.0

@dataclass
class CDSSpread:
    """Credit Default Swap spread data"""
    cds_id: str
    entity_id: str
    tenor: int  # years
    spread_bps: float  # basis points
    spread_date: datetime
    data_source: str
    bid_spread: Optional[float] = None
    ask_spread: Optional[float] = None
    mid_spread: Optional[float] = None

@dataclass
class DefaultProbability:
    """Default probability calculation"""
    prob_id: str
    entity_id: str
    model_type: DefaultModel
    probability_1y: float  # 1-year default probability
    probability_5y: float  # 5-year default probability
    calculation_date: datetime
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    model_version: str = "1.0"

@dataclass
class CreditLimit:
    """Credit limit for a counterparty"""
    limit_id: str
    entity_id: str
    counterparty_id: str
    limit_amount: float
    currency: str
    limit_type: str  # total, unsecured, secured
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    utilization: float = 0.0
    available_limit: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CreditEvent:
    """Credit event record"""
    event_id: str
    entity_id: str
    event_type: CreditEvent
    event_date: datetime
    description: str
    impact_score: float  # 0-1 scale
    affected_exposures: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    status: str = "active"  # active, resolved, escalated

@dataclass
class CreditRiskProfile:
    """Comprehensive credit risk profile for an entity"""
    entity_id: str
    entity_name: str
    current_rating: Optional[CreditRating]
    rating_agency: Optional[RatingAgency]
    rating_outlook: str
    watch_status: str
    default_probability_1y: float
    default_probability_5y: float
    cds_spread_5y: Optional[float]
    credit_limits: List[CreditLimit]
    credit_events: List[CreditEvent]
    exposure_utilization: float
    risk_summary: str
    last_updated: datetime = field(default_factory=datetime.utcnow)

class CreditRiskTracker:
    """
    Credit risk and default probability tracker that monitors counterparty
    creditworthiness and provides early warning systems.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the credit risk tracker."""
        self.db_session = db_session
        self.entity_resolver = EnhancedEntityResolver(db_session)
        self.risk_analyzer = SinglePartyRiskAnalyzer(db_session)
        self.credit_cache = {}
        
        # Credit risk parameters
        self.rating_numeric_values = self._init_rating_numeric_values()
        self.default_thresholds = self._init_default_thresholds()
        
    def _init_rating_numeric_values(self) -> Dict[CreditRating, float]:
        """Initialize numeric values for credit ratings."""
        return {
            CreditRating.AAA: 0.0001,
            CreditRating.AA_PLUS: 0.0002,
            CreditRating.AA: 0.0003,
            CreditRating.AA_MINUS: 0.0005,
            CreditRating.A_PLUS: 0.001,
            CreditRating.A: 0.002,
            CreditRating.A_MINUS: 0.003,
            CreditRating.BBB_PLUS: 0.005,
            CreditRating.BBB: 0.01,
            CreditRating.BBB_MINUS: 0.02,
            CreditRating.BB_PLUS: 0.03,
            CreditRating.BB: 0.05,
            CreditRating.BB_MINUS: 0.08,
            CreditRating.B_PLUS: 0.12,
            CreditRating.B: 0.18,
            CreditRating.B_MINUS: 0.25,
            CreditRating.CCC_PLUS: 0.35,
            CreditRating.CCC: 0.45,
            CreditRating.CCC_MINUS: 0.55,
            CreditRating.CC: 0.65,
            CreditRating.C: 0.75,
            CreditRating.D: 1.0,
            CreditRating.NR: 0.1  # Default for not rated
        }
    
    def _init_default_thresholds(self) -> Dict[str, float]:
        """Initialize default probability thresholds."""
        return {
            "low_risk": 0.01,      # 1%
            "medium_risk": 0.05,   # 5%
            "high_risk": 0.15,     # 15%
            "critical_risk": 0.30  # 30%
        }
    
    def track_credit_risk(self, entity_identifier: str, 
                         identifier_type: IdentifierType = IdentifierType.AUTO) -> Optional[CreditRiskProfile]:
        """
        Track credit risk for a specific entity.
        
        Args:
            entity_identifier: Entity identifier
            identifier_type: Type of identifier
            
        Returns:
            CreditRiskProfile with comprehensive credit risk analysis
        """
        try:
            # Resolve entity
            entity_profile = self.entity_resolver.resolve_entity(entity_identifier, identifier_type)
            if not entity_profile:
                logger.warning(f"Entity not found: {entity_identifier}")
                return None
            
            entity_id = entity_profile.entity_id
            entity_name = entity_profile.entity_name
            
            logger.info(f"Tracking credit risk for {entity_name} (ID: {entity_id})")
            
            # Get current credit rating
            current_rating = self._get_current_credit_rating(entity_id)
            
            # Get default probabilities
            default_prob_1y, default_prob_5y = self._calculate_default_probabilities(entity_id, current_rating)
            
            # Get CDS spreads
            cds_spread_5y = self._get_cds_spread(entity_id, 5)
            
            # Get credit limits
            credit_limits = self._get_credit_limits(entity_id)
            
            # Get credit events
            credit_events = self._get_credit_events(entity_id)
            
            # Calculate exposure utilization
            exposure_utilization = self._calculate_exposure_utilization(entity_id, credit_limits)
            
            # Generate risk summary
            risk_summary = self._generate_credit_risk_summary(
                entity_name, current_rating, default_prob_1y, cds_spread_5y, 
                exposure_utilization, credit_events
            )
            
            # Create credit risk profile
            credit_profile = CreditRiskProfile(
                entity_id=entity_id,
                entity_name=entity_name,
                current_rating=current_rating.rating if current_rating else None,
                rating_agency=current_rating.rating_agency if current_rating else None,
                rating_outlook=current_rating.outlook if current_rating else "unknown",
                watch_status=current_rating.watch_status if current_rating else "none",
                default_probability_1y=default_prob_1y,
                default_probability_5y=default_prob_5y,
                cds_spread_5y=cds_spread_5y,
                credit_limits=credit_limits,
                credit_events=credit_events,
                exposure_utilization=exposure_utilization,
                risk_summary=risk_summary
            )
            
            # Cache the result
            self.credit_cache[entity_id] = credit_profile
            
            logger.info(f"Credit risk tracking completed for {entity_name}: "
                       f"Rating: {current_rating.rating.value if current_rating else 'NR'}, "
                       f"1Y PD: {default_prob_1y:.2%}, "
                       f"Utilization: {exposure_utilization:.1%}")
            
            return credit_profile
            
        except Exception as e:
            logger.error(f"Error tracking credit risk for {entity_identifier}: {str(e)}")
            return None
    
    def _get_current_credit_rating(self, entity_id: str) -> Optional[CreditRatingHistory]:
        """Get current credit rating for an entity."""
        try:
            if not self.db_session:
                # Return mock rating for demonstration
                return CreditRatingHistory(
                    rating_id=f"RATING_{entity_id}",
                    entity_id=entity_id,
                    rating_agency=RatingAgency.S_P,
                    rating=CreditRating.BBB,
                    outlook="stable",
                    watch_status="none",
                    rating_date=datetime.utcnow() - timedelta(days=30),
                    effective_date=datetime.utcnow() - timedelta(days=30),
                    previous_rating=CreditRating.BBB_MINUS,
                    rating_change="upgrade"
                )
            
            # In a real implementation, would query credit rating database
            # For now, return a mock rating
            return CreditRatingHistory(
                rating_id=f"RATING_{entity_id}",
                entity_id=entity_id,
                rating_agency=RatingAgency.S_P,
                rating=CreditRating.BBB,
                outlook="stable",
                watch_status="none",
                rating_date=datetime.utcnow() - timedelta(days=30),
                effective_date=datetime.utcnow() - timedelta(days=30)
            )
            
        except Exception as e:
            logger.error(f"Error getting credit rating: {str(e)}")
            return None
    
    def _calculate_default_probabilities(self, entity_id: str, 
                                       current_rating: Optional[CreditRatingHistory]) -> Tuple[float, float]:
        """Calculate default probabilities using multiple models."""
        try:
            # Base probabilities from rating
            if current_rating and current_rating.rating in self.rating_numeric_values:
                base_prob_1y = self.rating_numeric_values[current_rating.rating]
            else:
                base_prob_1y = 0.05  # Default 5% for unrated entities
            
            # Adjust based on outlook and watch status
            outlook_multiplier = 1.0
            if current_rating:
                if current_rating.outlook == "negative":
                    outlook_multiplier = 1.5
                elif current_rating.outlook == "positive":
                    outlook_multiplier = 0.7
                
                if current_rating.watch_status == "negative":
                    outlook_multiplier *= 1.3
                elif current_rating.watch_status == "positive":
                    outlook_multiplier *= 0.8
            
            # Calculate 1-year probability
            prob_1y = min(base_prob_1y * outlook_multiplier, 0.5)  # Cap at 50%
            
            # Calculate 5-year probability (simplified)
            prob_5y = 1 - (1 - prob_1y) ** 5
            
            return prob_1y, prob_5y
            
        except Exception as e:
            logger.error(f"Error calculating default probabilities: {str(e)}")
            return 0.05, 0.20  # Default values
    
    def _get_cds_spread(self, entity_id: str, tenor: int) -> Optional[float]:
        """Get CDS spread for an entity."""
        try:
            # In a real implementation, would query CDS market data
            # For now, return mock data based on rating
            current_rating = self._get_current_credit_rating(entity_id)
            
            if current_rating and current_rating.rating in self.rating_numeric_values:
                base_spread = self.rating_numeric_values[current_rating.rating] * 10000  # Convert to bps
            else:
                base_spread = 500  # Default 500 bps
            
            # Adjust for tenor (simplified)
            if tenor == 5:
                return base_spread
            elif tenor == 1:
                return base_spread * 0.6
            elif tenor == 10:
                return base_spread * 1.2
            else:
                return base_spread
            
        except Exception as e:
            logger.error(f"Error getting CDS spread: {str(e)}")
            return None
    
    def _get_credit_limits(self, entity_id: str) -> List[CreditLimit]:
        """Get credit limits for an entity."""
        credit_limits = []
        
        try:
            # In a real implementation, would query credit limit database
            # For now, create mock limits
            
            # Get swap exposures to determine limits
            risk_profile = self.risk_analyzer.analyze_single_party_risk(entity_id)
            if risk_profile:
                total_exposure = risk_profile.total_notional_exposure
                
                # Create limits based on exposure
                limit = CreditLimit(
                    limit_id=f"LIMIT_{entity_id}",
                    entity_id=entity_id,
                    counterparty_id="ALL",
                    limit_amount=total_exposure * 1.5,  # 150% of current exposure
                    currency="USD",
                    limit_type="total",
                    effective_date=datetime.utcnow() - timedelta(days=365),
                    utilization=total_exposure / (total_exposure * 1.5) if total_exposure > 0 else 0.0,
                    available_limit=(total_exposure * 1.5) - total_exposure if total_exposure > 0 else total_exposure * 1.5
                )
                credit_limits.append(limit)
            
        except Exception as e:
            logger.error(f"Error getting credit limits: {str(e)}")
        
        return credit_limits
    
    def _get_credit_events(self, entity_id: str) -> List[CreditEvent]:
        """Get credit events for an entity."""
        credit_events = []
        
        try:
            # In a real implementation, would query credit event database
            # For now, create mock events based on rating changes
            
            current_rating = self._get_current_credit_rating(entity_id)
            if current_rating and current_rating.rating_change:
                event = CreditEvent(
                    event_id=f"EVENT_{entity_id}_{len(credit_events)}",
                    entity_id=entity_id,
                    event_type=CreditEvent.RATING_UPGRADE if current_rating.rating_change == "upgrade" else CreditEvent.RATING_DOWNGRADE,
                    event_date=current_rating.rating_date,
                    description=f"Credit rating {current_rating.rating_change} from {current_rating.previous_rating.value if current_rating.previous_rating else 'Unknown'} to {current_rating.rating.value}",
                    impact_score=0.3 if current_rating.rating_change == "upgrade" else 0.7,
                    required_actions=["Review credit limits", "Update risk models"] if current_rating.rating_change == "downgrade" else ["Monitor for further changes"]
                )
                credit_events.append(event)
            
        except Exception as e:
            logger.error(f"Error getting credit events: {str(e)}")
        
        return credit_events
    
    def _calculate_exposure_utilization(self, entity_id: str, credit_limits: List[CreditLimit]) -> float:
        """Calculate exposure utilization against credit limits."""
        try:
            if not credit_limits:
                return 0.0
            
            # Get current exposure
            risk_profile = self.risk_analyzer.analyze_single_party_risk(entity_id)
            if not risk_profile:
                return 0.0
            
            total_exposure = risk_profile.total_notional_exposure
            total_limit = sum(limit.limit_amount for limit in credit_limits)
            
            if total_limit > 0:
                return total_exposure / total_limit
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating exposure utilization: {str(e)}")
            return 0.0
    
    def _generate_credit_risk_summary(self, entity_name: str, current_rating: Optional[CreditRatingHistory],
                                    default_prob_1y: float, cds_spread_5y: Optional[float],
                                    exposure_utilization: float, credit_events: List[CreditEvent]) -> str:
        """Generate credit risk summary."""
        
        # Determine risk level
        if default_prob_1y <= self.default_thresholds["low_risk"]:
            risk_level = "Low"
        elif default_prob_1y <= self.default_thresholds["medium_risk"]:
            risk_level = "Medium"
        elif default_prob_1y <= self.default_thresholds["high_risk"]:
            risk_level = "High"
        else:
            risk_level = "Critical"
        
        summary = f"Counterparty {entity_name}: Rating {current_rating.rating.value if current_rating else 'NR'}, "
        summary += f"1Y PD {default_prob_1y:.1%}, CDS spreads {cds_spread_5y:.0f}bps, "
        summary += f"PD increased to {default_prob_1y:.1%}" if default_prob_1y > 0.02 else f"Credit risk {risk_level.lower()}"
        
        if exposure_utilization > 0.8:
            summary += f". WARNING: Credit limit utilization at {exposure_utilization:.1%}"
        
        if credit_events:
            recent_events = [e for e in credit_events if (datetime.utcnow() - e.event_date).days <= 30]
            if recent_events:
                summary += f". Recent credit events: {len(recent_events)} in past 30 days"
        
        return summary
    
    def monitor_credit_events(self, entity_identifier: str) -> List[CreditEvent]:
        """
        Monitor for new credit events for an entity.
        
        Args:
            entity_identifier: Entity identifier
            
        Returns:
            List of new credit events
        """
        try:
            # Resolve entity
            entity_profile = self.entity_resolver.resolve_entity(entity_identifier)
            if not entity_profile:
                return []
            
            entity_id = entity_profile.entity_id
            
            # Get current credit events
            current_events = self._get_credit_events(entity_id)
            
            # Filter for recent events (last 30 days)
            recent_events = [
                event for event in current_events 
                if (datetime.utcnow() - event.event_date).days <= 30
            ]
            
            return recent_events
            
        except Exception as e:
            logger.error(f"Error monitoring credit events: {str(e)}")
            return []
    
    def get_early_warning_signals(self, entity_identifier: str) -> List[Dict[str, Any]]:
        """
        Get early warning signals for credit risk.
        
        Args:
            entity_identifier: Entity identifier
            
        Returns:
            List of early warning signals
        """
        try:
            # Get credit risk profile
            credit_profile = self.track_credit_risk(entity_identifier)
            if not credit_profile:
                return []
            
            warning_signals = []
            
            # Check default probability
            if credit_profile.default_probability_1y > self.default_thresholds["high_risk"]:
                warning_signals.append({
                    'type': 'high_default_probability',
                    'severity': 'high',
                    'description': f"1-year default probability is {credit_profile.default_probability_1y:.1%}",
                    'recommended_action': 'Reduce exposure or increase collateral requirements'
                })
            
            # Check credit limit utilization
            if credit_profile.exposure_utilization > 0.8:
                warning_signals.append({
                    'type': 'high_credit_utilization',
                    'severity': 'medium',
                    'description': f"Credit limit utilization is {credit_profile.exposure_utilization:.1%}",
                    'recommended_action': 'Review and potentially increase credit limits'
                })
            
            # Check CDS spreads
            if credit_profile.cds_spread_5y and credit_profile.cds_spread_5y > 1000:  # 1000 bps
                warning_signals.append({
                    'type': 'wide_cds_spreads',
                    'severity': 'high',
                    'description': f"5-year CDS spreads are {credit_profile.cds_spread_5y:.0f} bps",
                    'recommended_action': 'Monitor market sentiment and consider reducing exposure'
                })
            
            # Check rating outlook
            if credit_profile.rating_outlook == "negative":
                warning_signals.append({
                    'type': 'negative_rating_outlook',
                    'severity': 'medium',
                    'description': "Credit rating outlook is negative",
                    'recommended_action': 'Monitor for potential rating downgrade'
                })
            
            # Check watch status
            if credit_profile.watch_status == "negative":
                warning_signals.append({
                    'type': 'negative_watch_status',
                    'severity': 'high',
                    'description': "Credit rating is on negative watch",
                    'recommended_action': 'Prepare for potential rating downgrade'
                })
            
            return warning_signals
            
        except Exception as e:
            logger.error(f"Error getting early warning signals: {str(e)}")
            return []
    
    def get_credit_risk_summary_for_entity(self, entity_identifier: str) -> str:
        """
        Get a quick credit risk summary for an entity.
        
        Args:
            entity_identifier: Entity identifier
            
        Returns:
            Credit risk summary string
        """
        credit_profile = self.track_credit_risk(entity_identifier)
        if credit_profile:
            return credit_profile.risk_summary
        else:
            return f"Entity {entity_identifier}: No credit risk data available"
    
    def clear_cache(self):
        """Clear all caches."""
        self.credit_cache.clear()
        logger.info("Credit risk tracker cache cleared")
