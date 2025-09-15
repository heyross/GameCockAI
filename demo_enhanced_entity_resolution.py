#!/usr/bin/env python3
"""
Demonstration of Enhanced Entity Resolution System.

This script demonstrates the key features of the enhanced entity resolution system
including multi-identifier lookup, fuzzy matching, and relationship discovery.
"""

import os
import sys
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def demo_enhanced_entity_resolution():
    """Demonstrate the enhanced entity resolution system."""
    print("🔍 Enhanced Entity Resolution System Demo")
    print("=" * 50)
    
    try:
        from src.enhanced_entity_resolver import (
            EnhancedEntityResolver, IdentifierType, EntityType
        )
        from database import SessionLocal
        
        print("✅ Successfully imported enhanced entity resolver")
        
        # Create resolver with database session
        db_session = SessionLocal()
        resolver = EnhancedEntityResolver(db_session)
        
        print("\n📋 Testing Identifier Type Detection:")
        print("-" * 30)
        
        # Test identifier type detection
        test_identifiers = [
            ("1234567", "CIK"),
            ("037833100", "CUSIP"),
            ("US0378331005", "ISIN"),
            ("AAPL", "Ticker"),
            ("Apple Inc", "Name")
        ]
        
        for identifier, expected_type in test_identifiers:
            detected_type = resolver._detect_identifier_type(identifier)
            print(f"  {identifier:15} → {detected_type.value:10} (expected: {expected_type})")
        
        print("\n🔧 Testing Identifier Cleaning:")
        print("-" * 30)
        
        # Test identifier cleaning
        test_cleaning = [
            ("1234567", IdentifierType.CIK),
            ("aapl", IdentifierType.TICKER),
            ("  Apple   Inc.  ", IdentifierType.NAME)
        ]
        
        for identifier, id_type in test_cleaning:
            cleaned = resolver._clean_identifier(identifier, id_type)
            print(f"  {identifier:20} → {cleaned}")
        
        print("\n🎯 Testing Entity Resolution:")
        print("-" * 30)
        
        # Test entity resolution (this will work if we have data in the database)
        test_resolutions = [
            ("AAPL", IdentifierType.TICKER),
            ("Apple", IdentifierType.NAME),
            ("0000320193", IdentifierType.CIK)
        ]
        
        for identifier, id_type in test_resolutions:
            try:
                profile = resolver.resolve_entity(identifier, id_type)
                if profile:
                    print(f"  ✅ {identifier:15} → {profile.entity_name} (confidence: {profile.confidence_score:.2f})")
                else:
                    print(f"  ❌ {identifier:15} → No entity found")
            except Exception as e:
                print(f"  ⚠️  {identifier:15} → Error: {str(e)}")
        
        print("\n🔍 Testing Entity Search:")
        print("-" * 30)
        
        # Test entity search
        try:
            matches = resolver.search_entities("Apple", 5)
            if matches:
                print(f"  Found {len(matches)} matches for 'Apple':")
                for i, match in enumerate(matches[:3], 1):
                    print(f"    {i}. {match.matched_identifiers.get('name', 'Unknown')} ({match.entity_id})")
            else:
                print("  No matches found for 'Apple'")
        except Exception as e:
            print(f"  Error in search: {str(e)}")
        
        print("\n🔗 Testing Related Entity Discovery:")
        print("-" * 30)
        
        # Test related entity discovery
        try:
            related = resolver.find_related_entities("0000320193")
            if related:
                print(f"  Found {len(related)} related entities for Apple:")
                for i, entity in enumerate(related[:3], 1):
                    print(f"    {i}. {entity.entity_name} ({entity.relationship_type})")
            else:
                print("  No related entities found for Apple")
        except Exception as e:
            print(f"  Error finding related entities: {str(e)}")
        
        print("\n💼 Testing Related Security Discovery:")
        print("-" * 30)
        
        # Test related security discovery
        try:
            securities = resolver.find_related_securities("0000320193")
            if securities:
                print(f"  Found {len(securities)} related securities for Apple:")
                for i, security in enumerate(securities[:3], 1):
                    print(f"    {i}. {security.security_name} ({security.security_type})")
            else:
                print("  No related securities found for Apple")
        except Exception as e:
            print(f"  Error finding related securities: {str(e)}")
        
        # Close database session
        db_session.close()
        
        print("\n✅ Enhanced Entity Resolution Demo Complete!")
        print("\nKey Features Demonstrated:")
        print("  • Multi-identifier type detection (CIK, CUSIP, ISIN, LEI, Ticker, Name)")
        print("  • Identifier cleaning and normalization")
        print("  • Entity resolution with confidence scoring")
        print("  • Fuzzy and partial matching")
        print("  • Related entity discovery")
        print("  • Related security discovery")
        print("  • Comprehensive entity profiling")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required modules are available.")
    except Exception as e:
        print(f"❌ Error during demo: {e}")

def demo_ai_tools():
    """Demonstrate the AI agent tools."""
    print("\n🤖 AI Agent Tools Demo")
    print("=" * 30)
    
    try:
        from src.enhanced_entity_tools import (
            resolve_entity_by_identifier, search_entities_by_name,
            resolve_entity_for_ai_query
        )
        import json
        
        print("✅ Successfully imported AI agent tools")
        
        print("\n🔍 Testing Entity Resolution Tool:")
        print("-" * 30)
        
        # Test entity resolution tool
        try:
            result = resolve_entity_by_identifier("AAPL", "ticker")
            result_data = json.loads(result)
            if "entity_profile" in result_data:
                profile = result_data["entity_profile"]
                print(f"  ✅ Found: {profile['entity_name']} (confidence: {profile['confidence_score']:.2f})")
            else:
                print(f"  ❌ No entity found: {result_data.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")
        
        print("\n🔍 Testing Entity Search Tool:")
        print("-" * 30)
        
        # Test entity search tool
        try:
            result = search_entities_by_name("Apple", 5)
            result_data = json.loads(result)
            if "search_results" in result_data:
                results = result_data["search_results"]
                print(f"  ✅ Found {len(results)} matches:")
                for i, match in enumerate(results[:3], 1):
                    print(f"    {i}. {match['matched_identifiers'].get('name', 'Unknown')} ({match['entity_id']})")
            else:
                print(f"  ❌ No matches: {result_data.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")
        
        print("\n🤖 Testing AI Query Resolution:")
        print("-" * 30)
        
        # Test AI query resolution
        test_queries = [
            "Show me swaps for CIK 0000320193",
            "Find Apple's bonds",
            "What securities does Microsoft have?"
        ]
        
        for query in test_queries:
            try:
                result = resolve_entity_for_ai_query(query)
                result_data = json.loads(result)
                if "resolved_entities" in result_data:
                    entities = result_data["resolved_entities"]
                    print(f"  ✅ Query: '{query}'")
                    print(f"     Resolved {len(entities)} entities")
                    if "suggested_actions" in result_data:
                        actions = result_data["suggested_actions"]
                        print(f"     Suggested actions: {', '.join(actions[:2])}")
                else:
                    print(f"  ❌ Query: '{query}' - {result_data.get('message', 'No entities found')}")
            except Exception as e:
                print(f"  ⚠️  Query: '{query}' - Error: {str(e)}")
        
        print("\n✅ AI Agent Tools Demo Complete!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error during AI tools demo: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Entity Resolution System Demonstration")
    print("=" * 60)
    
    # Run the demos
    demo_enhanced_entity_resolution()
    demo_ai_tools()
    
    print("\n🎉 Demonstration Complete!")
    print("\nNext Steps:")
    print("  1. Run the enhanced entity search menu: python app.py")
    print("  2. Test with real data by downloading SEC data")
    print("  3. Use the AI agent tools in your RAG system")
    print("  4. Extend the system with additional data sources")
