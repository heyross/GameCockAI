#!/usr/bin/env python3
"""
Enhanced Entity Tools for GameCock AI System.

This module provides AI agent tools for entity resolution and relationship mapping.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .enhanced_entity_resolver import (
    EnhancedEntityResolver, EntityProfile, EntityMatch, 
    IdentifierType, EntityType
)
from database import SessionLocal

logger = logging.getLogger(__name__)

# Global entity resolver instance
_entity_resolver = None

def get_entity_resolver() -> EnhancedEntityResolver:
    """Get or create the global entity resolver instance."""
    global _entity_resolver
    if _entity_resolver is None:
        db_session = SessionLocal()
        _entity_resolver = EnhancedEntityResolver(db_session)
    return _entity_resolver

def handle_entity_tool_errors(func):
    """Decorator to handle errors in entity tools."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return json.dumps({
                "error": f"Entity operation failed: {str(e)}",
                "suggestion": "Please check your input and try again"
            })
    return wrapper

@handle_entity_tool_errors
def resolve_entity_by_identifier(identifier: str, identifier_type: str = "auto") -> str:
    """
    Resolve an entity by any identifier (CIK, CUSIP, ISIN, LEI, ticker, or name).
    
    Args:
        identifier: The identifier to search for
        identifier_type: Type of identifier (auto, cik, cusip, isin, lei, ticker, name)
        
    Returns:
        JSON string with entity profile information
    """
    try:
        resolver = get_entity_resolver()
        
        # Convert string to enum
        if identifier_type == "auto":
            id_type = IdentifierType.AUTO
        else:
            id_type = IdentifierType(identifier_type.lower())
        
        # Resolve entity
        entity_profile = resolver.resolve_entity(identifier, id_type)
        
        if not entity_profile:
            return json.dumps({
                "message": "No entity found",
                "search_term": identifier,
                "identifier_type": identifier_type,
                "suggestion": "Try a different identifier or check spelling"
            })
        
        # Convert to JSON-serializable format
        result = {
            "entity_id": entity_profile.entity_id,
            "entity_name": entity_profile.entity_name,
            "entity_type": entity_profile.entity_type.value,
            "primary_identifiers": entity_profile.primary_identifiers,
            "confidence_score": entity_profile.confidence_score,
            "data_sources": entity_profile.data_sources,
            "last_updated": entity_profile.last_updated.isoformat(),
            "related_securities_count": len(entity_profile.related_securities),
            "related_entities_count": len(entity_profile.related_entities)
        }
        
        return json.dumps({
            "entity_profile": result,
            "search_term": identifier,
            "identifier_type": identifier_type
        })
        
    except Exception as e:
        logger.error(f"Error resolving entity: {str(e)}")
        return json.dumps({
            "error": "Entity resolution failed",
            "suggestion": "Please check your input and try again"
        })

@handle_entity_tool_errors
def get_comprehensive_entity_profile(entity_id: str) -> str:
    """
    Get a comprehensive entity profile including related entities and securities.
    
    Args:
        entity_id: The entity ID (typically CIK)
        
    Returns:
        JSON string with comprehensive entity information
    """
    try:
        resolver = get_entity_resolver()
        
        # Get comprehensive profile
        profile = resolver.get_entity_profile(entity_id)
        
        if not profile:
            return json.dumps({
                "message": "Entity not found",
                "entity_id": entity_id,
                "suggestion": "Please check the entity ID"
            })
        
        # Convert related entities to JSON-serializable format
        related_entities = []
        for entity in profile.related_entities:
            related_entities.append({
                "entity_id": entity.entity_id,
                "entity_name": entity.entity_name,
                "relationship_type": entity.relationship_type,
                "confidence": entity.confidence
            })
        
        # Convert related securities to JSON-serializable format
        related_securities = []
        for security in profile.related_securities:
            related_securities.append({
                "security_id": security.security_id,
                "security_type": security.security_type,
                "cusip": security.cusip,
                "isin": security.isin,
                "security_name": security.security_name,
                "maturity_date": security.maturity_date.isoformat() if security.maturity_date else None,
                "face_value": security.face_value,
                "currency": security.currency
            })
        
        result = {
            "entity_id": profile.entity_id,
            "entity_name": profile.entity_name,
            "entity_type": profile.entity_type.value,
            "primary_identifiers": profile.primary_identifiers,
            "confidence_score": profile.confidence_score,
            "data_sources": profile.data_sources,
            "last_updated": profile.last_updated.isoformat(),
            "related_entities": related_entities,
            "related_securities": related_securities
        }
        
        return json.dumps({
            "comprehensive_profile": result,
            "entity_id": entity_id
        })
        
    except Exception as e:
        logger.error(f"Error getting comprehensive profile: {str(e)}")
        return json.dumps({
            "error": "Failed to get entity profile",
            "suggestion": "Please check the entity ID and try again"
        })

@handle_entity_tool_errors
def search_entities_by_name(search_term: str, limit: int = 10) -> str:
    """
    Search for entities by name or ticker symbol.
    
    Args:
        search_term: The search term (name or ticker)
        limit: Maximum number of results (default 10)
        
    Returns:
        JSON string with search results
    """
    try:
        resolver = get_entity_resolver()
        
        # Search for entities
        matches = resolver.search_entities(search_term, limit)
        
        if not matches:
            return json.dumps({
                "message": "No entities found",
                "search_term": search_term,
                "suggestion": "Try a different search term or check spelling"
            })
        
        # Convert matches to JSON-serializable format
        results = []
        for match in matches:
            results.append({
                "entity_id": match.entity_id,
                "confidence_score": match.confidence_score,
                "match_type": match.match_type,
                "matched_fields": match.matched_fields,
                "matched_identifiers": match.matched_identifiers
            })
        
        return json.dumps({
            "search_results": results,
            "count": len(results),
            "search_term": search_term,
            "limit": limit
        })
        
    except Exception as e:
        logger.error(f"Error searching entities: {str(e)}")
        return json.dumps({
            "error": "Entity search failed",
            "suggestion": "Please check your search term and try again"
        })

@handle_entity_tool_errors
def find_related_entities(entity_id: str) -> str:
    """
    Find entities related to a given entity.
    
    Args:
        entity_id: The entity ID (typically CIK)
        
    Returns:
        JSON string with related entities
    """
    try:
        resolver = get_entity_resolver()
        
        # Find related entities
        related_entities = resolver.find_related_entities(entity_id)
        
        if not related_entities:
            return json.dumps({
                "message": "No related entities found",
                "entity_id": entity_id,
                "suggestion": "This entity may not have related entities in the database"
            })
        
        # Convert to JSON-serializable format
        results = []
        for entity in related_entities:
            results.append({
                "entity_id": entity.entity_id,
                "entity_name": entity.entity_name,
                "relationship_type": entity.relationship_type,
                "confidence": entity.confidence
            })
        
        return json.dumps({
            "related_entities": results,
            "count": len(results),
            "entity_id": entity_id
        })
        
    except Exception as e:
        logger.error(f"Error finding related entities: {str(e)}")
        return json.dumps({
            "error": "Failed to find related entities",
            "suggestion": "Please check the entity ID and try again"
        })

@handle_entity_tool_errors
def find_related_securities(entity_id: str) -> str:
    """
    Find securities related to a given entity.
    
    Args:
        entity_id: The entity ID (typically CIK)
        
    Returns:
        JSON string with related securities
    """
    try:
        resolver = get_entity_resolver()
        
        # Find related securities
        related_securities = resolver.find_related_securities(entity_id)
        
        if not related_securities:
            return json.dumps({
                "message": "No related securities found",
                "entity_id": entity_id,
                "suggestion": "This entity may not have securities in the database"
            })
        
        # Convert to JSON-serializable format
        results = []
        for security in related_securities:
            results.append({
                "security_id": security.security_id,
                "security_type": security.security_type,
                "cusip": security.cusip,
                "isin": security.isin,
                "security_name": security.security_name,
                "maturity_date": security.maturity_date.isoformat() if security.maturity_date else None,
                "face_value": security.face_value,
                "currency": security.currency
            })
        
        return json.dumps({
            "related_securities": results,
            "count": len(results),
            "entity_id": entity_id
        })
        
    except Exception as e:
        logger.error(f"Error finding related securities: {str(e)}")
        return json.dumps({
            "error": "Failed to find related securities",
            "suggestion": "Please check the entity ID and try again"
        })

@handle_entity_tool_errors
def resolve_entity_for_ai_query(query: str) -> str:
    """
    Resolve entity from natural language query for AI agent.
    
    Args:
        query: Natural language query (e.g., "Find Apple's bonds", "Show me swaps for CIK 1234567")
        
    Returns:
        JSON string with resolved entity and suggested actions
    """
    try:
        resolver = get_entity_resolver()
        
        # Extract potential identifiers from query
        identifiers = _extract_identifiers_from_query(query)
        
        if not identifiers:
            return json.dumps({
                "message": "No entity identifiers found in query",
                "query": query,
                "suggestion": "Please include a company name, ticker, or CIK in your query"
            })
        
        # Try to resolve each identifier
        resolved_entities = []
        for identifier, id_type in identifiers:
            entity_profile = resolver.resolve_entity(identifier, id_type)
            if entity_profile:
                resolved_entities.append({
                    "identifier": identifier,
                    "identifier_type": id_type.value,
                    "entity_profile": {
                        "entity_id": entity_profile.entity_id,
                        "entity_name": entity_profile.entity_name,
                        "confidence_score": entity_profile.confidence_score
                    }
                })
        
        if not resolved_entities:
            return json.dumps({
                "message": "Could not resolve any entities from query",
                "query": query,
                "suggested_identifiers": [{"identifier": id, "type": t.value} for id, t in identifiers],
                "suggestion": "Please check the entity identifiers in your query"
            })
        
        # Determine suggested actions based on query
        suggested_actions = _suggest_actions_from_query(query, resolved_entities)
        
        return json.dumps({
            "resolved_entities": resolved_entities,
            "suggested_actions": suggested_actions,
            "query": query
        })
        
    except Exception as e:
        logger.error(f"Error resolving entity for AI query: {str(e)}")
        return json.dumps({
            "error": "Failed to resolve entity from query",
            "suggestion": "Please rephrase your query with clear entity identifiers"
        })

def _extract_identifiers_from_query(query: str) -> List[tuple]:
    """Extract potential identifiers from a natural language query."""
    import re
    
    identifiers = []
    query_lower = query.lower()
    
    # Look for CIK patterns - more specific pattern
    cik_pattern = r'\b(\d{4,10})\b'
    cik_matches = re.findall(cik_pattern, query)
    for match in cik_matches:
        if len(match) >= 4:  # CIK should be at least 4 digits
            # Check if it's preceded by "CIK" to be more specific
            cik_context = re.search(rf'\bcik\s+{re.escape(match)}\b', query_lower)
            if cik_context or len(match) >= 6:  # Longer numbers are more likely to be CIKs
                identifiers.append((match, IdentifierType.CIK))
    
    # Look for ticker patterns (3-5 uppercase letters) - but exclude common words
    ticker_pattern = r'\b([A-Z]{3,5})\b'
    ticker_matches = re.findall(ticker_pattern, query.upper())
    common_words = {"THE", "AND", "FOR", "SHOW", "ME", "FIND", "GET", "ALL", "ANY", "NEW", "OLD", "BIG", "SMALL"}
    for match in ticker_matches:
        if match not in common_words:
            identifiers.append((match, IdentifierType.TICKER))
    
    # Look for company names (common patterns)
    company_names = ["apple", "microsoft", "google", "amazon", "tesla", "meta", "nvidia"]
    for name in company_names:
        if name in query_lower:
            identifiers.append((name.title(), IdentifierType.NAME))
    
    return identifiers

def _suggest_actions_from_query(query: str, resolved_entities: List[Dict]) -> List[str]:
    """Suggest actions based on the query and resolved entities."""
    suggestions = []
    query_lower = query.lower()
    
    # Suggest actions based on query content
    if any(word in query_lower for word in ["bond", "bonds", "debt"]):
        suggestions.append("find_related_securities")
    
    if any(word in query_lower for word in ["swap", "swaps", "derivative", "derivatives"]):
        suggestions.append("find_swap_exposures")
    
    if any(word in query_lower for word in ["related", "subsidiary", "subsidiaries", "parent"]):
        suggestions.append("find_related_entities")
    
    if any(word in query_lower for word in ["profile", "information", "details"]):
        suggestions.append("get_comprehensive_entity_profile")
    
    # Default suggestions
    if not suggestions:
        suggestions = [
            "get_comprehensive_entity_profile",
            "find_related_entities",
            "find_related_securities"
        ]
    
    return suggestions
