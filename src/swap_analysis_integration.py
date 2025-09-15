#!/usr/bin/env python3
"""
Swap Analysis Integration Module for GameCock AI System.

This module integrates all the new swap analysis features and provides a unified interface
for comprehensive swap risk analysis. It combines single party risk analysis, cross-filing
correlation, obligation tracking, credit risk monitoring, and executive dashboards.

Key Features:
- Unified Swap Risk Analysis Interface
- Integration with Existing RAG System
- Comprehensive Risk Reporting
- AI-Powered Risk Insights
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from sqlalchemy.orm import Session

# Import all swap analysis modules
from src.swap_analysis.single_party_risk_analyzer import SinglePartyRiskAnalyzer, SinglePartyRiskProfile
from src.cross_filing_analysis.cross_filing_correlation_engine import CrossFilingCorrelationEngine, ConsolidatedRiskProfile
from src.obligation_tracking.obligation_tracking_system import ObligationTrackingSystem, ObligationSummary
from src.credit_risk.credit_risk_tracker import CreditRiskTracker, CreditRiskProfile
from src.dashboards.executive_dashboard import ExecutiveDashboard
from src.enhanced_entity_resolver import EnhancedEntityResolver, IdentifierType

logger = logging.getLogger(__name__)

class SwapAnalysisIntegration:
    """
    Comprehensive swap analysis integration that combines all swap risk analysis
    features into a unified interface.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the swap analysis integration."""
        self.db_session = db_session
        
        # Initialize all analysis modules
        self.entity_resolver = EnhancedEntityResolver(db_session)
        self.risk_analyzer = SinglePartyRiskAnalyzer(db_session)
        self.correlation_engine = CrossFilingCorrelationEngine(db_session)
        self.obligation_tracker = ObligationTrackingSystem(db_session)
        self.credit_tracker = CreditRiskTracker(db_session)
        self.executive_dashboard = ExecutiveDashboard(db_session)
        
        logger.info("Swap Analysis Integration initialized with all modules")
    
    def analyze_comprehensive_swap_risk(self, entity_identifier: str, 
                                      identifier_type: IdentifierType = IdentifierType.AUTO) -> Dict[str, Any]:
        """
        Perform comprehensive swap risk analysis for an entity.
        
        Args:
            entity_identifier: Entity identifier
            identifier_type: Type of identifier
            
        Returns:
            Comprehensive risk analysis results
        """
        try:
            logger.info(f"Starting comprehensive swap risk analysis for {entity_identifier}")
            
            # Resolve entity
            entity_profile = self.entity_resolver.resolve_entity(entity_identifier, identifier_type)
            if not entity_profile:
                return {"error": f"Entity not found: {entity_identifier}"}
            
            entity_id = entity_profile.entity_id
            entity_name = entity_profile.entity_name
            
            # Run all analysis modules
            results = {
                "entity_info": {
                    "entity_id": entity_id,
                    "entity_name": entity_name,
                    "analysis_date": datetime.utcnow().isoformat()
                },
                "single_party_risk": None,
                "cross_filing_correlation": None,
                "obligation_tracking": None,
                "credit_risk": None,
                "executive_dashboard": None,
                "comprehensive_summary": None
            }
            
            # Single Party Risk Analysis
            logger.info("Running single party risk analysis...")
            single_party_risk = self.risk_analyzer.analyze_single_party_risk(entity_id)
            results["single_party_risk"] = self._serialize_risk_profile(single_party_risk)
            
            # Cross-Filing Correlation Analysis
            logger.info("Running cross-filing correlation analysis...")
            cross_filing_correlations = self.correlation_engine.analyze_cross_filing_correlations(entity_id)
            consolidated_risk = self.correlation_engine.get_consolidated_risk_profile(entity_id)
            results["cross_filing_correlation"] = {
                "correlations": [self._serialize_correlation(c) for c in cross_filing_correlations],
                "consolidated_risk": self._serialize_consolidated_risk(consolidated_risk)
            }
            
            # Obligation Tracking
            logger.info("Running obligation tracking...")
            obligation_summary = self.obligation_tracker.track_entity_obligations(entity_id)
            results["obligation_tracking"] = self._serialize_obligation_summary(obligation_summary)
            
            # Credit Risk Analysis
            logger.info("Running credit risk analysis...")
            credit_risk = self.credit_tracker.track_credit_risk(entity_id)
            results["credit_risk"] = self._serialize_credit_risk(credit_risk)
            
            # Executive Dashboard
            logger.info("Generating executive dashboard...")
            dashboard = self.executive_dashboard.generate_executive_dashboard(entity_id)
            results["executive_dashboard"] = self._serialize_dashboard(dashboard)
            
            # Generate comprehensive summary
            results["comprehensive_summary"] = self._generate_comprehensive_summary(
                entity_name, single_party_risk, consolidated_risk, obligation_summary, 
                credit_risk, dashboard
            )
            
            logger.info(f"Comprehensive swap risk analysis completed for {entity_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive swap risk analysis: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def get_quick_risk_summary(self, entity_identifier: str) -> str:
        """
        Get a quick risk summary for an entity.
        
        Args:
            entity_identifier: Entity identifier
            
        Returns:
            Quick risk summary string
        """
        try:
            # Get single party risk summary
            risk_summary = self.risk_analyzer.get_risk_summary_for_entity(entity_identifier)
            
            # Get obligation summary
            obligation_summary = self.obligation_tracker.get_obligation_summary_for_entity(entity_identifier)
            
            # Get credit risk summary
            credit_summary = self.credit_tracker.get_credit_risk_summary_for_entity(entity_identifier)
            
            # Get dashboard summary
            dashboard_summary = self.executive_dashboard.get_dashboard_summary_for_entity(entity_identifier)
            
            # Combine summaries
            combined_summary = f"""
SWAP RISK ANALYSIS SUMMARY FOR {entity_identifier.upper()}

SINGLE PARTY RISK:
{risk_summary}

OBLIGATION TRACKING:
{obligation_summary}

CREDIT RISK:
{credit_summary}

EXECUTIVE DASHBOARD:
{dashboard_summary}

Analysis completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            return combined_summary
            
        except Exception as e:
            logger.error(f"Error getting quick risk summary: {str(e)}")
            return f"Error generating risk summary: {str(e)}"
    
    def _serialize_risk_profile(self, risk_profile: Optional[SinglePartyRiskProfile]) -> Optional[Dict[str, Any]]:
        """Serialize risk profile for JSON output."""
        if not risk_profile:
            return None
        
        return {
            "entity_id": risk_profile.entity_id,
            "entity_name": risk_profile.entity_name,
            "total_notional_exposure": risk_profile.total_notional_exposure,
            "total_mark_to_market": risk_profile.total_mark_to_market,
            "net_collateral_position": risk_profile.net_collateral_position,
            "counterparty_count": risk_profile.counterparty_count,
            "swap_count": risk_profile.swap_count,
            "risk_triggers_count": len(risk_profile.risk_triggers),
            "obligations_count": len(risk_profile.obligations),
            "risk_summary": risk_profile.risk_summary,
            "last_updated": risk_profile.last_updated.isoformat()
        }
    
    def _serialize_correlation(self, correlation) -> Dict[str, Any]:
        """Serialize cross-filing correlation for JSON output."""
        return {
            "correlation_id": correlation.correlation_id,
            "entity_id": correlation.entity_id,
            "correlation_type": correlation.correlation_type,
            "risk_impact": correlation.risk_impact.value if correlation.risk_impact else None,
            "description": correlation.description,
            "recommended_action": correlation.recommended_action,
            "related_filings_count": len(correlation.related_filings),
            "last_analyzed": correlation.last_analyzed.isoformat()
        }
    
    def _serialize_consolidated_risk(self, consolidated_risk: Optional[ConsolidatedRiskProfile]) -> Optional[Dict[str, Any]]:
        """Serialize consolidated risk profile for JSON output."""
        if not consolidated_risk:
            return None
        
        return {
            "primary_entity_id": consolidated_risk.primary_entity_id,
            "primary_entity_name": consolidated_risk.primary_entity_name,
            "total_consolidated_exposure": consolidated_risk.total_consolidated_exposure,
            "related_entities_count": len(consolidated_risk.related_entities),
            "missing_disclosures_count": len(consolidated_risk.missing_disclosures),
            "compliance_issues_count": len(consolidated_risk.compliance_issues),
            "risk_summary": consolidated_risk.risk_summary,
            "last_updated": consolidated_risk.last_updated.isoformat()
        }
    
    def _serialize_obligation_summary(self, obligation_summary: Optional[ObligationSummary]) -> Optional[Dict[str, Any]]:
        """Serialize obligation summary for JSON output."""
        if not obligation_summary:
            return None
        
        return {
            "entity_id": obligation_summary.entity_id,
            "entity_name": obligation_summary.entity_name,
            "total_payment_obligations": obligation_summary.total_payment_obligations,
            "total_collateral_obligations": obligation_summary.total_collateral_obligations,
            "total_settlement_obligations": obligation_summary.total_settlement_obligations,
            "overdue_obligations": obligation_summary.overdue_obligations,
            "upcoming_obligations": obligation_summary.upcoming_obligations,
            "risk_summary": obligation_summary.risk_summary,
            "last_updated": obligation_summary.last_updated.isoformat()
        }
    
    def _serialize_credit_risk(self, credit_risk: Optional[CreditRiskProfile]) -> Optional[Dict[str, Any]]:
        """Serialize credit risk profile for JSON output."""
        if not credit_risk:
            return None
        
        return {
            "entity_id": credit_risk.entity_id,
            "entity_name": credit_risk.entity_name,
            "current_rating": credit_risk.current_rating.value if credit_risk.current_rating else None,
            "rating_agency": credit_risk.rating_agency.value if credit_risk.rating_agency else None,
            "rating_outlook": credit_risk.rating_outlook,
            "watch_status": credit_risk.watch_status,
            "default_probability_1y": credit_risk.default_probability_1y,
            "default_probability_5y": credit_risk.default_probability_5y,
            "cds_spread_5y": credit_risk.cds_spread_5y,
            "exposure_utilization": credit_risk.exposure_utilization,
            "credit_events_count": len(credit_risk.credit_events),
            "risk_summary": credit_risk.risk_summary,
            "last_updated": credit_risk.last_updated.isoformat()
        }
    
    def _serialize_dashboard(self, dashboard: Optional[ExecutiveDashboard]) -> Optional[Dict[str, Any]]:
        """Serialize executive dashboard for JSON output."""
        if not dashboard:
            return None
        
        return {
            "dashboard_id": dashboard.dashboard_id,
            "entity_id": dashboard.entity_id,
            "entity_name": dashboard.entity_name,
            "dashboard_date": dashboard.dashboard_date.isoformat(),
            "risk_metrics_count": len(dashboard.risk_metrics),
            "active_alerts_count": len(dashboard.active_alerts),
            "recommendations_count": len(dashboard.recommendations),
            "key_insights": dashboard.key_insights,
            "compliance_status": dashboard.compliance_status,
            "risk_summary": dashboard.risk_summary,
            "last_updated": dashboard.last_updated.isoformat()
        }
    
    def _generate_comprehensive_summary(self, entity_name: str, single_party_risk, 
                                      consolidated_risk, obligation_summary, 
                                      credit_risk, dashboard) -> str:
        """Generate comprehensive risk summary."""
        
        summary_parts = [f"COMPREHENSIVE SWAP RISK ANALYSIS FOR {entity_name.upper()}"]
        summary_parts.append("=" * 60)
        
        # Single Party Risk Summary
        if single_party_risk:
            summary_parts.append(f"\nSINGLE PARTY RISK:")
            summary_parts.append(f"  Total Exposure: ${single_party_risk.total_notional_exposure:,.0f}")
            summary_parts.append(f"  Counterparties: {single_party_risk.counterparty_count}")
            summary_parts.append(f"  Risk Triggers: {len(single_party_risk.risk_triggers)}")
        
        # Consolidated Risk Summary
        if consolidated_risk:
            summary_parts.append(f"\nCONSOLIDATED RISK (Including Subsidiaries):")
            summary_parts.append(f"  Total Consolidated Exposure: ${consolidated_risk.total_consolidated_exposure:,.0f}")
            summary_parts.append(f"  Related Entities: {len(consolidated_risk.related_entities)}")
            if consolidated_risk.missing_disclosures:
                summary_parts.append(f"  Missing Disclosures: {len(consolidated_risk.missing_disclosures)}")
        
        # Obligation Summary
        if obligation_summary:
            summary_parts.append(f"\nOBLIGATION TRACKING:")
            summary_parts.append(f"  Payment Obligations: ${obligation_summary.total_payment_obligations:,.0f}")
            summary_parts.append(f"  Collateral Obligations: ${obligation_summary.total_collateral_obligations:,.0f}")
            if obligation_summary.overdue_obligations > 0:
                summary_parts.append(f"  OVERDUE OBLIGATIONS: {obligation_summary.overdue_obligations}")
        
        # Credit Risk Summary
        if credit_risk:
            summary_parts.append(f"\nCREDIT RISK:")
            summary_parts.append(f"  Current Rating: {credit_risk.current_rating.value if credit_risk.current_rating else 'NR'}")
            summary_parts.append(f"  1-Year Default Probability: {credit_risk.default_probability_1y:.1%}")
            if credit_risk.cds_spread_5y:
                summary_parts.append(f"  5-Year CDS Spread: {credit_risk.cds_spread_5y:.0f} bps")
        
        # Executive Dashboard Summary
        if dashboard:
            summary_parts.append(f"\nEXECUTIVE DASHBOARD:")
            summary_parts.append(f"  Risk Metrics: {len(dashboard.risk_metrics)}")
            summary_parts.append(f"  Active Alerts: {len(dashboard.active_alerts)}")
            summary_parts.append(f"  Recommendations: {len(dashboard.recommendations)}")
            
            # Add key insights
            if dashboard.key_insights:
                summary_parts.append(f"\nKEY INSIGHTS:")
                for insight in dashboard.key_insights[:3]:  # Top 3 insights
                    summary_parts.append(f"  • {insight}")
        
        summary_parts.append(f"\nAnalysis completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(summary_parts)
    
    def clear_all_caches(self):
        """Clear all module caches."""
        self.risk_analyzer.clear_cache()
        self.correlation_engine.clear_cache()
        self.obligation_tracker.clear_cache()
        self.credit_tracker.clear_cache()
        self.executive_dashboard.clear_cache()
        logger.info("All swap analysis module caches cleared")
