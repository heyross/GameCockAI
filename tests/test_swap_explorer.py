"""
Comprehensive tests for Swap Explorer & Single Party Risk Analyzer

Tests the core functionality of the swap explorer including:
- Data integration
- Entity resolution
- Risk analysis
- Obligation tracking
"""

import unittest
import tempfile
import shutil
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path for imports
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from swap_explorer import (
        SwapExplorer, EntityIdentifier, SwapExposure, RiskTrigger, Obligation,
        AssetClass, RiskLevel
    )
    from swap_data_integration import SwapDataIntegration
    from entity_resolution_engine import EntityResolutionEngine, EntityMatch
    SWAP_EXPLORER_AVAILABLE = True
except ImportError as e:
    SWAP_EXPLORER_AVAILABLE = False
    print(f"⚠️  Swap Explorer modules not available: {e}")

class TestSwapExplorer(unittest.TestCase):
    """Test cases for Swap Explorer core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not SWAP_EXPLORER_AVAILABLE:
            self.skipTest("Swap Explorer modules not available")
        
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_gamecock.db")
        
        # Initialize swap explorer
        self.explorer = SwapExplorer(self.db_path)
        
        # Create test entities
        self.setup_test_entities()
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # On Windows, files might still be in use
                pass
    
    def setup_test_entities(self):
        """Set up test entities and data"""
        # Register test entities
        self.explorer.register_entity("TEST_CORP", EntityIdentifier(
            lei="TEST123456789",
            cik="0001234567",
            ticker="TEST",
            name="Test Corporation",
            aliases=["Test Corp", "Test Inc"]
        ))
        
        self.explorer.register_entity("TEST_BANK", EntityIdentifier(
            lei="BANK987654321",
            cik="0007654321",
            ticker="BANK",
            name="Test Bank",
            aliases=["Test Bank Corp", "Test Financial"]
        ))
        
        # Add test swap exposures
        self.explorer.add_swap_exposure(SwapExposure(
            entity_id="TEST_CORP",
            counterparty_id="TEST_BANK",
            asset_class=AssetClass.INTEREST_RATE,
            notional_amount=100000000,  # $100M
            market_value=2500000,  # $2.5M
            maturity_date=datetime.now() + timedelta(days=365),
            trade_date=datetime.now() - timedelta(days=30),
            data_source="CFTC",
            risk_metrics={"duration": 2.5, "dv01": 250000}
        ))
        
        self.explorer.add_swap_exposure(SwapExposure(
            entity_id="TEST_CORP",
            counterparty_id="TEST_BANK",
            asset_class=AssetClass.CREDIT,
            notional_amount=50000000,  # $50M
            market_value=-1000000,  # -$1M
            maturity_date=datetime.now() + timedelta(days=730),
            trade_date=datetime.now() - timedelta(days=60),
            data_source="DTCC",
            risk_metrics={"spread_duration": 3.2, "credit_dv01": 160000}
        ))
        
        # Add test obligations
        self.explorer.add_obligation(Obligation(
            entity_id="TEST_CORP",
            obligation_type="payment",
            amount=500000,  # $500K
            due_date=datetime.now() + timedelta(days=15),
            counterparty_id="TEST_BANK",
            description="Quarterly interest payment"
        ))
    
    def test_entity_registration(self):
        """Test entity registration functionality"""
        # Test successful registration
        result = self.explorer.register_entity("NEW_ENTITY", EntityIdentifier(
            lei="NEW123456789",
            name="New Entity"
        ))
        self.assertTrue(result)
        
        # Test duplicate registration
        result = self.explorer.register_entity("NEW_ENTITY", EntityIdentifier(
            lei="NEW123456789",
            name="New Entity Updated"
        ))
        self.assertTrue(result)  # Should update existing
    
    def test_swap_exposure_management(self):
        """Test swap exposure management"""
        # Test adding exposure
        exposure = SwapExposure(
            entity_id="TEST_CORP",
            counterparty_id="NEW_COUNTERPARTY",
            asset_class=AssetClass.EQUITY,
            notional_amount=25000000,
            market_value=500000,
            maturity_date=datetime.now() + timedelta(days=180),
            trade_date=datetime.now() - timedelta(days=10),
            data_source="SEC"
        )
        
        result = self.explorer.add_swap_exposure(exposure)
        self.assertTrue(result)
    
    def test_obligation_management(self):
        """Test obligation management"""
        # Test adding obligation
        obligation = Obligation(
            entity_id="TEST_CORP",
            obligation_type="collateral",
            amount=1000000,
            due_date=datetime.now() + timedelta(days=7),
            counterparty_id="TEST_BANK",
            description="Initial margin posting"
        )
        
        result = self.explorer.add_obligation(obligation)
        self.assertTrue(result)
    
    def test_exposure_summary(self):
        """Test exposure summary generation"""
        summary = self.explorer.get_entity_exposure_summary("TEST_CORP")
        
        # Verify summary structure
        self.assertIn('entity_id', summary)
        self.assertIn('total_notional_exposure', summary)
        self.assertIn('total_market_value', summary)
        self.assertIn('exposure_by_asset_class', summary)
        self.assertIn('top_counterparties', summary)
        
        # Verify data
        self.assertEqual(summary['entity_id'], "TEST_CORP")
        self.assertGreater(summary['total_notional_exposure'], 0)
        self.assertGreater(summary['total_market_value'], 0)
        self.assertGreater(summary['total_positions'], 0)
    
    def test_risk_trigger_detection(self):
        """Test risk trigger detection"""
        triggers = self.explorer.detect_risk_triggers("TEST_CORP")
        
        # Should detect negative market value trigger
        negative_triggers = [t for t in triggers if t.trigger_type == "negative_market_value"]
        self.assertGreater(len(negative_triggers), 0)
        
        # Verify trigger structure
        for trigger in triggers:
            self.assertIn('entity_id', trigger.__dict__)
            self.assertIn('trigger_type', trigger.__dict__)
            self.assertIn('severity', trigger.__dict__)
            self.assertIn('description', trigger.__dict__)
    
    def test_risk_report_generation(self):
        """Test risk report generation"""
        report = self.explorer.generate_risk_report("TEST_CORP")
        
        # Verify report structure
        self.assertIn("COMPREHENSIVE SWAP RISK ANALYSIS REPORT", report)
        self.assertIn("EXPOSURE SUMMARY", report)
        self.assertIn("ASSET CLASS BREAKDOWN", report)
        self.assertIn("TOP COUNTERPARTIES", report)
        self.assertIn("RISK TRIGGERS", report)
        
        # Verify report contains data
        self.assertIn("TEST_CORP", report)
        self.assertIn("$", report)  # Should contain monetary amounts


class TestSwapDataIntegration(unittest.TestCase):
    """Test cases for Swap Data Integration"""
    
    def setUp(self):
        """Set up test environment"""
        if not SWAP_EXPLORER_AVAILABLE:
            self.skipTest("Swap Explorer modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_gamecock.db")
        
        self.integration = SwapDataIntegration(self.db_path)
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                pass
    
    def test_cftc_data_loading(self):
        """Test CFTC data loading"""
        cftc_data = self.integration.load_cftc_data()
        
        # Should return a list (may be empty if no CFTC data available)
        self.assertIsInstance(cftc_data, list)
        
        # If data exists, verify structure
        if cftc_data:
            record = cftc_data[0]
            self.assertIn('data_source', record)
            self.assertEqual(record['data_source'], 'CFTC')
    
    def test_dtcc_data_loading(self):
        """Test DTCC data loading"""
        dtcc_data = self.integration.load_dtcc_data()
        
        # Should return a list
        self.assertIsInstance(dtcc_data, list)
        
        # Verify sample data structure
        if dtcc_data:
            record = dtcc_data[0]
            self.assertIn('data_source', record)
            self.assertEqual(record['data_source'], 'DTCC')
            self.assertIn('notional_amount', record)
            self.assertIn('market_value', record)
    
    def test_sec_data_loading(self):
        """Test SEC data loading"""
        sec_data = self.integration.load_sec_filing_data()
        
        # Should return a list
        self.assertIsInstance(sec_data, list)
        
        # Verify sample data structure
        if sec_data:
            record = sec_data[0]
            self.assertIn('data_source', record)
            self.assertEqual(record['data_source'], 'SEC')
            self.assertIn('filing_type', record)
            self.assertIn('derivative_disclosures', record)
    
    def test_data_aggregation(self):
        """Test data aggregation functionality"""
        aggregated_data = self.integration.aggregate_entity_data("TEST_ENTITY")
        
        # Verify aggregation structure
        self.assertIn('entity_id', aggregated_data)
        self.assertIn('data_sources', aggregated_data)
        self.assertIn('summary', aggregated_data)
        
        # Verify data sources
        self.assertIn('cftc', aggregated_data['data_sources'])
        self.assertIn('dtcc', aggregated_data['data_sources'])
        self.assertIn('sec', aggregated_data['data_sources'])
        
        # Verify summary
        summary = aggregated_data['summary']
        self.assertIn('total_records', summary)
        self.assertIn('total_notional', summary)
        self.assertIn('data_quality_score', summary)
    
    def test_cross_referencing(self):
        """Test entity cross-referencing"""
        cross_refs = self.integration.cross_reference_entities("TEST_ENTITY")
        
        # Verify cross-reference structure
        self.assertIn('cftc_entities', cross_refs)
        self.assertIn('dtcc_entities', cross_refs)
        self.assertIn('sec_entities', cross_refs)
        self.assertIn('matched_entities', cross_refs)
        
        # Should return lists
        for key in ['cftc_entities', 'dtcc_entities', 'sec_entities', 'matched_entities']:
            self.assertIsInstance(cross_refs[key], list)


class TestEntityResolutionEngine(unittest.TestCase):
    """Test cases for Entity Resolution Engine"""
    
    def setUp(self):
        """Set up test environment"""
        if not SWAP_EXPLORER_AVAILABLE:
            self.skipTest("Swap Explorer modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_gamecock.db")
        
        self.engine = EntityResolutionEngine(self.db_path)
        
        # Set up test entities
        self.setup_test_entities()
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                pass
    
    def setup_test_entities(self):
        """Set up test entities for resolution testing"""
        # Register test entities
        self.engine.register_entity("ENTITY_A", {
            'lei': 'LEI123456789',
            'cik': '0001234567',
            'ticker': 'ENTA',
            'name': 'Entity A Corporation',
            'aliases': ['Entity A Corp', 'Entity A Inc']
        })
        
        self.engine.register_entity("ENTITY_B", {
            'lei': 'LEI987654321',
            'cik': '0007654321',
            'ticker': 'ENTB',
            'name': 'Entity B Corporation',
            'aliases': ['Entity B Corp', 'Entity B Inc']
        })
        
        # Entity with similar identifiers to Entity A
        self.engine.register_entity("ENTITY_A_SIMILAR", {
            'lei': 'LEI123456789',  # Same LEI
            'cik': '0001234567',    # Same CIK
            'ticker': 'ENTA',
            'name': 'Entity A Corp',  # Similar name
            'aliases': ['Entity A Corporation']
        })
    
    def test_entity_registration(self):
        """Test entity registration"""
        result = self.engine.register_entity("NEW_ENTITY", {
            'lei': 'NEW123456789',
            'name': 'New Entity',
            'aliases': ['New Corp']
        })
        
        self.assertTrue(result)
        self.assertIn("NEW_ENTITY", self.engine.entity_registry)
    
    def test_exact_matching(self):
        """Test exact entity matching"""
        search_entities = [
            {
                'entity_id': 'ENTITY_A_SIMILAR',
                'lei': 'LEI123456789',
                'cik': '0001234567',
                'ticker': 'ENTA',
                'name': 'Entity A Corp',
                'aliases': ['Entity A Corporation']
            }
        ]
        
        matches = self.engine.find_matches("ENTITY_A_SIMILAR", search_entities)
        
        # Should find exact match
        self.assertGreater(len(matches), 0)
        
        # Should have high confidence
        best_match = matches[0]
        self.assertGreater(best_match.confidence_score, 0.9)
        # With matching LEI and CIK, this should be exact match
        self.assertEqual(best_match.match_type, "exact")
        self.assertIn('lei', best_match.matched_fields)
        self.assertIn('cik', best_match.matched_fields)
    
    def test_fuzzy_matching(self):
        """Test fuzzy entity matching"""
        search_entities = [
            {
                'entity_id': 'ENTITY_B',
                'lei': 'LEI987654321',
                'cik': '0007654321',
                'ticker': 'ENTB',
                'name': 'Entity B Corp',  # Similar but not exact
                'aliases': ['Entity B Corporation']
            }
        ]
        
        matches = self.engine.find_matches("ENTITY_A", search_entities)
        
        # Should not match (different LEI/CIK)
        self.assertEqual(len(matches), 0)
    
    def test_name_similarity(self):
        """Test name similarity calculation"""
        similarity = self.engine._calculate_name_similarity(
            "ABC Corporation",
            "ABC Corp"
        )
        
        self.assertGreater(similarity, 0.8)
        self.assertLessEqual(similarity, 1.0)
    
    def test_name_normalization(self):
        """Test name normalization"""
        normalized = self.engine._normalize_name("ABC Corporation Inc.")
        
        self.assertIn("abc", normalized)
        self.assertNotIn("corporation", normalized)
        self.assertNotIn("inc", normalized)
        self.assertNotIn(".", normalized)
    
    def test_entity_relationships(self):
        """Test entity relationship retrieval"""
        relationships = self.engine.get_entity_relationships("ENTITY_A")
        
        # Verify structure
        self.assertIn('entity_id', relationships)
        self.assertIn('matches', relationships)
        self.assertIn('aliases', relationships)
        self.assertIn('total_matches', relationships)
        
        # Verify data types
        self.assertIsInstance(relationships['matches'], list)
        self.assertIsInstance(relationships['aliases'], list)
        self.assertIsInstance(relationships['total_matches'], int)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete swap explorer system"""
    
    def setUp(self):
        """Set up integration test environment"""
        if not SWAP_EXPLORER_AVAILABLE:
            self.skipTest("Swap Explorer modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_gamecock.db")
        
        # Initialize all components
        self.explorer = SwapExplorer(self.db_path)
        self.integration = SwapDataIntegration(self.db_path)
        self.resolution_engine = EntityResolutionEngine(self.db_path)
    
    def tearDown(self):
        """Clean up integration test environment"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                pass
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # 1. Register entities
        self.explorer.register_entity("INTEGRATION_TEST", EntityIdentifier(
            lei="INT123456789",
            cik="0001234567",
            ticker="INT",
            name="Integration Test Corp",
            aliases=["Integration Test", "Int Test Corp"]
        ))
        
        # 2. Add swap exposures
        self.explorer.add_swap_exposure(SwapExposure(
            entity_id="INTEGRATION_TEST",
            counterparty_id="TEST_COUNTERPARTY",
            asset_class=AssetClass.INTEREST_RATE,
            notional_amount=75000000,
            market_value=1500000,
            maturity_date=datetime.now() + timedelta(days=500),
            trade_date=datetime.now() - timedelta(days=45),
            data_source="CFTC"
        ))
        
        # 3. Add obligations
        self.explorer.add_obligation(Obligation(
            entity_id="INTEGRATION_TEST",
            obligation_type="payment",
            amount=750000,
            due_date=datetime.now() + timedelta(days=20),
            counterparty_id="TEST_COUNTERPARTY",
            description="Monthly payment"
        ))
        
        # 4. Generate exposure summary
        summary = self.explorer.get_entity_exposure_summary("INTEGRATION_TEST")
        self.assertGreater(summary['total_notional_exposure'], 0)
        
        # 5. Detect risk triggers
        triggers = self.explorer.detect_risk_triggers("INTEGRATION_TEST")
        # May or may not have triggers depending on data
        
        # 6. Generate risk report
        report = self.explorer.generate_risk_report("INTEGRATION_TEST")
        self.assertIn("INTEGRATION_TEST", report)
        
        # 7. Test data integration
        aggregated_data = self.integration.aggregate_entity_data("INTEGRATION_TEST")
        self.assertIn('entity_id', aggregated_data)
        
        # 8. Test entity resolution
        relationships = self.resolution_engine.get_entity_relationships("INTEGRATION_TEST")
        self.assertIn('entity_id', relationships)
        
        # Verify all components work together
        self.assertTrue(True)  # If we get here, integration test passed


def run_swap_explorer_tests():
    """Run all swap explorer tests"""
    print("🧪 Running Swap Explorer Tests")
    print("=" * 50)
    
    if not SWAP_EXPLORER_AVAILABLE:
        print("❌ Swap Explorer modules not available - skipping tests")
        return False
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestSwapExplorer,
        TestSwapDataIntegration,
        TestEntityResolutionEngine,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success


if __name__ == "__main__":
    success = run_swap_explorer_tests()
    sys.exit(0 if success else 1)
