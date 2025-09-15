#!/usr/bin/env python3
"""
Cross-Filing Risk Correlation Engine for GameCock AI System.

This module identifies and correlates swap exposures across multiple SEC filings and data sources.
It provides filing cross-reference analysis, entity relationship mapping, and risk aggregation
across entities to ensure comprehensive derivative disclosure compliance.

Key Features:
- Filing Cross-Reference Analysis: Link derivative disclosures across 10-K, 10-Q, 8-K filings
- Entity Relationship Mapping: Map parent-subsidiary relationships for comprehensive exposure view
- Risk Aggregation Across Entities: Consolidate swap exposures across all related entities
- Regulatory Filing Compliance: Ensure derivative disclosures comply with SEC requirements
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

class FilingType(Enum):
    """Types of SEC filings"""
    FORM_10K = "10-K"
    FORM_10Q = "10-Q"
    FORM_8K = "8-K"
    FORM_13F = "13F"
    FORM_NPORT = "N-PORT"
    FORM_NCEN = "N-CEN"

class DisclosureType(Enum):
    """Types of derivative disclosures"""
    DERIVATIVE_INSTRUMENTS = "derivative_instruments"
    HEDGING_ACTIVITIES = "hedging_activities"
    CREDIT_RISK = "credit_risk"
    MARKET_RISK = "market_risk"
    COLLATERAL_REQUIREMENTS = "collateral_requirements"
    FAIR_VALUE = "fair_value"
    CONCENTRATION_RISK = "concentration_risk"

@dataclass
class FilingReference:
    """Reference to a specific SEC filing"""
    accession_number: str
    filing_type: FilingType
    filing_date: datetime
    period_end_date: datetime
    entity_id: str
    entity_name: str
    form_type: str
    url: Optional[str] = None

@dataclass
class DerivativeDisclosure:
    """Derivative disclosure from a specific filing"""
    disclosure_id: str
    filing_reference: FilingReference
    disclosure_type: DisclosureType
    section: str  # e.g., "Item 7A", "Note 8"
    content: str
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EntityRelationship:
    """Relationship between entities"""
    parent_entity_id: str
    child_entity_id: str
    relationship_type: str  # subsidiary, affiliate, joint_venture, etc.
    ownership_percentage: Optional[float] = None
    effective_date: Optional[datetime] = None
    confidence_score: float = 1.0

@dataclass
class CrossFilingCorrelation:
    """Correlation between derivative disclosures across filings"""
    correlation_id: str
    entity_id: str
    related_filings: List[FilingReference]
    disclosures: List[DerivativeDisclosure]
    correlation_type: str  # consistent, inconsistent, missing, updated
    risk_impact: RiskLevel
    description: str
    recommended_action: str
    last_analyzed: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ConsolidatedRiskProfile:
    """Consolidated risk profile across all related entities"""
    primary_entity_id: str
    primary_entity_name: str
    related_entities: List[EntityRelationship]
    total_consolidated_exposure: float
    individual_entity_exposures: Dict[str, float]
    missing_disclosures: List[str]
    compliance_issues: List[str]
    risk_summary: str
    last_updated: datetime = field(default_factory=datetime.utcnow)

class CrossFilingCorrelationEngine:
    """
    Cross-filing risk correlation engine that identifies and correlates swap exposures
    across multiple SEC filings and data sources.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the cross-filing correlation engine."""
        self.db_session = db_session
        self.entity_resolver = EnhancedEntityResolver(db_session)
        self.risk_analyzer = SinglePartyRiskAnalyzer(db_session)
        self.correlation_cache = {}
        self.relationship_cache = {}
        
        # Disclosure patterns for different filing types
        self.disclosure_patterns = self._init_disclosure_patterns()
        
    def _init_disclosure_patterns(self) -> Dict[FilingType, Dict[DisclosureType, List[str]]]:
        """Initialize patterns for finding derivative disclosures in different filing types."""
        return {
            FilingType.FORM_10K: {
                DisclosureType.DERIVATIVE_INSTRUMENTS: [
                    "derivative instruments", "derivatives", "swaps", "futures", "options"
                ],
                DisclosureType.HEDGING_ACTIVITIES: [
                    "hedging", "hedge", "risk management", "hedge accounting"
                ],
                DisclosureType.CREDIT_RISK: [
                    "credit risk", "counterparty risk", "credit exposure"
                ],
                DisclosureType.MARKET_RISK: [
                    "market risk", "interest rate risk", "currency risk"
                ],
                DisclosureType.FAIR_VALUE: [
                    "fair value", "mark to market", "valuation"
                ]
            },
            FilingType.FORM_10Q: {
                DisclosureType.DERIVATIVE_INSTRUMENTS: [
                    "derivative instruments", "derivatives", "swaps"
                ],
                DisclosureType.HEDGING_ACTIVITIES: [
                    "hedging", "hedge", "risk management"
                ],
                DisclosureType.FAIR_VALUE: [
                    "fair value", "mark to market"
                ]
            },
            FilingType.FORM_8K: {
                DisclosureType.DERIVATIVE_INSTRUMENTS: [
                    "derivative", "swap", "hedge", "risk management"
                ]
            }
        }
    
    def analyze_cross_filing_correlations(self, entity_identifier: str, 
                                        identifier_type: IdentifierType = IdentifierType.AUTO) -> List[CrossFilingCorrelation]:
        """
        Analyze correlations between derivative disclosures across multiple filings.
        
        Args:
            entity_identifier: Entity identifier
            identifier_type: Type of identifier
            
        Returns:
            List of cross-filing correlations
        """
        try:
            # Resolve entity
            entity_profile = self.entity_resolver.resolve_entity(entity_identifier, identifier_type)
            if not entity_profile:
                logger.warning(f"Entity not found: {entity_identifier}")
                return []
            
            entity_id = entity_profile.entity_id
            entity_name = entity_profile.entity_name
            
            logger.info(f"Analyzing cross-filing correlations for {entity_name} (ID: {entity_id})")
            
            # Get all filings for the entity
            filings = self._get_entity_filings(entity_id)
            
            if not filings:
                logger.info(f"No filings found for {entity_name}")
                return []
            
            # Extract derivative disclosures from each filing
            all_disclosures = []
            for filing in filings:
                disclosures = self._extract_derivative_disclosures(filing)
                all_disclosures.extend(disclosures)
            
            # Correlate disclosures across filings
            correlations = self._correlate_disclosures(entity_id, all_disclosures)
            
            logger.info(f"Found {len(correlations)} cross-filing correlations for {entity_name}")
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error analyzing cross-filing correlations for {entity_identifier}: {str(e)}")
            return []
    
    def get_consolidated_risk_profile(self, entity_identifier: str, 
                                    identifier_type: IdentifierType = IdentifierType.AUTO) -> Optional[ConsolidatedRiskProfile]:
        """
        Get consolidated risk profile across all related entities.
        
        Args:
            entity_identifier: Primary entity identifier
            identifier_type: Type of identifier
            
        Returns:
            Consolidated risk profile
        """
        try:
            # Resolve primary entity
            primary_entity = self.entity_resolver.resolve_entity(entity_identifier, identifier_type)
            if not primary_entity:
                logger.warning(f"Primary entity not found: {entity_identifier}")
                return None
            
            primary_entity_id = primary_entity.entity_id
            primary_entity_name = primary_entity.entity_name
            
            logger.info(f"Getting consolidated risk profile for {primary_entity_name}")
            
            # Find related entities
            related_entities = self._find_related_entities(primary_entity_id)
            
            # Get individual risk profiles
            individual_exposures = {}
            total_consolidated_exposure = 0.0
            
            # Primary entity exposure
            primary_risk = self.risk_analyzer.analyze_single_party_risk(primary_entity_id)
            if primary_risk:
                individual_exposures[primary_entity_id] = primary_risk.total_notional_exposure
                total_consolidated_exposure += primary_risk.total_notional_exposure
            
            # Related entity exposures
            for relationship in related_entities:
                related_risk = self.risk_analyzer.analyze_single_party_risk(relationship.child_entity_id)
                if related_risk:
                    individual_exposures[relationship.child_entity_id] = related_risk.total_notional_exposure
                    total_consolidated_exposure += related_risk.total_notional_exposure
            
            # Check for missing disclosures
            missing_disclosures = self._identify_missing_disclosures(primary_entity_id, related_entities)
            
            # Check for compliance issues
            compliance_issues = self._check_compliance_issues(primary_entity_id, related_entities)
            
            # Generate risk summary
            risk_summary = self._generate_consolidated_risk_summary(
                primary_entity_name, total_consolidated_exposure, 
                individual_exposures, len(related_entities), 
                missing_disclosures, compliance_issues
            )
            
            return ConsolidatedRiskProfile(
                primary_entity_id=primary_entity_id,
                primary_entity_name=primary_entity_name,
                related_entities=related_entities,
                total_consolidated_exposure=total_consolidated_exposure,
                individual_entity_exposures=individual_exposures,
                missing_disclosures=missing_disclosures,
                compliance_issues=compliance_issues,
                risk_summary=risk_summary
            )
            
        except Exception as e:
            logger.error(f"Error getting consolidated risk profile for {entity_identifier}: {str(e)}")
            return None
    
    def _get_entity_filings(self, entity_id: str) -> List[FilingReference]:
        """Get all relevant filings for an entity."""
        filings = []
        
        try:
            if not self.db_session:
                return filings
            
            # Get 10-K filings
            query_10k = text("""
                SELECT accession_number, filing_date, period_of_report, company_name, form_type
                FROM sec_10k_submissions
                WHERE cik = :entity_id
                ORDER BY filing_date DESC
                LIMIT 10
            """)
            
            results_10k = self.db_session.execute(query_10k, {"entity_id": entity_id}).fetchall()
            for result in results_10k:
                filing = FilingReference(
                    accession_number=result.accession_number,
                    filing_type=FilingType.FORM_10K,
                    filing_date=result.filing_date,
                    period_end_date=result.period_of_report,
                    entity_id=entity_id,
                    entity_name=result.company_name,
                    form_type=result.form_type
                )
                filings.append(filing)
            
            # Get 10-Q filings
            query_10q = text("""
                SELECT accession_number, filing_date, period_of_report, company_name, form_type
                FROM sec_10k_submissions
                WHERE cik = :entity_id AND form_type IN ('10-Q', '10-Q/A')
                ORDER BY filing_date DESC
                LIMIT 20
            """)
            
            results_10q = self.db_session.execute(query_10q, {"entity_id": entity_id}).fetchall()
            for result in results_10q:
                filing = FilingReference(
                    accession_number=result.accession_number,
                    filing_type=FilingType.FORM_10Q,
                    filing_date=result.filing_date,
                    period_end_date=result.period_of_report,
                    entity_id=entity_id,
                    entity_name=result.company_name,
                    form_type=result.form_type
                )
                filings.append(filing)
            
            # Get 8-K filings
            query_8k = text("""
                SELECT accession_number, filing_date, period_of_report, company_name, form_type
                FROM sec_8k_submissions
                WHERE cik = :entity_id
                ORDER BY filing_date DESC
                LIMIT 20
            """)
            
            results_8k = self.db_session.execute(query_8k, {"entity_id": entity_id}).fetchall()
            for result in results_8k:
                filing = FilingReference(
                    accession_number=result.accession_number,
                    filing_type=FilingType.FORM_8K,
                    filing_date=result.filing_date,
                    period_end_date=result.period_of_report or result.filing_date,
                    entity_id=entity_id,
                    entity_name=result.company_name,
                    form_type=result.form_type
                )
                filings.append(filing)
            
            logger.info(f"Found {len(filings)} filings for entity {entity_id}")
            
        except Exception as e:
            logger.error(f"Error getting entity filings: {str(e)}")
        
        return filings
    
    def _extract_derivative_disclosures(self, filing: FilingReference) -> List[DerivativeDisclosure]:
        """Extract derivative disclosures from a specific filing."""
        disclosures = []
        
        try:
            if not self.db_session:
                return disclosures
            
            # Get document content based on filing type
            if filing.filing_type == FilingType.FORM_10K:
                query = text("""
                    SELECT section, content
                    FROM sec_10k_documents
                    WHERE accession_number = :accession_number
                    AND (content LIKE '%derivative%' OR content LIKE '%swap%' OR content LIKE '%hedge%')
                """)
            elif filing.filing_type == FilingType.FORM_10Q:
                query = text("""
                    SELECT section, content
                    FROM sec_10k_documents
                    WHERE accession_number = :accession_number
                    AND (content LIKE '%derivative%' OR content LIKE '%swap%' OR content LIKE '%hedge%')
                """)
            elif filing.filing_type == FilingType.FORM_8K:
                query = text("""
                    SELECT item_number as section, content
                    FROM sec_8k_items
                    WHERE accession_number = :accession_number
                    AND (content LIKE '%derivative%' OR content LIKE '%swap%' OR content LIKE '%hedge%')
                """)
            else:
                return disclosures
            
            results = self.db_session.execute(query, {"accession_number": filing.accession_number}).fetchall()
            
            for result in results:
                # Determine disclosure type
                disclosure_type = self._classify_disclosure_type(result.content, filing.filing_type)
                
                if disclosure_type:
                    disclosure = DerivativeDisclosure(
                        disclosure_id=f"{filing.accession_number}_{result.section}",
                        filing_reference=filing,
                        disclosure_type=disclosure_type,
                        section=result.section,
                        content=result.content,
                        extracted_data=self._extract_structured_data(result.content),
                        confidence_score=self._calculate_disclosure_confidence(result.content, disclosure_type)
                    )
                    disclosures.append(disclosure)
            
            logger.info(f"Extracted {len(disclosures)} derivative disclosures from {filing.accession_number}")
            
        except Exception as e:
            logger.error(f"Error extracting derivative disclosures: {str(e)}")
        
        return disclosures
    
    def _classify_disclosure_type(self, content: str, filing_type: FilingType) -> Optional[DisclosureType]:
        """Classify the type of derivative disclosure."""
        if not content:
            return None
        
        content_lower = content.lower()
        
        # Get patterns for this filing type
        patterns = self.disclosure_patterns.get(filing_type, {})
        
        # Check each disclosure type
        for disclosure_type, keywords in patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                return disclosure_type
        
        return None
    
    def _extract_structured_data(self, content: str) -> Dict[str, Any]:
        """Extract structured data from disclosure content."""
        extracted_data = {}
        
        if not content:
            return extracted_data
        
        import re
        
        # Extract notional amounts
        notional_patterns = [
            r'notional.*?(\$?[\d,]+\.?\d*)\s*(?:million|billion|thousand)?',
            r'(\$?[\d,]+\.?\d*)\s*(?:million|billion|thousand)?.*?notional'
        ]
        
        for pattern in notional_patterns:
            matches = re.finditer(pattern, content.lower())
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
                    
                    if 'notional_amounts' not in extracted_data:
                        extracted_data['notional_amounts'] = []
                    extracted_data['notional_amounts'].append(amount)
                except ValueError:
                    continue
        
        # Extract fair values
        fair_value_patterns = [
            r'fair value.*?(\$?[\d,]+\.?\d*)\s*(?:million|billion|thousand)?',
            r'(\$?[\d,]+\.?\d*)\s*(?:million|billion|thousand)?.*?fair value'
        ]
        
        for pattern in fair_value_patterns:
            matches = re.finditer(pattern, content.lower())
            for match in matches:
                amount_str = match.group(1).replace(',', '').replace('$', '')
                try:
                    amount = float(amount_str)
                    if 'billion' in match.group(0):
                        amount *= 1_000_000_000
                    elif 'million' in match.group(0):
                        amount *= 1_000_000
                    elif 'thousand' in match.group(0):
                        amount *= 1_000
                    
                    if 'fair_values' not in extracted_data:
                        extracted_data['fair_values'] = []
                    extracted_data['fair_values'].append(amount)
                except ValueError:
                    continue
        
        return extracted_data
    
    def _calculate_disclosure_confidence(self, content: str, disclosure_type: DisclosureType) -> float:
        """Calculate confidence score for a disclosure."""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        confidence = 0.0
        
        # Base confidence based on disclosure type
        base_confidence = {
            DisclosureType.DERIVATIVE_INSTRUMENTS: 0.8,
            DisclosureType.HEDGING_ACTIVITIES: 0.7,
            DisclosureType.CREDIT_RISK: 0.6,
            DisclosureType.MARKET_RISK: 0.6,
            DisclosureType.FAIR_VALUE: 0.9,
            DisclosureType.COLLATERAL_REQUIREMENTS: 0.5,
            DisclosureType.CONCENTRATION_RISK: 0.5
        }
        
        confidence = base_confidence.get(disclosure_type, 0.5)
        
        # Adjust based on content quality
        if any(term in content_lower for term in ['notional', 'fair value', 'mark to market']):
            confidence += 0.1
        
        if any(term in content_lower for term in ['million', 'billion', 'thousand']):
            confidence += 0.1
        
        if len(content) > 500:  # Longer content suggests more detail
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _correlate_disclosures(self, entity_id: str, disclosures: List[DerivativeDisclosure]) -> List[CrossFilingCorrelation]:
        """Correlate disclosures across different filings."""
        correlations = []
        
        # Group disclosures by type
        disclosures_by_type = {}
        for disclosure in disclosures:
            if disclosure.disclosure_type not in disclosures_by_type:
                disclosures_by_type[disclosure.disclosure_type] = []
            disclosures_by_type[disclosure.disclosure_type].append(disclosure)
        
        # Analyze correlations for each disclosure type
        for disclosure_type, type_disclosures in disclosures_by_type.items():
            if len(type_disclosures) > 1:
                correlation = self._analyze_disclosure_consistency(entity_id, disclosure_type, type_disclosures)
                if correlation:
                    correlations.append(correlation)
        
        return correlations
    
    def _analyze_disclosure_consistency(self, entity_id: str, disclosure_type: DisclosureType, 
                                      disclosures: List[DerivativeDisclosure]) -> Optional[CrossFilingCorrelation]:
        """Analyze consistency of disclosures across filings."""
        if len(disclosures) < 2:
            return None
        
        # Sort by filing date
        disclosures.sort(key=lambda x: x.filing_reference.filing_date)
        
        # Compare extracted data
        inconsistencies = []
        consistent_data = True
        
        # Check for notional amount consistency
        notional_amounts = []
        for disclosure in disclosures:
            if 'notional_amounts' in disclosure.extracted_data:
                notional_amounts.extend(disclosure.extracted_data['notional_amounts'])
        
        if notional_amounts:
            # Check for significant changes
            if len(set(notional_amounts)) > 1:
                max_amount = max(notional_amounts)
                min_amount = min(notional_amounts)
                if max_amount > 0 and (max_amount - min_amount) / max_amount > 0.2:  # 20% change threshold
                    consistent_data = False
                    inconsistencies.append(f"Notional amounts vary significantly: ${min_amount:,.0f} to ${max_amount:,.0f}")
        
        # Determine correlation type and risk impact
        if consistent_data:
            correlation_type = "consistent"
            risk_impact = RiskLevel.LOW
            description = f"Consistent {disclosure_type.value} disclosures across {len(disclosures)} filings"
            recommended_action = "No action required"
        else:
            correlation_type = "inconsistent"
            risk_impact = RiskLevel.MEDIUM
            description = f"Inconsistent {disclosure_type.value} disclosures: {'; '.join(inconsistencies)}"
            recommended_action = "Review and reconcile derivative disclosures"
        
        return CrossFilingCorrelation(
            correlation_id=f"{entity_id}_{disclosure_type.value}_{len(correlations)}",
            entity_id=entity_id,
            related_filings=[d.filing_reference for d in disclosures],
            disclosures=disclosures,
            correlation_type=correlation_type,
            risk_impact=risk_impact,
            description=description,
            recommended_action=recommended_action
        )
    
    def _find_related_entities(self, entity_id: str) -> List[EntityRelationship]:
        """Find related entities (subsidiaries, affiliates, etc.)."""
        relationships = []
        
        try:
            if not self.db_session:
                return relationships
            
            # Use enhanced entity resolver to find related entities
            entity_profile = self.entity_resolver.get_entity_profile(entity_id)
            if entity_profile and entity_profile.related_entities:
                for related_entity in entity_profile.related_entities:
                    relationship = EntityRelationship(
                        parent_entity_id=entity_id,
                        child_entity_id=related_entity.entity_id,
                        relationship_type=related_entity.relationship_type,
                        confidence_score=related_entity.confidence
                    )
                    relationships.append(relationship)
            
            logger.info(f"Found {len(relationships)} related entities for {entity_id}")
            
        except Exception as e:
            logger.error(f"Error finding related entities: {str(e)}")
        
        return relationships
    
    def _identify_missing_disclosures(self, primary_entity_id: str, 
                                    related_entities: List[EntityRelationship]) -> List[str]:
        """Identify missing derivative disclosures."""
        missing_disclosures = []
        
        # This is a simplified implementation
        # In practice, would need to check specific SEC requirements
        
        # Check if primary entity has derivative disclosures
        primary_filings = self._get_entity_filings(primary_entity_id)
        primary_has_derivatives = False
        
        for filing in primary_filings:
            disclosures = self._extract_derivative_disclosures(filing)
            if disclosures:
                primary_has_derivatives = True
                break
        
        if not primary_has_derivatives:
            missing_disclosures.append(f"Primary entity {primary_entity_id} missing derivative disclosures")
        
        # Check related entities
        for relationship in related_entities:
            related_filings = self._get_entity_filings(relationship.child_entity_id)
            related_has_derivatives = False
            
            for filing in related_filings:
                disclosures = self._extract_derivative_disclosures(filing)
                if disclosures:
                    related_has_derivatives = True
                    break
            
            if not related_has_derivatives:
                missing_disclosures.append(f"Related entity {relationship.child_entity_id} missing derivative disclosures")
        
        return missing_disclosures
    
    def _check_compliance_issues(self, primary_entity_id: str, 
                               related_entities: List[EntityRelationship]) -> List[str]:
        """Check for regulatory compliance issues."""
        compliance_issues = []
        
        # This is a simplified implementation
        # In practice, would need to check specific SEC requirements and regulations
        
        # Check for timely filing
        primary_filings = self._get_entity_filings(primary_entity_id)
        if primary_filings:
            latest_filing = max(primary_filings, key=lambda x: x.filing_date)
            days_since_filing = (datetime.utcnow() - latest_filing.filing_date).days
            
            if days_since_filing > 90:  # 90-day threshold
                compliance_issues.append(f"Primary entity {primary_entity_id} has not filed in {days_since_filing} days")
        
        return compliance_issues
    
    def _generate_consolidated_risk_summary(self, primary_entity_name: str, 
                                          total_consolidated_exposure: float,
                                          individual_exposures: Dict[str, float],
                                          related_entity_count: int,
                                          missing_disclosures: List[str],
                                          compliance_issues: List[str]) -> str:
        """Generate consolidated risk summary."""
        
        # Calculate individual vs consolidated exposure
        primary_exposure = individual_exposures.get(primary_entity_name, 0.0)
        consolidated_vs_individual = total_consolidated_exposure - primary_exposure
        
        summary = f"{primary_entity_name} and subsidiaries: Combined swap exposure ${total_consolidated_exposure:,.0f} "
        summary += f"(vs. ${primary_exposure:,.0f} reported individually). "
        
        if consolidated_vs_individual > 0:
            summary += f"Additional ${consolidated_vs_individual:,.0f} exposure from {related_entity_count} subsidiaries. "
        
        if missing_disclosures:
            summary += f"Missing disclosures in {len(missing_disclosures)} entities. "
        
        if compliance_issues:
            summary += f"Compliance issues: {len(compliance_issues)} items requiring attention."
        
        return summary
    
    def clear_cache(self):
        """Clear all caches."""
        self.correlation_cache.clear()
        self.relationship_cache.clear()
        logger.info("Cross-filing correlation engine cache cleared")
