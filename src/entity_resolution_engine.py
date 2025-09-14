"""
Entity Resolution Engine

This module provides entity matching and resolution across different data sources
using LEI, CIK, CUSIP, ticker symbols, and name matching algorithms.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
import json
import re
from difflib import SequenceMatcher
from dataclasses import dataclass
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class EntityMatch:
    """Entity match result"""
    entity_id: str
    confidence_score: float
    match_type: str  # exact, fuzzy, partial
    matched_fields: List[str]
    source_entities: List[str]

class EntityResolutionEngine:
    """
    Entity resolution engine for matching entities across data sources
    """
    
    def __init__(self, db_path: str = "gamecock.db"):
        """Initialize the entity resolution engine"""
        self.db_path = db_path
        self.entity_registry: Dict[str, Dict[str, Any]] = {}
        self.match_cache: Dict[str, List[EntityMatch]] = {}
        
        # Initialize database
        self._init_database()
        
        logger.info("Entity Resolution Engine initialized")
    
    def _init_database(self):
        """Initialize database tables for entity resolution"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create entity matches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT,
                    matched_entity_id TEXT,
                    confidence_score REAL,
                    match_type TEXT,
                    matched_fields TEXT,
                    source_entities TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(entity_id, matched_entity_id)
                )
            """)
            
            # Create entity aliases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_aliases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT,
                    alias TEXT,
                    alias_type TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(entity_id, alias, alias_type)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing entity resolution database: {e}")
    
    def register_entity(self, entity_id: str, identifiers: Dict[str, Any]) -> bool:
        """
        Register an entity with its identifiers
        
        Args:
            entity_id: Unique entity identifier
            identifiers: Dictionary of identifiers (LEI, CIK, CUSIP, ticker, name, aliases)
            
        Returns:
            bool: True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store entity in registry
            self.entity_registry[entity_id] = identifiers
            
            # Store aliases
            aliases = identifiers.get('aliases', [])
            for alias in aliases:
                cursor.execute("""
                    INSERT OR REPLACE INTO entity_aliases 
                    (entity_id, alias, alias_type, source)
                    VALUES (?, ?, ?, ?)
                """, (entity_id, alias, 'name_alias', 'manual'))
            
            # Store primary identifiers as aliases
            for field, value in identifiers.items():
                if field != 'aliases' and value:
                    cursor.execute("""
                        INSERT OR REPLACE INTO entity_aliases 
                        (entity_id, alias, alias_type, source)
                        VALUES (?, ?, ?, ?)
                    """, (entity_id, str(value), field, 'primary'))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Registered entity {entity_id} with {len(identifiers)} identifiers")
            return True
            
        except Exception as e:
            logger.error(f"Error registering entity {entity_id}: {e}")
            return False
    
    def find_matches(self, entity_id: str, search_entities: List[Dict[str, Any]]) -> List[EntityMatch]:
        """
        Find matches for an entity in a list of search entities
        
        Args:
            entity_id: Entity to find matches for
            search_entities: List of entities to search in
            
        Returns:
            List of EntityMatch objects
        """
        try:
            if entity_id not in self.entity_registry:
                logger.warning(f"Entity {entity_id} not found in registry")
                return []
            
            target_entity = self.entity_registry[entity_id]
            matches = []
            
            for search_entity in search_entities:
                match = self._calculate_match(target_entity, search_entity)
                if match and match.confidence_score > 0.3:  # Minimum confidence threshold
                    matches.append(match)
            
            # Sort by confidence score
            matches.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Cache results
            self.match_cache[entity_id] = matches
            
            logger.info(f"Found {len(matches)} matches for entity {entity_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Error finding matches for entity {entity_id}: {e}")
            return []
    
    def _calculate_match(self, target_entity: Dict[str, Any], search_entity: Dict[str, Any]) -> Optional[EntityMatch]:
        """
        Calculate match between two entities
        
        Args:
            target_entity: Target entity to match
            search_entity: Entity to match against
            
        Returns:
            EntityMatch object if match found, None otherwise
        """
        try:
            matched_fields = []
            confidence_scores = []
            
            # LEI exact match
            if target_entity.get('lei') and search_entity.get('lei'):
                if target_entity['lei'] == search_entity['lei']:
                    matched_fields.append('lei')
                    confidence_scores.append(1.0)
            
            # CIK exact match
            if target_entity.get('cik') and search_entity.get('cik'):
                if target_entity['cik'] == search_entity['cik']:
                    matched_fields.append('cik')
                    confidence_scores.append(1.0)
            
            # CUSIP exact match
            if target_entity.get('cusip') and search_entity.get('cusip'):
                if target_entity['cusip'] == search_entity['cusip']:
                    matched_fields.append('cusip')
                    confidence_scores.append(1.0)
            
            # Ticker exact match
            if target_entity.get('ticker') and search_entity.get('ticker'):
                if target_entity['ticker'].upper() == search_entity['ticker'].upper():
                    matched_fields.append('ticker')
                    confidence_scores.append(0.9)
            
            # Name fuzzy match
            if target_entity.get('name') and search_entity.get('name'):
                name_similarity = self._calculate_name_similarity(
                    target_entity['name'], 
                    search_entity['name']
                )
                if name_similarity > 0.8:
                    matched_fields.append('name')
                    confidence_scores.append(name_similarity)
            
            # Alias matching
            target_aliases = target_entity.get('aliases', [])
            search_aliases = search_entity.get('aliases', [])
            
            for target_alias in target_aliases:
                for search_alias in search_aliases:
                    alias_similarity = self._calculate_name_similarity(target_alias, search_alias)
                    if alias_similarity > 0.85:
                        matched_fields.append('alias')
                        confidence_scores.append(alias_similarity * 0.8)
            
            if not matched_fields:
                return None
            
            # Calculate overall confidence score
            overall_confidence = np.mean(confidence_scores)
            
            # Determine match type
            if overall_confidence >= 0.95:
                match_type = "exact"
            elif overall_confidence >= 0.8:
                match_type = "fuzzy"
            else:
                match_type = "partial"
            
            return EntityMatch(
                entity_id=search_entity.get('entity_id', 'unknown'),
                confidence_score=overall_confidence,
                match_type=match_type,
                matched_fields=matched_fields,
                source_entities=[target_entity.get('entity_id', 'unknown')]
            )
            
        except Exception as e:
            logger.error(f"Error calculating match: {e}")
            return None
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two entity names
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Normalize names
            name1_norm = self._normalize_name(name1)
            name2_norm = self._normalize_name(name2)
            
            # Calculate sequence similarity
            similarity = SequenceMatcher(None, name1_norm, name2_norm).ratio()
            
            # Boost score for exact matches after normalization
            if name1_norm == name2_norm:
                similarity = 1.0
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating name similarity: {e}")
            return 0.0
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize entity name for comparison
        
        Args:
            name: Entity name
            
        Returns:
            Normalized name
        """
        try:
            # Convert to lowercase
            normalized = name.lower()
            
            # Remove common suffixes
            suffixes = ['inc', 'corp', 'corporation', 'ltd', 'limited', 'llc', 'lp', 'llp']
            for suffix in suffixes:
                normalized = re.sub(rf'\b{suffix}\b', '', normalized)
            
            # Remove punctuation and extra spaces
            normalized = re.sub(r'[^\w\s]', ' ', normalized)
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing name: {e}")
            return name.lower()
    
    def resolve_entity_across_sources(self, entity_id: str, data_sources: List[Dict[str, Any]]) -> Dict[str, List[EntityMatch]]:
        """
        Resolve entity across multiple data sources
        
        Args:
            entity_id: Entity to resolve
            data_sources: List of data source dictionaries
            
        Returns:
            Dictionary mapping data sources to matches
        """
        try:
            resolution_results = {}
            
            for source_name, source_data in data_sources.items():
                if isinstance(source_data, list):
                    matches = self.find_matches(entity_id, source_data)
                    resolution_results[source_name] = matches
                else:
                    logger.warning(f"Invalid data format for source {source_name}")
                    resolution_results[source_name] = []
            
            # Store resolution results
            self._store_resolution_results(entity_id, resolution_results)
            
            logger.info(f"Resolved entity {entity_id} across {len(data_sources)} sources")
            return resolution_results
            
        except Exception as e:
            logger.error(f"Error resolving entity {entity_id}: {e}")
            return {}
    
    def _store_resolution_results(self, entity_id: str, resolution_results: Dict[str, List[EntityMatch]]):
        """Store entity resolution results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for source_name, matches in resolution_results.items():
                for match in matches:
                    cursor.execute("""
                        INSERT OR REPLACE INTO entity_matches 
                        (entity_id, matched_entity_id, confidence_score, match_type, 
                         matched_fields, source_entities)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        entity_id,
                        match.entity_id,
                        match.confidence_score,
                        match.match_type,
                        json.dumps(match.matched_fields),
                        json.dumps(match.source_entities)
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing resolution results: {e}")
    
    def get_entity_relationships(self, entity_id: str) -> Dict[str, Any]:
        """
        Get entity relationships and matches
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Dictionary of entity relationships
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get matches
            matches_query = """
                SELECT matched_entity_id, confidence_score, match_type, matched_fields
                FROM entity_matches 
                WHERE entity_id = ?
                ORDER BY confidence_score DESC
            """
            matches_df = pd.read_sql_query(matches_query, conn, params=(entity_id,))
            
            # Get aliases
            aliases_query = """
                SELECT alias, alias_type, source
                FROM entity_aliases 
                WHERE entity_id = ?
            """
            aliases_df = pd.read_sql_query(aliases_query, conn, params=(entity_id,))
            
            conn.close()
            
            relationships = {
                'entity_id': entity_id,
                'matches': matches_df.to_dict('records') if not matches_df.empty else [],
                'aliases': aliases_df.to_dict('records') if not aliases_df.empty else [],
                'total_matches': len(matches_df),
                'high_confidence_matches': len(matches_df[matches_df['confidence_score'] >= 0.8]) if not matches_df.empty else 0
            }
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error getting entity relationships for {entity_id}: {e}")
            return {}


def create_sample_entity_resolution():
    """Create sample entity resolution for testing"""
    engine = EntityResolutionEngine()
    
    # Register sample entities
    engine.register_entity("ABC_CORP", {
        'lei': 'ABC123456789',
        'cik': '0001234567',
        'ticker': 'ABC',
        'name': 'ABC Corporation',
        'aliases': ['ABC Corp', 'ABC Inc', 'ABC Company']
    })
    
    engine.register_entity("ABC_CORP_ALT", {
        'lei': 'ABC123456789',  # Same LEI
        'cik': '0001234567',    # Same CIK
        'ticker': 'ABC',
        'name': 'ABC Corp',     # Similar name
        'aliases': ['ABC Corporation', 'ABC Inc']
    })
    
    # Test matching
    search_entities = [
        {
            'entity_id': 'ABC_CORP_ALT',
            'lei': 'ABC123456789',
            'cik': '0001234567',
            'ticker': 'ABC',
            'name': 'ABC Corp',
            'aliases': ['ABC Corporation']
        }
    ]
    
    matches = engine.find_matches("ABC_CORP", search_entities)
    
    print(f"Found {len(matches)} matches:")
    for match in matches:
        print(f"- {match.entity_id}: {match.confidence_score:.2f} confidence ({match.match_type})")
        print(f"  Matched fields: {match.matched_fields}")
    
    # Test entity relationships
    relationships = engine.get_entity_relationships("ABC_CORP")
    print(f"\nEntity relationships: {json.dumps(relationships, indent=2)}")
    
    return engine


if __name__ == "__main__":
    # Run sample entity resolution
    engine = create_sample_entity_resolution()
