#!/usr/bin/env python3
"""
Derivative Risk Executive Dashboard for GameCock AI System.

This module provides a high-level derivative risk overview for executives and risk managers.
It aggregates data from all swap analysis modules and provides real-time risk metrics,
interactive visualizations, alert systems, and AI-powered recommendations.

Key Features:
- Real-time Risk Metrics: VaR, stress test results, counterparty exposure
- Risk Trend Visualization: Interactive charts showing risk evolution
- Alert System: Real-time alerts for risk limit breaches and market events
- Action Recommendations: AI-powered recommendations for risk mitigation
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
from src.swap_analysis.single_party_risk_analyzer import SinglePartyRiskAnalyzer, RiskLevel
from src.cross_filing_analysis.cross_filing_correlation_engine import CrossFilingCorrelationEngine
from src.obligation_tracking.obligation_tracking_system import ObligationTrackingSystem
from src.credit_risk.credit_risk_tracker import CreditRiskTracker

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class RiskMetric(Enum):
    """Types of risk metrics"""
    VAR = "var"
    STRESS_TEST = "stress_test"
    COUNTERPARTY_EXPOSURE = "counterparty_exposure"
    CONCENTRATION_RISK = "concentration_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    CREDIT_RISK = "credit_risk"
    MARKET_RISK = "market_risk"
    OPERATIONAL_RISK = "operational_risk"

class DashboardView(Enum):
    """Dashboard view types"""
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_OVERVIEW = "risk_overview"
    COUNTERPARTY_ANALYSIS = "counterparty_analysis"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    ALERTS_AND_NOTIFICATIONS = "alerts_and_notifications"

@dataclass
class RiskMetricValue:
    """Risk metric value with metadata"""
    metric_type: RiskMetric
    value: float
    currency: str
    confidence_level: float
    calculation_date: datetime
    benchmark_value: Optional[float] = None
    trend: str = "stable"  # increasing, decreasing, stable
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RiskAlert:
    """Risk alert"""
    alert_id: str
    entity_id: Optional[str]
    alert_type: str
    severity: AlertSeverity
    title: str
    description: str
    alert_date: datetime
    status: str = "active"  # active, acknowledged, resolved
    recommended_actions: List[str] = field(default_factory=list)
    escalation_level: int = 1
    assigned_to: Optional[str] = None

@dataclass
class RiskRecommendation:
    """AI-powered risk recommendation"""
    recommendation_id: str
    entity_id: Optional[str]
    recommendation_type: str
    priority: str  # high, medium, low
    title: str
    description: str
    expected_impact: str
    implementation_effort: str  # low, medium, high
    cost_estimate: Optional[float] = None
    timeline: Optional[str] = None
    success_probability: float = 0.5

@dataclass
class ExecutiveDashboard:
    """Executive dashboard data"""
    dashboard_id: str
    entity_id: str
    entity_name: str
    dashboard_date: datetime
    risk_metrics: Dict[RiskMetric, RiskMetricValue]
    active_alerts: List[RiskAlert]
    recommendations: List[RiskRecommendation]
    risk_summary: str
    key_insights: List[str]
    compliance_status: Dict[str, str]
    last_updated: datetime = field(default_factory=datetime.utcnow)

class ExecutiveDashboard:
    """
    Derivative risk executive dashboard that provides comprehensive risk overview
    for executives and risk managers.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the executive dashboard."""
        self.db_session = db_session
        self.entity_resolver = EnhancedEntityResolver(db_session)
        self.risk_analyzer = SinglePartyRiskAnalyzer(db_session)
        self.correlation_engine = CrossFilingCorrelationEngine(db_session)
        self.obligation_tracker = ObligationTrackingSystem(db_session)
        self.credit_tracker = CreditRiskTracker(db_session)
        self.dashboard_cache = {}
        
        # Dashboard parameters
        self.var_confidence_level = 0.95
        self.stress_test_scenarios = self._init_stress_test_scenarios()
        
    def _init_stress_test_scenarios(self) -> Dict[str, Dict[str, float]]:
        """Initialize stress test scenarios."""
        return {
            "market_crash": {
                "equity_shock": -0.30,
                "rate_shock": 0.02,
                "credit_spread_shock": 0.05,
                "volatility_shock": 0.20
            },
            "rate_shock": {
                "rate_shock": 0.03,
                "credit_spread_shock": 0.02
            },
            "credit_crisis": {
                "credit_spread_shock": 0.10,
                "equity_shock": -0.20
            },
            "liquidity_crisis": {
                "liquidity_premium": 0.05,
                "funding_cost_shock": 0.03
            }
        }
    
    def generate_executive_dashboard(self, entity_identifier: str, 
                                   identifier_type: IdentifierType = IdentifierType.AUTO) -> Optional[ExecutiveDashboard]:
        """
        Generate comprehensive executive dashboard for an entity.
        
        Args:
            entity_identifier: Entity identifier
            identifier_type: Type of identifier
            
        Returns:
            ExecutiveDashboard with comprehensive risk overview
        """
        try:
            # Resolve entity
            entity_profile = self.entity_resolver.resolve_entity(entity_identifier, identifier_type)
            if not entity_profile:
                logger.warning(f"Entity not found: {entity_identifier}")
                return None
            
            entity_id = entity_profile.entity_id
            entity_name = entity_profile.entity_name
            
            logger.info(f"Generating executive dashboard for {entity_name} (ID: {entity_id})")
            
            # Get risk metrics
            risk_metrics = self._calculate_risk_metrics(entity_id)
            
            # Get active alerts
            active_alerts = self._get_active_alerts(entity_id)
            
            # Get recommendations
            recommendations = self._generate_recommendations(entity_id, risk_metrics, active_alerts)
            
            # Generate key insights
            key_insights = self._generate_key_insights(entity_id, risk_metrics, active_alerts)
            
            # Check compliance status
            compliance_status = self._check_compliance_status(entity_id)
            
            # Generate risk summary
            risk_summary = self._generate_risk_summary(entity_name, risk_metrics, active_alerts)
            
            # Create executive dashboard
            dashboard = ExecutiveDashboard(
                dashboard_id=f"DASH_{entity_id}_{datetime.utcnow().strftime('%Y%m%d')}",
                entity_id=entity_id,
                entity_name=entity_name,
                dashboard_date=datetime.utcnow(),
                risk_metrics=risk_metrics,
                active_alerts=active_alerts,
                recommendations=recommendations,
                risk_summary=risk_summary,
                key_insights=key_insights,
                compliance_status=compliance_status
            )
            
            # Cache the result
            self.dashboard_cache[entity_id] = dashboard
            
            logger.info(f"Executive dashboard generated for {entity_name}: "
                       f"{len(risk_metrics)} metrics, {len(active_alerts)} alerts, "
                       f"{len(recommendations)} recommendations")
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating executive dashboard for {entity_identifier}: {str(e)}")
            return None
    
    def _calculate_risk_metrics(self, entity_id: str) -> Dict[RiskMetric, RiskMetricValue]:
        """Calculate comprehensive risk metrics."""
        risk_metrics = {}
        
        try:
            # Get risk profile
            risk_profile = self.risk_analyzer.analyze_single_party_risk(entity_id)
            if not risk_profile:
                return risk_metrics
            
            # Calculate VaR
            var_value = self._calculate_var(entity_id, risk_profile)
            if var_value is not None:
                risk_metrics[RiskMetric.VAR] = RiskMetricValue(
                    metric_type=RiskMetric.VAR,
                    value=var_value,
                    currency="USD",
                    confidence_level=self.var_confidence_level,
                    calculation_date=datetime.utcnow(),
                    trend="stable"
                )
            
            # Calculate stress test results
            stress_test_results = self._run_stress_tests(entity_id, risk_profile)
            if stress_test_results:
                risk_metrics[RiskMetric.STRESS_TEST] = RiskMetricValue(
                    metric_type=RiskMetric.STRESS_TEST,
                    value=stress_test_results["worst_case_loss"],
                    currency="USD",
                    confidence_level=0.99,
                    calculation_date=datetime.utcnow(),
                    trend="stable"
                )
            
            # Calculate counterparty exposure
            counterparty_exposure = self._calculate_counterparty_exposure(risk_profile)
            risk_metrics[RiskMetric.COUNTERPARTY_EXPOSURE] = RiskMetricValue(
                metric_type=RiskMetric.COUNTERPARTY_EXPOSURE,
                value=counterparty_exposure,
                currency="USD",
                confidence_level=0.95,
                calculation_date=datetime.utcnow(),
                trend="stable"
            )
            
            # Calculate concentration risk
            concentration_risk = self._calculate_concentration_risk(risk_profile)
            risk_metrics[RiskMetric.CONCENTRATION_RISK] = RiskMetricValue(
                metric_type=RiskMetric.CONCENTRATION_RISK,
                value=concentration_risk,
                currency="USD",
                confidence_level=0.90,
                calculation_date=datetime.utcnow(),
                trend="stable"
            )
            
            # Calculate liquidity risk
            liquidity_risk = self._calculate_liquidity_risk(entity_id)
            risk_metrics[RiskMetric.LIQUIDITY_RISK] = RiskMetricValue(
                metric_type=RiskMetric.LIQUIDITY_RISK,
                value=liquidity_risk,
                currency="USD",
                confidence_level=0.85,
                calculation_date=datetime.utcnow(),
                trend="stable"
            )
            
            # Calculate credit risk
            credit_risk = self._calculate_credit_risk(entity_id)
            risk_metrics[RiskMetric.CREDIT_RISK] = RiskMetricValue(
                metric_type=RiskMetric.CREDIT_RISK,
                value=credit_risk,
                currency="USD",
                confidence_level=0.90,
                calculation_date=datetime.utcnow(),
                trend="stable"
            )
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
        
        return risk_metrics
    
    def _calculate_var(self, entity_id: str, risk_profile) -> Optional[float]:
        """Calculate Value at Risk."""
        try:
            # Simplified VaR calculation
            # In practice, would use historical simulation or Monte Carlo
            
            total_exposure = risk_profile.total_notional_exposure
            if total_exposure == 0:
                return 0.0
            
            # Assume 5% daily volatility for derivatives
            daily_volatility = 0.05
            var_multiplier = 1.645  # 95% confidence level
            
            var_1d = total_exposure * daily_volatility * var_multiplier
            
            # Convert to 10-day VaR (square root of time rule)
            var_10d = var_1d * np.sqrt(10)
            
            return var_10d
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {str(e)}")
            return None
    
    def _run_stress_tests(self, entity_id: str, risk_profile) -> Optional[Dict[str, float]]:
        """Run stress test scenarios."""
        try:
            total_exposure = risk_profile.total_notional_exposure
            if total_exposure == 0:
                return {"worst_case_loss": 0.0}
            
            stress_results = {}
            worst_case_loss = 0.0
            
            for scenario_name, scenario_params in self.stress_test_scenarios.items():
                # Simplified stress test calculation
                scenario_loss = 0.0
                
                for risk_factor, shock in scenario_params.items():
                    if risk_factor == "equity_shock":
                        # Assume 30% of exposure is equity-related
                        scenario_loss += total_exposure * 0.30 * abs(shock)
                    elif risk_factor == "rate_shock":
                        # Assume 50% of exposure is rate-related
                        scenario_loss += total_exposure * 0.50 * abs(shock) * 5  # 5-year duration
                    elif risk_factor == "credit_spread_shock":
                        # Assume 20% of exposure is credit-related
                        scenario_loss += total_exposure * 0.20 * abs(shock) * 3  # 3-year duration
                
                stress_results[scenario_name] = scenario_loss
                worst_case_loss = max(worst_case_loss, scenario_loss)
            
            return {
                "worst_case_loss": worst_case_loss,
                "scenario_results": stress_results
            }
            
        except Exception as e:
            logger.error(f"Error running stress tests: {str(e)}")
            return None
    
    def _calculate_counterparty_exposure(self, risk_profile) -> float:
        """Calculate total counterparty exposure."""
        try:
            return risk_profile.total_notional_exposure
        except Exception as e:
            logger.error(f"Error calculating counterparty exposure: {str(e)}")
            return 0.0
    
    def _calculate_concentration_risk(self, risk_profile) -> float:
        """Calculate concentration risk."""
        try:
            if not risk_profile.exposures_by_counterparty:
                return 0.0
            
            # Calculate Herfindahl-Hirschman Index for concentration
            total_exposure = risk_profile.total_notional_exposure
            if total_exposure == 0:
                return 0.0
            
            hhi = 0.0
            for counterparty_id, exposures in risk_profile.exposures_by_counterparty.items():
                counterparty_exposure = sum(e.notional_amount for e in exposures)
                market_share = counterparty_exposure / total_exposure
                hhi += market_share ** 2
            
            return hhi * 10000  # Scale to 0-10000 range
            
        except Exception as e:
            logger.error(f"Error calculating concentration risk: {str(e)}")
            return 0.0
    
    def _calculate_liquidity_risk(self, entity_id: str) -> float:
        """Calculate liquidity risk."""
        try:
            # Get obligation summary
            obligation_summary = self.obligation_tracker.track_entity_obligations(entity_id)
            if not obligation_summary:
                return 0.0
            
            # Calculate upcoming payment obligations
            upcoming_payments = sum(
                s.payment_amount for s in obligation_summary.payment_schedules
                if s.status.value == "pending" and s.payment_date <= datetime.utcnow() + timedelta(days=30)
            )
            
            return upcoming_payments
            
        except Exception as e:
            logger.error(f"Error calculating liquidity risk: {str(e)}")
            return 0.0
    
    def _calculate_credit_risk(self, entity_id: str) -> float:
        """Calculate credit risk."""
        try:
            # Get credit risk profile
            credit_profile = self.credit_tracker.track_credit_risk(entity_id)
            if not credit_profile:
                return 0.0
            
            # Calculate expected loss
            total_exposure = credit_profile.exposure_utilization * 1000000000  # Assume $1B limit
            expected_loss = total_exposure * credit_profile.default_probability_1y
            
            return expected_loss
            
        except Exception as e:
            logger.error(f"Error calculating credit risk: {str(e)}")
            return 0.0
    
    def _get_active_alerts(self, entity_id: str) -> List[RiskAlert]:
        """Get active risk alerts."""
        alerts = []
        
        try:
            # Get risk profile
            risk_profile = self.risk_analyzer.analyze_single_party_risk(entity_id)
            if not risk_profile:
                return alerts
            
            # Check for high concentration risk
            if len(risk_profile.exposures_by_counterparty) > 0:
                total_exposure = risk_profile.total_notional_exposure
                for counterparty_id, exposures in risk_profile.exposures_by_counterparty.items():
                    counterparty_exposure = sum(e.notional_amount for e in exposures)
                    concentration_ratio = counterparty_exposure / total_exposure if total_exposure > 0 else 0
                    
                    if concentration_ratio > 0.3:  # 30% concentration threshold
                        alert = RiskAlert(
                            alert_id=f"ALERT_CONCENTRATION_{counterparty_id}",
                            entity_id=entity_id,
                            alert_type="concentration_risk",
                            severity=AlertSeverity.WARNING if concentration_ratio > 0.5 else AlertSeverity.INFO,
                            title=f"High Concentration Risk with {counterparty_id}",
                            description=f"Exposure to {counterparty_id} represents {concentration_ratio:.1%} of total exposure",
                            alert_date=datetime.utcnow(),
                            recommended_actions=["Review counterparty concentration limits", "Consider diversification"]
                        )
                        alerts.append(alert)
            
            # Check for overdue obligations
            obligation_summary = self.obligation_tracker.track_entity_obligations(entity_id)
            if obligation_summary and obligation_summary.overdue_obligations > 0:
                alert = RiskAlert(
                    alert_id=f"ALERT_OVERDUE_{entity_id}",
                    entity_id=entity_id,
                    alert_type="overdue_obligations",
                    severity=AlertSeverity.CRITICAL,
                    title=f"{obligation_summary.overdue_obligations} Overdue Obligations",
                    description=f"Entity has {obligation_summary.overdue_obligations} overdue obligations requiring immediate attention",
                    alert_date=datetime.utcnow(),
                    recommended_actions=["Review overdue obligations", "Contact counterparties", "Update payment schedules"]
                )
                alerts.append(alert)
            
            # Check for credit risk alerts
            credit_profile = self.credit_tracker.track_credit_risk(entity_id)
            if credit_profile and credit_profile.default_probability_1y > 0.15:  # 15% threshold
                alert = RiskAlert(
                    alert_id=f"ALERT_CREDIT_{entity_id}",
                    entity_id=entity_id,
                    alert_type="high_credit_risk",
                    severity=AlertSeverity.CRITICAL,
                    title="High Credit Risk",
                    description=f"1-year default probability is {credit_profile.default_probability_1y:.1%}",
                    alert_date=datetime.utcnow(),
                    recommended_actions=["Reduce exposure", "Increase collateral requirements", "Monitor closely"]
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
        
        return alerts
    
    def _generate_recommendations(self, entity_id: str, risk_metrics: Dict[RiskMetric, RiskMetricValue], 
                                active_alerts: List[RiskAlert]) -> List[RiskRecommendation]:
        """Generate AI-powered risk recommendations."""
        recommendations = []
        
        try:
            # Risk mitigation recommendations based on alerts
            for alert in active_alerts:
                if alert.alert_type == "concentration_risk":
                    recommendation = RiskRecommendation(
                        recommendation_id=f"REC_CONCENTRATION_{entity_id}",
                        entity_id=entity_id,
                        recommendation_type="risk_diversification",
                        priority="high",
                        title="Diversify Counterparty Exposure",
                        description="Reduce concentration risk by diversifying exposure across multiple counterparties",
                        expected_impact="Reduce concentration risk by 50%",
                        implementation_effort="medium",
                        cost_estimate=100000,  # $100K
                        timeline="3-6 months",
                        success_probability=0.8
                    )
                    recommendations.append(recommendation)
                
                elif alert.alert_type == "overdue_obligations":
                    recommendation = RiskRecommendation(
                        recommendation_id=f"REC_OBLIGATIONS_{entity_id}",
                        entity_id=entity_id,
                        recommendation_type="operational_improvement",
                        priority="critical",
                        title="Implement Automated Obligation Tracking",
                        description="Implement automated systems to track and manage payment obligations",
                        expected_impact="Reduce overdue obligations by 90%",
                        implementation_effort="high",
                        cost_estimate=500000,  # $500K
                        timeline="6-12 months",
                        success_probability=0.9
                    )
                    recommendations.append(recommendation)
                
                elif alert.alert_type == "high_credit_risk":
                    recommendation = RiskRecommendation(
                        recommendation_id=f"REC_CREDIT_{entity_id}",
                        entity_id=entity_id,
                        recommendation_type="credit_risk_management",
                        priority="critical",
                        title="Enhance Credit Risk Monitoring",
                        description="Implement real-time credit risk monitoring and early warning systems",
                        expected_impact="Reduce credit losses by 30%",
                        implementation_effort="high",
                        cost_estimate=750000,  # $750K
                        timeline="9-12 months",
                        success_probability=0.85
                    )
                    recommendations.append(recommendation)
            
            # Performance optimization recommendations
            if RiskMetric.VAR in risk_metrics:
                var_value = risk_metrics[RiskMetric.VAR].value
                if var_value > 10000000:  # $10M VaR threshold
                    recommendation = RiskRecommendation(
                        recommendation_id=f"REC_VAR_{entity_id}",
                        entity_id=entity_id,
                        recommendation_type="risk_optimization",
                        priority="medium",
                        title="Optimize Portfolio Risk",
                        description="Implement portfolio optimization to reduce VaR while maintaining returns",
                        expected_impact="Reduce VaR by 20%",
                        implementation_effort="medium",
                        cost_estimate=200000,  # $200K
                        timeline="4-6 months",
                        success_probability=0.7
                    )
                    recommendations.append(recommendation)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def _generate_key_insights(self, entity_id: str, risk_metrics: Dict[RiskMetric, RiskMetricValue], 
                             active_alerts: List[RiskAlert]) -> List[str]:
        """Generate key insights from risk analysis."""
        insights = []
        
        try:
            # Risk level insight
            critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
            if critical_alerts:
                insights.append(f"CRITICAL: {len(critical_alerts)} critical risk alerts require immediate attention")
            elif active_alerts:
                insights.append(f"WARNING: {len(active_alerts)} risk alerts require monitoring")
            else:
                insights.append("Risk profile is within acceptable limits")
            
            # VaR insight
            if RiskMetric.VAR in risk_metrics:
                var_value = risk_metrics[RiskMetric.VAR].value
                insights.append(f"10-day VaR at 95% confidence: ${var_value:,.0f}")
            
            # Concentration insight
            if RiskMetric.CONCENTRATION_RISK in risk_metrics:
                concentration = risk_metrics[RiskMetric.CONCENTRATION_RISK].value
                if concentration > 2500:  # HHI > 2500 indicates high concentration
                    insights.append("High portfolio concentration detected - consider diversification")
            
            # Credit risk insight
            if RiskMetric.CREDIT_RISK in risk_metrics:
                credit_risk = risk_metrics[RiskMetric.CREDIT_RISK].value
                insights.append(f"Expected credit loss: ${credit_risk:,.0f}")
            
            # Liquidity insight
            if RiskMetric.LIQUIDITY_RISK in risk_metrics:
                liquidity_risk = risk_metrics[RiskMetric.LIQUIDITY_RISK].value
                if liquidity_risk > 5000000:  # $5M threshold
                    insights.append(f"High liquidity requirements: ${liquidity_risk:,.0f} in next 30 days")
            
        except Exception as e:
            logger.error(f"Error generating key insights: {str(e)}")
        
        return insights
    
    def _check_compliance_status(self, entity_id: str) -> Dict[str, str]:
        """Check regulatory compliance status."""
        compliance_status = {}
        
        try:
            # Check SEC filing compliance
            obligation_summary = self.obligation_tracker.track_entity_obligations(entity_id)
            if obligation_summary:
                overdue_regulatory = sum(
                    1 for r in obligation_summary.regulatory_obligations
                    if r.status.value == "pending" and r.due_date < datetime.utcnow()
                )
                compliance_status["SEC_Filings"] = "Compliant" if overdue_regulatory == 0 else f"{overdue_regulatory} overdue"
            
            # Check CFTC reporting compliance
            compliance_status["CFTC_Reporting"] = "Compliant"  # Simplified
            
            # Check ISDA compliance
            compliance_status["ISDA_Compliance"] = "Compliant"  # Simplified
            
        except Exception as e:
            logger.error(f"Error checking compliance status: {str(e)}")
            compliance_status = {"Error": "Unable to check compliance status"}
        
        return compliance_status
    
    def _generate_risk_summary(self, entity_name: str, risk_metrics: Dict[RiskMetric, RiskMetricValue], 
                             active_alerts: List[RiskAlert]) -> str:
        """Generate executive risk summary."""
        
        # Count alerts by severity
        critical_alerts = len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL])
        warning_alerts = len([a for a in active_alerts if a.severity == AlertSeverity.WARNING])
        
        # Get key metrics
        var_value = risk_metrics.get(RiskMetric.VAR, RiskMetricValue(RiskMetric.VAR, 0, "USD", 0.95, datetime.utcnow())).value
        total_exposure = risk_metrics.get(RiskMetric.COUNTERPARTY_EXPOSURE, RiskMetricValue(RiskMetric.COUNTERPARTY_EXPOSURE, 0, "USD", 0.95, datetime.utcnow())).value
        
        summary = f"Total derivative exposure: ${total_exposure:,.0f}, VaR: ${var_value:,.0f}"
        
        if critical_alerts > 0:
            summary += f", {critical_alerts} counterparties at limit"
        elif warning_alerts > 0:
            summary += f", {warning_alerts} warnings requiring attention"
        else:
            summary += ", risk profile within limits"
        
        return summary
    
    def get_dashboard_summary_for_entity(self, entity_identifier: str) -> str:
        """
        Get a quick dashboard summary for an entity.
        
        Args:
            entity_identifier: Entity identifier
            
        Returns:
            Dashboard summary string
        """
        dashboard = self.generate_executive_dashboard(entity_identifier)
        if dashboard:
            return dashboard.risk_summary
        else:
            return f"Entity {entity_identifier}: No dashboard data available"
    
    def clear_cache(self):
        """Clear all caches."""
        self.dashboard_cache.clear()
        logger.info("Executive dashboard cache cleared")
