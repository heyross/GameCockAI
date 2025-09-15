#!/usr/bin/env python3
"""Test enhanced entity resolver directly"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.enhanced_entity_resolver import EnhancedEntityResolver, IdentifierType

def test_entity_resolver():
    print("Testing Enhanced Entity Resolver...")
    
    # Initialize resolver (no database session needed for SEC API)
    resolver = EnhancedEntityResolver()
    
    # Test CIK search
    print("\n1. Testing CIK search for Apple (0000320193):")
    profile = resolver.resolve_entity("0000320193", IdentifierType.CIK)
    if profile:
        print(f"  Found: {profile.entity_name}")
        print(f"  CIK: {profile.primary_identifiers.get('cik', 'N/A')}")
        print(f"  Ticker: {profile.primary_identifiers.get('ticker', 'N/A')}")
        print(f"  Confidence: {profile.confidence_score}")
    else:
        print("  No profile found")
    
    # Test CIK search without leading zeros
    print("\n2. Testing CIK search for Apple (320193):")
    profile = resolver.resolve_entity("320193", IdentifierType.CIK)
    if profile:
        print(f"  Found: {profile.entity_name}")
        print(f"  CIK: {profile.primary_identifiers.get('cik', 'N/A')}")
        print(f"  Ticker: {profile.primary_identifiers.get('ticker', 'N/A')}")
        print(f"  Confidence: {profile.confidence_score}")
    else:
        print("  No profile found")
    
    # Test ticker search
    print("\n3. Testing ticker search for Apple (AAPL):")
    profile = resolver.resolve_entity("AAPL", IdentifierType.TICKER)
    if profile:
        print(f"  Found: {profile.entity_name}")
        print(f"  CIK: {profile.primary_identifiers.get('cik', 'N/A')}")
        print(f"  Ticker: {profile.primary_identifiers.get('ticker', 'N/A')}")
        print(f"  Confidence: {profile.confidence_score}")
    else:
        print("  No profile found")
    
    # Test name search
    print("\n4. Testing name search for Apple:")
    profile = resolver.resolve_entity("Apple", IdentifierType.NAME)
    if profile:
        print(f"  Found: {profile.entity_name}")
        print(f"  CIK: {profile.primary_identifiers.get('cik', 'N/A')}")
        print(f"  Ticker: {profile.primary_identifiers.get('ticker', 'N/A')}")
        print(f"  Confidence: {profile.confidence_score}")
    else:
        print("  No profile found")

if __name__ == "__main__":
    test_entity_resolver()
