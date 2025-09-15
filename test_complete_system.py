#!/usr/bin/env python3
"""Test the complete enhanced entity search system"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.enhanced_entity_resolver import EnhancedEntityResolver, IdentifierType

def test_complete_system():
    print("Testing Complete Enhanced Entity Search System")
    print("=" * 50)
    
    # Initialize resolver
    resolver = EnhancedEntityResolver()
    
    # Test cases
    test_cases = [
        ("Apple CIK (SEC API)", "0000320193", IdentifierType.CIK),
        ("Apple Ticker (SEC API)", "AAPL", IdentifierType.TICKER),
        ("Apple Name (SEC API)", "Apple", IdentifierType.NAME),
        ("Delisted Company CIK (EDGAR Fallback)", "0000886158", IdentifierType.CIK),
    ]
    
    for test_name, identifier, id_type in test_cases:
        print(f"\n{test_name}:")
        print(f"  Searching for: {identifier}")
        
        profile = resolver.resolve_entity(identifier, id_type)
        
        if profile:
            print(f"  ✅ Found: {profile.entity_name}")
            print(f"  CIK: {profile.primary_identifiers.get('cik', 'N/A')}")
            print(f"  Ticker: {profile.primary_identifiers.get('ticker', 'N/A')}")
            print(f"  Data Sources: {profile.data_sources}")
            print(f"  Confidence: {profile.confidence_score}")
        else:
            print(f"  ❌ No entity found")

if __name__ == "__main__":
    test_complete_system()
