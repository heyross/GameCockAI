#!/usr/bin/env python3
"""
Enhanced Entity Resolution Engine for GameCock AI System.

This module provides comprehensive entity resolution across all data sources
using CIK, CUSIP, ISIN, LEI, ticker symbols, and name matching algorithms.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import json
import re
from difflib import SequenceMatcher
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class IdentifierType(Enum):
    """Types of entity identifiers"""
    CIK = "cik"
    CUSIP = "cusip"
    ISIN = "isin"
    LEI = "lei"
    TICKER = "ticker"
    NAME = "name"
    AUTO = "auto"

class EntityType(Enum):
    """Types of entities"""
    CORPORATION = "corporation"
    FUND = "fund"
    BANK = "bank"
    INSURANCE = "insurance"
    GOVERNMENT = "government"
    UNKNOWN = "unknown"

@dataclass
class EntityIdentifier:
    """Entity identifier information"""
    identifier_type: IdentifierType
    value: str
    confidence: float = 1.0
    source: str = "unknown"

@dataclass
class SecurityInfo:
    """Information about a security"""
    security_id: str
    security_type: str  # equity, bond, derivative, etc.
    cusip: Optional[str] = None
    isin: Optional[str] = None
    security_name: str = ""
    maturity_date: Optional[datetime] = None
    face_value: Optional[float] = None
    currency: str = "USD"

@dataclass
class EntityReference:
    """Reference to a related entity"""
    entity_id: str
    entity_name: str
    relationship_type: str  # parent, subsidiary, counterparty, etc.
    confidence: float = 1.0

@dataclass
class EntityProfile:
    """Comprehensive entity profile"""
    entity_id: str
    primary_identifiers: Dict[str, str] = field(default_factory=dict)
    entity_name: str = ""
    entity_type: EntityType = EntityType.UNKNOWN
    related_securities: List[SecurityInfo] = field(default_factory=list)
    related_entities: List[EntityReference] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EntityMatch:
    """Entity match result"""
    entity_id: str
    confidence_score: float
    match_type: str  # exact, fuzzy, partial
    matched_fields: List[str]
    matched_identifiers: Dict[str, str] = field(default_factory=dict)

class EnhancedEntityResolver:
    """
    Enhanced entity resolution engine that can resolve entities from partial information
    across multiple data sources and identifier types.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the entity resolver."""
        self.db_session = db_session
        self.entity_cache = {}
        self.identifier_patterns = self._init_identifier_patterns()
        self.fuzzy_threshold = 0.8
        self.partial_threshold = 0.6
        
    def _init_identifier_patterns(self) -> Dict[IdentifierType, str]:
        """Initialize regex patterns for different identifier types."""
        return {
            IdentifierType.CIK: r'^(\d{4,10})$',  # CIK should be 4-10 digits
            IdentifierType.CUSIP: r'^([A-Z0-9]{8,9})$',  # CUSIP should be 8-9 characters
            IdentifierType.ISIN: r'^([A-Z]{2}[A-Z0-9]{10})$',
            IdentifierType.LEI: r'^([A-Z0-9]{20})$',
            IdentifierType.TICKER: r'^([A-Z]{1,5})$',
            IdentifierType.NAME: r'^(.+)$'  # Any non-empty string
        }
    
    def resolve_entity(self, identifier: str, identifier_type: IdentifierType = IdentifierType.AUTO) -> Optional[EntityProfile]:
        """
        Resolve entity from partial information.
        
        Args:
            identifier: The identifier value to search for
            identifier_type: Type of identifier (auto-detect if AUTO)
            
        Returns:
            EntityProfile if found, None otherwise
        """
        try:
            # Auto-detect identifier type if needed
            if identifier_type == IdentifierType.AUTO:
                identifier_type = self._detect_identifier_type(identifier)
            
            # Clean and normalize identifier
            clean_identifier = self._clean_identifier(identifier, identifier_type)
            
            # Check cache first
            cache_key = f"{identifier_type.value}:{clean_identifier}"
            if cache_key in self.entity_cache:
                logger.info(f"Entity found in cache: {cache_key}")
                return self.entity_cache[cache_key]
            
            # Search for entity
            entity_profile = self._search_entity(clean_identifier, identifier_type)
            
            if entity_profile:
                # Cache the result
                self.entity_cache[cache_key] = entity_profile
                logger.info(f"Entity resolved: {entity_profile.entity_name} (confidence: {entity_profile.confidence_score})")
            
            return entity_profile
            
        except Exception as e:
            logger.error(f"Error resolving entity {identifier}: {str(e)}")
            return None
    
    def _detect_identifier_type(self, identifier: str) -> IdentifierType:
        """Auto-detect the type of identifier."""
        identifier = identifier.strip().upper()
        
        # Check patterns in order of specificity
        if re.match(self.identifier_patterns[IdentifierType.ISIN], identifier):
            return IdentifierType.ISIN
        elif re.match(self.identifier_patterns[IdentifierType.LEI], identifier):
            return IdentifierType.LEI
        elif re.match(self.identifier_patterns[IdentifierType.CUSIP], identifier):
            return IdentifierType.CUSIP
        elif re.match(self.identifier_patterns[IdentifierType.CIK], identifier):
            return IdentifierType.CIK
        elif re.match(self.identifier_patterns[IdentifierType.TICKER], identifier):
            return IdentifierType.TICKER
        else:
            return IdentifierType.NAME
    
    def _clean_identifier(self, identifier: str, identifier_type: IdentifierType) -> str:
        """Clean and normalize identifier based on type."""
        identifier = identifier.strip()
        
        if identifier_type == IdentifierType.CIK:
            # Pad CIK to 10 digits
            return identifier.zfill(10)
        elif identifier_type == IdentifierType.TICKER:
            # Convert to uppercase
            return identifier.upper()
        elif identifier_type in [IdentifierType.CUSIP, IdentifierType.ISIN, IdentifierType.LEI]:
            # Convert to uppercase
            return identifier.upper()
        else:
            # For names, normalize whitespace
            return ' '.join(identifier.split())
    
    def _search_entity(self, identifier: str, identifier_type: IdentifierType) -> Optional[EntityProfile]:
        """Search for entity using SEC API for company data, database for security identifiers."""
        try:
            # For CUSIP, ISIN, LEI - use database as SEC API doesn't have security identifiers
            if identifier_type in [IdentifierType.CUSIP, IdentifierType.ISIN, IdentifierType.LEI]:
                return self._search_security_identifier(identifier, identifier_type)
            
            # For CIK, NAME, TICKER - use SEC API
            if identifier_type in [IdentifierType.CIK, IdentifierType.NAME, IdentifierType.TICKER]:
                return self._search_company_identifier(identifier, identifier_type)
            
            # For AUTO - try to detect and search accordingly
            if identifier_type == IdentifierType.AUTO:
                detected_type = self._detect_identifier_type(identifier)
                return self._search_entity(identifier, detected_type)
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching entity: {str(e)}")
            return None
    
    def _search_company_identifier(self, identifier: str, identifier_type: IdentifierType) -> Optional[EntityProfile]:
        """Search for company using SEC API with EDGAR fallback."""
        try:
            # Use SEC API for company data
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from company_manager import get_company_map, find_company
            
            company_map = get_company_map()
            if company_map is None:
                logger.error("Could not retrieve company data from SEC API")
                return None
            
            results = find_company(company_map, identifier)
            
            if results:
                # Use the first (best) match
                result = results[0]
                entity_profile = EntityProfile(
                    entity_id=result['cik_str'],
                    entity_name=result.get('title', 'Unknown'),
                    confidence_score=0.95,  # High confidence for SEC API results
                    last_updated=datetime.utcnow()
                )
                
                # Add primary identifiers
                entity_profile.primary_identifiers["cik"] = result['cik_str']
                if result.get('ticker'):
                    entity_profile.primary_identifiers["ticker"] = result['ticker']
                if result.get('title'):
                    entity_profile.primary_identifiers["name"] = result['title']
                
                # Add data sources
                entity_profile.data_sources.append("SEC_API")
                
                return entity_profile
            
            # If not found in SEC API, try EDGAR fallback for CIK searches
            if identifier_type == IdentifierType.CIK:
                return self._search_edgar_fallback(identifier)
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching company via SEC API: {str(e)}")
            return None
    
    def _search_edgar_fallback(self, cik: str) -> Optional[EntityProfile]:
        """Fallback to EDGAR web scraping for CIKs not in SEC API."""
        try:
            import requests
            from config import SEC_USER_AGENT
            
            # Clean CIK format
            clean_cik = cik.zfill(10)
            
            # Try EDGAR company lookup
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={clean_cik}&owner=exclude&count=1"
            headers = {'User-Agent': SEC_USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse the response to extract company name
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for company name in the page
                company_name = None
                title_tag = soup.find('span', class_='companyName')
                if title_tag:
                    company_name = title_tag.get_text(strip=True)
                    # Clean up the company name - remove extra text after CIK
                    if 'CIK#' in company_name:
                        company_name = company_name.split('CIK#')[0].strip()
                    if '(see all company filings)' in company_name:
                        company_name = company_name.replace('(see all company filings)', '').strip()
                
                if company_name:
                    entity_profile = EntityProfile(
                        entity_id=clean_cik,
                        entity_name=company_name,
                        confidence_score=0.8,  # Lower confidence for EDGAR fallback
                        last_updated=datetime.utcnow()
                    )
                    
                    # Add primary identifiers
                    entity_profile.primary_identifiers["cik"] = clean_cik
                    entity_profile.primary_identifiers["name"] = company_name
                    
                    # Add data sources
                    entity_profile.data_sources.append("EDGAR_FALLBACK")
                    
                    logger.info(f"Found company via EDGAR fallback: {company_name} (CIK: {clean_cik})")
                    return entity_profile
            
            return None
            
        except Exception as e:
            logger.error(f"Error in EDGAR fallback search: {str(e)}")
            return None
    
    def _search_security_identifier(self, identifier: str, identifier_type: IdentifierType) -> Optional[EntityProfile]:
        """Search for security using database (CUSIP, ISIN, LEI)."""
        try:
            if not self.db_session:
                logger.error("Database session not available for security identifier search")
                return None
            
            # Search in Form 13F holdings for CUSIP
            if identifier_type == IdentifierType.CUSIP:
                query = text("""
                    SELECT DISTINCT 
                        f.nameofissuer as name,
                        f.cusip,
                        NULL as cik,
                        NULL as ticker
                    FROM form13f_info_tables f
                    WHERE f.cusip = :identifier
                    LIMIT 1
                """)
            # Search in N-MFP portfolio securities for CUSIP, ISIN, LEI
            elif identifier_type in [IdentifierType.ISIN, IdentifierType.LEI]:
                if identifier_type == IdentifierType.ISIN:
                    where_clause = "n.isin = :identifier"
                else:  # LEI
                    where_clause = "n.lei = :identifier"
                
                query = text(f"""
                    SELECT DISTINCT 
                        n.name_of_issuer as name,
                        n.cusip_number as cusip,
                        n.cik,
                        NULL as ticker
                    FROM nmfp_sch_portfolio_securities n
                    WHERE {where_clause}
                    LIMIT 1
                """)
            else:
                return None
            
            result = self.db_session.execute(query, {"identifier": identifier}).fetchone()
            
            if result:
                entity_profile = EntityProfile(
                    entity_id=result.cik or identifier,  # Use CIK if available, otherwise use identifier
                    entity_name=result.name or "Unknown",
                    confidence_score=0.85,  # Good confidence for database results
                    last_updated=datetime.utcnow()
                )
                
                # Add primary identifiers
                if result.cik:
                    entity_profile.primary_identifiers["cik"] = result.cik
                if result.cusip:
                    entity_profile.primary_identifiers["cusip"] = result.cusip
                if result.ticker:
                    entity_profile.primary_identifiers["ticker"] = result.ticker
                if result.name:
                    entity_profile.primary_identifiers["name"] = result.name
                
                # Add the searched identifier
                entity_profile.primary_identifiers[identifier_type.value] = identifier
                
                # Add data sources
                entity_profile.data_sources.append("DATABASE")
                
                return entity_profile
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching security identifier: {str(e)}")
            return None
    
    def _exact_match_search(self, identifier: str, identifier_type: IdentifierType) -> Optional[EntityProfile]:
        """Search for exact matches in database."""
        try:
            if not self.db_session:
                return None
            
            # Build query based on identifier type - use available data sources
            if identifier_type == IdentifierType.CIK:
                query = text("""
                    SELECT DISTINCT cik, entityname as name, NULL as ticker
                    FROM formd_issuers 
                    WHERE cik = :identifier
                    LIMIT 1
                """)
            elif identifier_type == IdentifierType.NAME:
                query = text("""
                    SELECT DISTINCT cik, entityname as name, NULL as ticker
                    FROM formd_issuers 
                    WHERE UPPER(entityname) = UPPER(:identifier)
                    LIMIT 1
                """)
            else:
                # For TICKER, CUSIP, ISIN, LEI - would need additional tables
                return None
            
            result = self.db_session.execute(query, {"identifier": identifier}).fetchone()
            
            if result:
                return self._create_entity_profile_from_result(result, 1.0, "exact")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in exact match search: {str(e)}")
            return None
    
    def _fuzzy_match_search(self, identifier: str, identifier_type: IdentifierType) -> Optional[EntityProfile]:
        """Search for fuzzy matches in database."""
        try:
            if not self.db_session or identifier_type != IdentifierType.NAME:
                return None
            
            # Get all company names for fuzzy matching from available data
            query = text("""
                SELECT DISTINCT cik, entityname as name, NULL as ticker
                FROM formd_issuers 
                WHERE entityname IS NOT NULL
                LIMIT 1000
            """)
            
            results = self.db_session.execute(query).fetchall()
            
            best_match = None
            best_score = 0.0
            
            for result in results:
                if result.name:
                    similarity = SequenceMatcher(None, identifier.lower(), result.name.lower()).ratio()
                    if similarity > best_score and similarity >= self.fuzzy_threshold:
                        best_score = similarity
                        best_match = result
            
            if best_match and best_score >= self.fuzzy_threshold:
                return self._create_entity_profile_from_result(best_match, best_score, "fuzzy")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in fuzzy match search: {str(e)}")
            return None
    
    def _partial_match_search(self, identifier: str, identifier_type: IdentifierType) -> Optional[EntityProfile]:
        """Search for partial matches in database."""
        try:
            if not self.db_session:
                return None
            
            # Build query for partial matching using available data
            if identifier_type == IdentifierType.NAME:
                query = text("""
                    SELECT DISTINCT cik, entityname as name, NULL as ticker
                    FROM formd_issuers 
                    WHERE UPPER(entityname) LIKE UPPER(:identifier)
                    LIMIT 10
                """)
                search_term = f"%{identifier}%"
            else:
                return None
            
            results = self.db_session.execute(query, {"identifier": search_term}).fetchall()
            
            if results:
                # Return the first result with partial confidence
                return self._create_entity_profile_from_result(results[0], self.partial_threshold, "partial")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in partial match search: {str(e)}")
            return None
    
    def _create_entity_profile_from_result(self, result, confidence: float, match_type: str) -> EntityProfile:
        """Create EntityProfile from database result."""
        profile = EntityProfile(
            entity_id=result.cik,
            entity_name=result.name or "Unknown",
            confidence_score=confidence,
            last_updated=datetime.utcnow()
        )
        
        # Add primary identifiers
        if result.cik:
            profile.primary_identifiers["cik"] = result.cik
        if result.ticker:
            profile.primary_identifiers["ticker"] = result.ticker
        if result.name:
            profile.primary_identifiers["name"] = result.name
        
        # Add data sources
        profile.data_sources.append("SEC")
        
        # Determine entity type (simplified)
        if result.name:
            name_lower = result.name.lower()
            if any(word in name_lower for word in ["fund", "trust", "etf"]):
                profile.entity_type = EntityType.FUND
            elif any(word in name_lower for word in ["bank", "financial"]):
                profile.entity_type = EntityType.BANK
            elif any(word in name_lower for word in ["insurance"]):
                profile.entity_type = EntityType.INSURANCE
            else:
                profile.entity_type = EntityType.CORPORATION
        
        return profile
    
    def find_related_entities(self, entity_id: str) -> List[EntityReference]:
        """
        Find all related entities for a given entity.
        
        Args:
            entity_id: The entity ID (typically CIK)
            
        Returns:
            List of related entities
        """
        try:
            related_entities = []
            
            if not self.db_session:
                return related_entities
            
            # Find entities with similar names (potential subsidiaries)
            query = text("""
                SELECT DISTINCT issuercik as cik, issuername as name
                FROM sec_submissions 
                WHERE issuercik != :entity_id
                AND (
                    UPPER(issuername) LIKE UPPER((SELECT issuername FROM sec_submissions WHERE issuercik = :entity_id LIMIT 1))
                    OR UPPER(issuername) LIKE UPPER((SELECT issuername FROM sec_submissions WHERE issuercik = :entity_id LIMIT 1)) || '%'
                )
                LIMIT 20
            """)
            
            results = self.db_session.execute(query, {"entity_id": entity_id}).fetchall()
            
            for result in results:
                if result.cik and result.name:
                    related_entities.append(EntityReference(
                        entity_id=result.cik,
                        entity_name=result.name,
                        relationship_type="potential_subsidiary",
                        confidence=0.7
                    ))
            
            return related_entities
            
        except Exception as e:
            logger.error(f"Error finding related entities: {str(e)}")
            return []
    
    def find_related_securities(self, entity_id: str) -> List[SecurityInfo]:
        """
        Find all related securities for a given entity.
        
        Args:
            entity_id: The entity ID (typically CIK)
            
        Returns:
            List of related securities
        """
        try:
            securities = []
            
            if not self.db_session:
                return securities
            
            # Find securities from Form 13F holdings
            query = text("""
                SELECT DISTINCT cusip, nameofissuer, titleofclass, value
                FROM form13f_info_tables f
                JOIN form13f_submissions s ON f.accession_number = s.accession_number
                WHERE s.cik = :entity_id
                AND cusip IS NOT NULL
                LIMIT 100
            """)
            
            results = self.db_session.execute(query, {"entity_id": entity_id}).fetchall()
            
            for result in results:
                if result.cusip:
                    securities.append(SecurityInfo(
                        security_id=result.cusip,
                        security_type="equity",
                        cusip=result.cusip,
                        security_name=f"{result.nameofissuer} - {result.titleofclass}",
                        face_value=result.value
                    ))
            
            return securities
            
        except Exception as e:
            logger.error(f"Error finding related securities: {str(e)}")
            return []
    
    def get_entity_profile(self, entity_id: str) -> Optional[EntityProfile]:
        """
        Get comprehensive entity profile including related entities and securities.
        
        Args:
            entity_id: The entity ID (typically CIK)
            
        Returns:
            Complete EntityProfile or None
        """
        try:
            # Get base entity profile
            profile = self.resolve_entity(entity_id, IdentifierType.CIK)
            if not profile:
                return None
            
            # Add related entities
            profile.related_entities = self.find_related_entities(entity_id)
            
            # Add related securities
            profile.related_securities = self.find_related_securities(entity_id)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting entity profile: {str(e)}")
            return None
    
    def search_entities(self, search_term: str, limit: int = 10) -> List[EntityMatch]:
        """
        Search for multiple entities matching a search term using SEC API.
        
        Args:
            search_term: The search term
            limit: Maximum number of results
            
        Returns:
            List of entity matches
        """
        try:
            matches = []
            
            # Use SEC API instead of database
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from company_manager import get_company_map, find_company
            
            company_map = get_company_map()
            if company_map is None:
                logger.error("Could not retrieve company data from SEC API")
                return matches
            
            results = find_company(company_map, search_term)
            
            for result in results[:limit]:
                if result.get('cik_str'):
                    match = EntityMatch(
                        entity_id=result['cik_str'],
                        confidence_score=0.9,  # High confidence for SEC API results
                        match_type="api_search",
                        matched_fields=["name", "ticker", "cik"],
                        matched_identifiers={
                            "cik": result['cik_str'],
                            "name": result.get('title', ''),
                            "ticker": result.get('ticker', '')
                        }
                    )
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error searching entities: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear the entity cache."""
        self.entity_cache.clear()
        logger.info("Entity cache cleared")
