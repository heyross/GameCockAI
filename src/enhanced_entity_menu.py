#!/usr/bin/env python3
"""
Enhanced Entity Search Menu for GameCock AI System.

This module provides an enhanced menu system for entity search and resolution
with support for multiple identifier types and comprehensive entity profiles.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .enhanced_entity_resolver import (
    EnhancedEntityResolver, EntityProfile, EntityMatch, 
    IdentifierType, EntityType
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import SessionLocal

logger = logging.getLogger(__name__)

class EnhancedEntityMenu:
    """Enhanced entity search menu system."""
    
    def __init__(self):
        """Initialize the enhanced entity menu."""
        self.db_session = SessionLocal()
        self.resolver = EnhancedEntityResolver(self.db_session)
    
    def display_main_menu(self):
        """Display the main enhanced entity search menu."""
        while True:
            print("\n" + "="*60)
            print("🔍 ENHANCED ENTITY SEARCH & RESOLUTION")
            print("="*60)
            print("1. Search by Company Name/Ticker")
            print("2. Search by CIK")
            print("3. Search by CUSIP")
            print("4. Search by ISIN")
            print("5. Search by LEI")
            print("6. Fuzzy/Partial Search")
            print("7. View Entity Profile")
            print("8. Find Related Entities")
            print("9. Find Related Securities")
            print("B. Back to Main Menu")
            print("="*60)
            
            choice = input("Enter your choice: ").strip().lower()
            
            if choice == '1':
                self._search_by_name_ticker()
            elif choice == '2':
                self._search_by_cik()
            elif choice == '3':
                self._search_by_cusip()
            elif choice == '4':
                self._search_by_isin()
            elif choice == '5':
                self._search_by_lei()
            elif choice == '6':
                self._fuzzy_partial_search()
            elif choice == '7':
                self._view_entity_profile()
            elif choice == '8':
                self._find_related_entities()
            elif choice == '9':
                self._find_related_securities()
            elif choice == 'b':
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _search_by_name_ticker(self):
        """Search for entities by name or ticker."""
        print("\n--- Search by Company Name/Ticker ---")
        search_term = input("Enter company name or ticker: ").strip()
        
        if not search_term:
            print("❌ Search term cannot be empty.")
            return
        
        try:
            # Try to resolve as ticker first, then name
            entity_profile = self.resolver.resolve_entity(search_term, IdentifierType.TICKER)
            if not entity_profile:
                entity_profile = self.resolver.resolve_entity(search_term, IdentifierType.NAME)
            
            if entity_profile:
                self._display_entity_profile(entity_profile)
            else:
                # Try fuzzy search
                matches = self.resolver.search_entities(search_term, 10)
                if matches:
                    self._display_search_results(matches, search_term)
                else:
                    print(f"❌ No entities found for '{search_term}'")
                    print("💡 Try a different spelling or ticker symbol")
        
        except Exception as e:
            print(f"❌ Error searching entities: {str(e)}")
    
    def _search_by_cik(self):
        """Search for entities by CIK."""
        print("\n--- Search by CIK ---")
        cik = input("Enter CIK (4-10 digits): ").strip()
        
        if not cik:
            print("❌ CIK cannot be empty.")
            return
        
        try:
            entity_profile = self.resolver.resolve_entity(cik, IdentifierType.CIK)
            if entity_profile:
                self._display_entity_profile(entity_profile)
            else:
                print(f"❌ No entity found for CIK '{cik}'")
                print("💡 This CIK may not exist or may be for a company that:")
                print("   • Is no longer actively trading")
                print("   • Has been delisted or acquired")
                print("   • Is a private company with limited filings")
                print("   • Has been removed from SEC API but exists in EDGAR")
        
        except Exception as e:
            print(f"❌ Error searching by CIK: {str(e)}")
    
    def _search_by_cusip(self):
        """Search for entities by CUSIP."""
        print("\n--- Search by CUSIP ---")
        cusip = input("Enter CUSIP (6-9 characters): ").strip().upper()
        
        if not cusip:
            print("❌ CUSIP cannot be empty.")
            return
        
        try:
            entity_profile = self.resolver.resolve_entity(cusip, IdentifierType.CUSIP)
            if entity_profile:
                self._display_entity_profile(entity_profile)
            else:
                print(f"❌ No entity found for CUSIP '{cusip}'")
                print("💡 CUSIP search requires data in the local database.")
                print("   This CUSIP may not be in the current dataset or the")
                print("   database may need to be populated with Form 13F or N-MFP data.")
        
        except Exception as e:
            print(f"❌ Error searching by CUSIP: {str(e)}")
    
    def _search_by_isin(self):
        """Search for entities by ISIN."""
        print("\n--- Search by ISIN ---")
        isin = input("Enter ISIN (12 characters): ").strip().upper()
        
        if not isin:
            print("❌ ISIN cannot be empty.")
            return
        
        try:
            entity_profile = self.resolver.resolve_entity(isin, IdentifierType.ISIN)
            if entity_profile:
                self._display_entity_profile(entity_profile)
            else:
                print(f"❌ No entity found for ISIN '{isin}'")
                print("💡 Check the ISIN format (2-letter country code + 10 characters)")
        
        except Exception as e:
            print(f"❌ Error searching by ISIN: {str(e)}")
    
    def _search_by_lei(self):
        """Search for entities by LEI."""
        print("\n--- Search by LEI ---")
        lei = input("Enter LEI (20 characters): ").strip().upper()
        
        if not lei:
            print("❌ LEI cannot be empty.")
            return
        
        try:
            entity_profile = self.resolver.resolve_entity(lei, IdentifierType.LEI)
            if entity_profile:
                self._display_entity_profile(entity_profile)
            else:
                print(f"❌ No entity found for LEI '{lei}'")
                print("💡 Check the LEI format (20 alphanumeric characters)")
        
        except Exception as e:
            print(f"❌ Error searching by LEI: {str(e)}")
    
    def _fuzzy_partial_search(self):
        """Perform fuzzy/partial search."""
        print("\n--- Fuzzy/Partial Search ---")
        search_term = input("Enter partial name or identifier: ").strip()
        
        if not search_term:
            print("❌ Search term cannot be empty.")
            return
        
        try:
            # Try auto-detection first
            entity_profile = self.resolver.resolve_entity(search_term, IdentifierType.AUTO)
            if entity_profile:
                self._display_entity_profile(entity_profile)
            else:
                # Try fuzzy search
                matches = self.resolver.search_entities(search_term, 15)
                if matches:
                    self._display_search_results(matches, search_term)
                else:
                    print(f"❌ No entities found for '{search_term}'")
                    print("💡 Try a different search term or check spelling")
        
        except Exception as e:
            print(f"❌ Error in fuzzy search: {str(e)}")
    
    def _view_entity_profile(self):
        """View comprehensive entity profile."""
        print("\n--- View Entity Profile ---")
        entity_id = input("Enter Entity ID (CIK): ").strip()
        
        if not entity_id:
            print("❌ Entity ID cannot be empty.")
            return
        
        try:
            profile = self.resolver.get_entity_profile(entity_id)
            if profile:
                self._display_comprehensive_profile(profile)
            else:
                print(f"❌ No entity profile found for ID '{entity_id}'")
                print("💡 Check the Entity ID format")
        
        except Exception as e:
            print(f"❌ Error viewing entity profile: {str(e)}")
    
    def _find_related_entities(self):
        """Find related entities."""
        print("\n--- Find Related Entities ---")
        entity_id = input("Enter Entity ID (CIK): ").strip()
        
        if not entity_id:
            print("❌ Entity ID cannot be empty.")
            return
        
        try:
            related_entities = self.resolver.find_related_entities(entity_id)
            if related_entities:
                self._display_related_entities(related_entities, entity_id)
            else:
                print(f"❌ No related entities found for ID '{entity_id}'")
                print("💡 This entity may not have related entities in the database")
        
        except Exception as e:
            print(f"❌ Error finding related entities: {str(e)}")
    
    def _find_related_securities(self):
        """Find related securities."""
        print("\n--- Find Related Securities ---")
        entity_id = input("Enter Entity ID (CIK): ").strip()
        
        if not entity_id:
            print("❌ Entity ID cannot be empty.")
            return
        
        try:
            related_securities = self.resolver.find_related_securities(entity_id)
            if related_securities:
                self._display_related_securities(related_securities, entity_id)
            else:
                print(f"❌ No related securities found for ID '{entity_id}'")
                print("💡 This entity may not have securities in the database")
        
        except Exception as e:
            print(f"❌ Error finding related securities: {str(e)}")
    
    def _display_entity_profile(self, profile: EntityProfile):
        """Display basic entity profile."""
        print("\n" + "="*50)
        print("📋 ENTITY PROFILE")
        print("="*50)
        print(f"🏢 Entity Name: {profile.entity_name}")
        print(f"🆔 Entity ID: {profile.entity_id}")
        print(f"📊 Entity Type: {profile.entity_type.value.title()}")
        print(f"🎯 Confidence Score: {profile.confidence_score:.2f}")
        print(f"📅 Last Updated: {profile.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if profile.primary_identifiers:
            print("\n🔑 Primary Identifiers:")
            for key, value in profile.primary_identifiers.items():
                print(f"   {key.upper()}: {value}")
        
        if profile.data_sources:
            print(f"\n📚 Data Sources: {', '.join(profile.data_sources)}")
        
        print("="*50)
    
    def _display_comprehensive_profile(self, profile: EntityProfile):
        """Display comprehensive entity profile."""
        self._display_entity_profile(profile)
        
        if profile.related_entities:
            print(f"\n🔗 Related Entities ({len(profile.related_entities)}):")
            for i, entity in enumerate(profile.related_entities[:10], 1):  # Show first 10
                print(f"   {i}. {entity.entity_name} ({entity.entity_id})")
                print(f"      Relationship: {entity.relationship_type}")
                print(f"      Confidence: {entity.confidence:.2f}")
            if len(profile.related_entities) > 10:
                print(f"   ... and {len(profile.related_entities) - 10} more")
        
        if profile.related_securities:
            print(f"\n💼 Related Securities ({len(profile.related_securities)}):")
            for i, security in enumerate(profile.related_securities[:10], 1):  # Show first 10
                print(f"   {i}. {security.security_name}")
                print(f"      Type: {security.security_type}")
                if security.cusip:
                    print(f"      CUSIP: {security.cusip}")
                if security.face_value:
                    print(f"      Value: ${security.face_value:,.2f}")
            if len(profile.related_securities) > 10:
                print(f"   ... and {len(profile.related_securities) - 10} more")
    
    def _display_search_results(self, matches: List[EntityMatch], search_term: str):
        """Display search results."""
        print(f"\n🔍 Search Results for '{search_term}' ({len(matches)} found):")
        print("="*60)
        
        for i, match in enumerate(matches, 1):
            print(f"{i}. Entity ID: {match.entity_id}")
            if "name" in match.matched_identifiers:
                print(f"   Name: {match.matched_identifiers['name']}")
            if "ticker" in match.matched_identifiers:
                print(f"   Ticker: {match.matched_identifiers['ticker']}")
            print(f"   Match Type: {match.match_type}")
            print(f"   Confidence: {match.confidence_score:.2f}")
            print("-" * 40)
    
    def _display_related_entities(self, related_entities: List, entity_id: str):
        """Display related entities."""
        print(f"\n🔗 Related Entities for {entity_id} ({len(related_entities)} found):")
        print("="*60)
        
        for i, entity in enumerate(related_entities, 1):
            print(f"{i}. {entity.entity_name}")
            print(f"   Entity ID: {entity.entity_id}")
            print(f"   Relationship: {entity.relationship_type}")
            print(f"   Confidence: {entity.confidence:.2f}")
            print("-" * 40)
    
    def _display_related_securities(self, related_securities: List, entity_id: str):
        """Display related securities."""
        print(f"\n💼 Related Securities for {entity_id} ({len(related_securities)} found):")
        print("="*60)
        
        for i, security in enumerate(related_securities, 1):
            print(f"{i}. {security.security_name}")
            print(f"   Type: {security.security_type}")
            if security.cusip:
                print(f"   CUSIP: {security.cusip}")
            if security.isin:
                print(f"   ISIN: {security.isin}")
            if security.face_value:
                print(f"   Value: ${security.face_value:,.2f}")
            if security.currency:
                print(f"   Currency: {security.currency}")
            print("-" * 40)
    
    def close(self):
        """Close the database session."""
        if self.db_session:
            self.db_session.close()

def enhanced_entity_search_menu():
    """Main function to run the enhanced entity search menu."""
    menu = EnhancedEntityMenu()
    try:
        menu.display_main_menu()
    finally:
        menu.close()
