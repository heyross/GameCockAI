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
        """Search for entity in database and external sources."""
        # Try exact match first
        entity_profile = self._exact_match_search(identifier, identifier_type)
        if entity_profile and entity_profile.confidence_score >= self.fuzzy_threshold:
            return entity_profile
        
        # Try fuzzy match if exact match not found or low confidence
        fuzzy_profile = self._fuzzy_match_search(identifier, identifier_type)
        if fuzzy_profile and fuzzy_profile.confidence_score > entity_profile.confidence_score:
            entity_profile = fuzzy_profile
        
        # Try partial match if still not found
        if not entity_profile or entity_profile.confidence_score < self.partial_threshold:
            partial_profile = self._partial_match_search(identifier, identifier_type)
            if partial_profile and partial_profile.confidence_score > entity_profile.confidence_score:
                entity_profile = partial_profile
        
        return entity_profile
    
    def _exact_match_search(self, identifier: str, identifier_type: IdentifierType) -> Optional[EntityProfile]:
        """Search for exact matches in database."""
        try:
            if not self.db_session:
                return None
            
            # Build query based on identifier type
            if identifier_type == IdentifierType.CIK:
                query = text("""
                    SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                    FROM sec_submissions 
                    WHERE issuercik = :identifier
                    LIMIT 1
                """)
            elif identifier_type == IdentifierType.TICKER:
                query = text("""
                    SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                    FROM sec_submissions 
                    WHERE UPPER(issuertradingsymbol) = UPPER(:identifier)
                    LIMIT 1
                """)
            elif identifier_type == IdentifierType.NAME:
                query = text("""
                    SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                    FROM sec_submissions 
                    WHERE UPPER(issuername) = UPPER(:identifier)
                    LIMIT 1
                """)
            else:
                # For CUSIP, ISIN, LEI - would need additional tables
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
            
            # Get all company names for fuzzy matching
            query = text("""
                SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                FROM sec_submissions 
                WHERE issuername IS NOT NULL
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
            
            # Build query for partial matching
            if identifier_type == IdentifierType.NAME:
                query = text("""
                    SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                    FROM sec_submissions 
                    WHERE UPPER(issuername) LIKE UPPER(:identifier)
                    LIMIT 10
                """)
                search_term = f"%{identifier}%"
            elif identifier_type == IdentifierType.TICKER:
                query = text("""
                    SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                    FROM sec_submissions 
                    WHERE UPPER(issuertradingsymbol) LIKE UPPER(:identifier)
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
        Search for multiple entities matching a search term.
        
        Args:
            search_term: The search term
            limit: Maximum number of results
            
        Returns:
            List of entity matches
        """
        try:
            matches = []
            identifier_type = self._detect_identifier_type(search_term)
            clean_term = self._clean_identifier(search_term, identifier_type)
            
            if not self.db_session:
                return matches
            
            # Build search query
            if identifier_type == IdentifierType.NAME:
                query = text("""
                    SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                    FROM sec_submissions 
                    WHERE UPPER(issuername) LIKE UPPER(:search_term)
                    ORDER BY issuername
                    LIMIT :limit
                """)
                search_param = f"%{clean_term}%"
            elif identifier_type == IdentifierType.TICKER:
                query = text("""
                    SELECT DISTINCT issuercik as cik, issuername as name, issuertradingsymbol as ticker
                    FROM sec_submissions 
                    WHERE UPPER(issuertradingsymbol) LIKE UPPER(:search_term)
                    ORDER BY issuertradingsymbol
                    LIMIT :limit
                """)
                search_param = f"%{clean_term}%"
            else:
                return matches
            
            results = self.db_session.execute(query, {
                "search_term": search_param,
                "limit": limit
            }).fetchall()
            
            for result in results:
                if result.cik:
                    match = EntityMatch(
                        entity_id=result.cik,
                        confidence_score=0.8,  # Default confidence for search results
                        match_type="search",
                        matched_fields=["name", "ticker"],
                        matched_identifiers={
                            "cik": result.cik,
                            "name": result.name or "",
                            "ticker": result.ticker or ""
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
