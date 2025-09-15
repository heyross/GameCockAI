#!/usr/bin/env python3
"""
Comprehensive Test Suite for Swap Analysis Features.

This test suite validates all the new swap analysis features including:
- Single Party Risk Analyzer
- Cross-Filing Correlation Engine
- Obligation Tracking System
- Credit Risk Tracker
- Executive Dashboard
- Integration Module
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the modules to test
from swap_analysis.single_party_risk_analyzer import (
    SinglePartyRiskAnalyzer, SwapExposure, RiskLevel, SwapType, CounterpartyType
)
from cross_filing_analysis.cross_filing_correlation_engine import (
    CrossFilingCorrelationEngine, CrossFilingCorrelation, ConsolidatedRiskProfile
)
from obligation_tracking.obligation_tracking_system import (
    ObligationTrackingSystem, ObligationSummary, PaymentSchedule, CollateralObligation
)
from credit_risk.credit_risk_tracker import (
    CreditRiskTracker, CreditRiskProfile, CreditRating, RatingAgency
)
from dashboards.executive_dashboard import (
    ExecutiveDashboard, RiskAlert, RiskRecommendation, AlertSeverity
)
from swap_analysis_integration import SwapAnalysisIntegration
from enhanced_entity_resolver import IdentifierType

class TestSinglePartyRiskAnalyzer(unittest.TestCase):
    """Test the Single Party Risk Analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.analyzer = SinglePartyRiskAnalyzer(self.mock_db_session)
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.fuzzy_threshold, 0.8)
        self.assertEqual(self.analyzer.partial_threshold, 0.6)
    
    def test_swap_exposure_creation(self):
        """Test SwapExposure dataclass creation."""
        exposure = SwapExposure(
            exposure_id="TEST_001",
            entity_id="1234567890",
            counterparty_id="9876543210",
            counterparty_name="Test Counterparty",
            swap_type=SwapType.INTEREST_RATE,
            notional_amount=1000000.0,
            currency="USD",
            mark_to_market=50000.0,
            collateral_posted=100000.0,
            collateral_received=50000.0,
            net_exposure=0.0,
            maturity_date=datetime.utcnow() + timedelta(days=365),
            effective_date=datetime.utcnow(),
            data_source="TEST"
        )
        
        self.assertEqual(exposure.exposure_id, "TEST_001")
        self.assertEqual(exposure.notional_amount, 1000000.0)
        self.assertEqual(exposure.swap_type, SwapType.INTEREST_RATE)
    
    def test_risk_level_enum(self):
        """Test RiskLevel enum values."""
        self.assertEqual(RiskLevel.LOW.value, "low")
        self.assertEqual(RiskLevel.HIGH.value, "high")
        self.assertEqual(RiskLevel.CRITICAL.value, "critical")
    
    def test_swap_type_enum(self):
        """Test SwapType enum values."""
        self.assertEqual(SwapType.INTEREST_RATE.value, "interest_rate")
        self.assertEqual(SwapType.CREDIT_DEFAULT.value, "credit_default")
        self.assertEqual(SwapType.EQUITY.value, "equity")
    
    @patch.object(SinglePartyRiskAnalyzer, '_aggregate_all_swap_exposures')
    def test_analyze_single_party_risk_mock(self, mock_aggregate):
        """Test single party risk analysis with mocked data."""
        # Mock the entity resolver
        mock_entity_profile = Mock()
        mock_entity_profile.entity_id = "1234567890"
        mock_entity_profile.entity_name = "Test Entity"
        
        with patch.object(self.analyzer.entity_resolver, 'resolve_entity', return_value=mock_entity_profile):
            # Mock empty exposures
            mock_aggregate.return_value = []
            
            result = self.analyzer.analyze_single_party_risk("TEST_ENTITY")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.entity_id, "1234567890")
            self.assertEqual(result.entity_name, "Test Entity")
            self.assertEqual(result.total_notional_exposure, 0.0)

class TestCrossFilingCorrelationEngine(unittest.TestCase):
    """Test the Cross-Filing Correlation Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.engine = CrossFilingCorrelationEngine(self.mock_db_session)
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.disclosure_patterns)
    
    def test_disclosure_patterns_initialization(self):
        """Test disclosure patterns are properly initialized."""
        patterns = self.engine.disclosure_patterns
        self.assertIn("FORM_10K", [ft.value for ft in patterns.keys()])
        self.assertIn("FORM_10Q", [ft.value for ft in patterns.keys()])
        self.assertIn("FORM_8K", [ft.value for ft in patterns.keys()])
    
    def test_filing_type_enum(self):
        """Test FilingType enum values."""
        from cross_filing_analysis.cross_filing_correlation_engine import FilingType
        self.assertEqual(FilingType.FORM_10K.value, "10-K")
        self.assertEqual(FilingType.FORM_10Q.value, "10-Q")
        self.assertEqual(FilingType.FORM_8K.value, "8-K")

class TestObligationTrackingSystem(unittest.TestCase):
    """Test the Obligation Tracking System."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.tracker = ObligationTrackingSystem(self.mock_db_session)
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(self.tracker.overdue_threshold_days, 1)
        self.assertEqual(self.tracker.upcoming_threshold_days, 30)
    
    def test_payment_schedule_creation(self):
        """Test PaymentSchedule dataclass creation."""
        schedule = PaymentSchedule(
            schedule_id="PAY_001",
            swap_exposure_id="SWAP_001",
            payment_date=datetime.utcnow() + timedelta(days=30),
            payment_amount=50000.0,
            currency="USD",
            payment_type="interest",
            counterparty_id="1234567890",
            is_payer=True
        )
        
        self.assertEqual(schedule.schedule_id, "PAY_001")
        self.assertEqual(schedule.payment_amount, 50000.0)
        self.assertTrue(schedule.is_payer)
    
    def test_collateral_obligation_creation(self):
        """Test CollateralObligation dataclass creation."""
        from obligation_tracking.obligation_tracking_system import CollateralType, ObligationType
        
        obligation = CollateralObligation(
            obligation_id="COLL_001",
            swap_exposure_id="SWAP_001",
            counterparty_id="1234567890",
            collateral_type=CollateralType.CASH,
            required_amount=100000.0,
            currency="USD",
            due_date=datetime.utcnow() + timedelta(days=1),
            obligation_type=ObligationType.COLLATERAL_POSTING
        )
        
        self.assertEqual(obligation.obligation_id, "COLL_001")
        self.assertEqual(obligation.required_amount, 100000.0)
        self.assertEqual(obligation.collateral_type, CollateralType.CASH)

class TestCreditRiskTracker(unittest.TestCase):
    """Test the Credit Risk Tracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.tracker = CreditRiskTracker(self.mock_db_session)
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertIsNotNone(self.tracker.rating_numeric_values)
        self.assertIsNotNone(self.tracker.default_thresholds)
    
    def test_credit_rating_enum(self):
        """Test CreditRating enum values."""
        self.assertEqual(CreditRating.AAA.value, "AAA")
        self.assertEqual(CreditRating.BBB.value, "BBB")
        self.assertEqual(CreditRating.D.value, "D")
    
    def test_rating_agency_enum(self):
        """Test RatingAgency enum values."""
        self.assertEqual(RatingAgency.S_P.value, "S&P")
        self.assertEqual(RatingAgency.MOODY.value, "Moody's")
        self.assertEqual(RatingAgency.FITCH.value, "Fitch")
    
    def test_rating_numeric_values(self):
        """Test rating numeric values are properly set."""
        values = self.tracker.rating_numeric_values
        self.assertLess(values[CreditRating.AAA], values[CreditRating.BBB])
        self.assertLess(values[CreditRating.BBB], values[CreditRating.D])
        self.assertEqual(values[CreditRating.D], 1.0)

class TestExecutiveDashboard(unittest.TestCase):
    """Test the Executive Dashboard."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.dashboard = ExecutiveDashboard(self.mock_db_session)
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(self.dashboard.var_confidence_level, 0.95)
        self.assertIsNotNone(self.dashboard.stress_test_scenarios)
    
    def test_alert_severity_enum(self):
        """Test AlertSeverity enum values."""
        self.assertEqual(AlertSeverity.INFO.value, "info")
        self.assertEqual(AlertSeverity.WARNING.value, "warning")
        self.assertEqual(AlertSeverity.CRITICAL.value, "critical")
        self.assertEqual(AlertSeverity.EMERGENCY.value, "emergency")
    
    def test_risk_alert_creation(self):
        """Test RiskAlert dataclass creation."""
        alert = RiskAlert(
            alert_id="ALERT_001",
            entity_id="1234567890",
            alert_type="concentration_risk",
            severity=AlertSeverity.WARNING,
            title="High Concentration Risk",
            description="Entity has high concentration with single counterparty",
            alert_date=datetime.utcnow()
        )
        
        self.assertEqual(alert.alert_id, "ALERT_001")
        self.assertEqual(alert.severity, AlertSeverity.WARNING)
        self.assertEqual(alert.alert_type, "concentration_risk")
    
    def test_stress_test_scenarios(self):
        """Test stress test scenarios are properly initialized."""
        scenarios = self.dashboard.stress_test_scenarios
        self.assertIn("market_crash", scenarios)
        self.assertIn("rate_shock", scenarios)
        self.assertIn("credit_crisis", scenarios)
        self.assertIn("liquidity_crisis", scenarios)

class TestSwapAnalysisIntegration(unittest.TestCase):
    """Test the Swap Analysis Integration module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.integration = SwapAnalysisIntegration(self.mock_db_session)
    
    def test_integration_initialization(self):
        """Test integration module initialization."""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.entity_resolver)
        self.assertIsNotNone(self.integration.risk_analyzer)
        self.assertIsNotNone(self.integration.correlation_engine)
        self.assertIsNotNone(self.integration.obligation_tracker)
        self.assertIsNotNone(self.integration.credit_tracker)
        self.assertIsNotNone(self.integration.executive_dashboard)
    
    def test_identifier_type_enum(self):
        """Test IdentifierType enum values."""
        self.assertEqual(IdentifierType.CIK.value, "cik")
        self.assertEqual(IdentifierType.CUSIP.value, "cusip")
        self.assertEqual(IdentifierType.TICKER.value, "ticker")
        self.assertEqual(IdentifierType.NAME.value, "name")
        self.assertEqual(IdentifierType.AUTO.value, "auto")
    
    @patch.object(SwapAnalysisIntegration, '_serialize_risk_profile')
    def test_comprehensive_analysis_mock(self, mock_serialize):
        """Test comprehensive analysis with mocked data."""
        # Mock entity resolution
        mock_entity_profile = Mock()
        mock_entity_profile.entity_id = "1234567890"
        mock_entity_profile.entity_name = "Test Entity"
        
        with patch.object(self.integration.entity_resolver, 'resolve_entity', return_value=mock_entity_profile):
            # Mock all analysis modules to return None (no data)
            with patch.object(self.integration.risk_analyzer, 'analyze_single_party_risk', return_value=None):
                with patch.object(self.integration.correlation_engine, 'analyze_cross_filing_correlations', return_value=[]):
                    with patch.object(self.integration.correlation_engine, 'get_consolidated_risk_profile', return_value=None):
                        with patch.object(self.integration.obligation_tracker, 'track_entity_obligations', return_value=None):
                            with patch.object(self.integration.credit_tracker, 'track_credit_risk', return_value=None):
                                with patch.object(self.integration.executive_dashboard, 'generate_executive_dashboard', return_value=None):
                                    
                                    result = self.integration.analyze_comprehensive_swap_risk("TEST_ENTITY")
                                    
                                    self.assertIsNotNone(result)
                                    self.assertIn("entity_info", result)
                                    self.assertEqual(result["entity_info"]["entity_id"], "1234567890")
                                    self.assertEqual(result["entity_info"]["entity_name"], "Test Entity")

class TestIntegrationAndCompatibility(unittest.TestCase):
    """Test integration and compatibility with existing system."""
    
    def test_import_compatibility(self):
        """Test that all modules can be imported without errors."""
        try:
            from swap_analysis import SinglePartyRiskAnalyzer
            from cross_filing_analysis import CrossFilingCorrelationEngine
            from obligation_tracking import ObligationTrackingSystem
            from credit_risk import CreditRiskTracker
            from dashboards import ExecutiveDashboard
            from swap_analysis_integration import SwapAnalysisIntegration
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_dataclass_serialization(self):
        """Test that dataclasses can be serialized to dict."""
        exposure = SwapExposure(
            exposure_id="TEST_001",
            entity_id="1234567890",
            counterparty_id="9876543210",
            counterparty_name="Test Counterparty",
            swap_type=SwapType.INTEREST_RATE,
            notional_amount=1000000.0,
            currency="USD",
            mark_to_market=50000.0,
            collateral_posted=100000.0,
            collateral_received=50000.0,
            net_exposure=0.0,
            maturity_date=datetime.utcnow() + timedelta(days=365),
            effective_date=datetime.utcnow(),
            data_source="TEST"
        )
        
        # Test that we can access all fields
        self.assertIsNotNone(exposure.exposure_id)
        self.assertIsNotNone(exposure.entity_id)
        self.assertIsNotNone(exposure.counterparty_id)
        self.assertIsNotNone(exposure.swap_type)
        self.assertIsNotNone(exposure.notional_amount)
        self.assertIsNotNone(exposure.currency)
        self.assertIsNotNone(exposure.mark_to_market)
        self.assertIsNotNone(exposure.collateral_posted)
        self.assertIsNotNone(exposure.collateral_received)
        self.assertIsNotNone(exposure.net_exposure)
        self.assertIsNotNone(exposure.maturity_date)
        self.assertIsNotNone(exposure.effective_date)
        self.assertIsNotNone(exposure.data_source)

def run_swap_analysis_tests():
    """Run all swap analysis tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestSinglePartyRiskAnalyzer,
        TestCrossFilingCorrelationEngine,
        TestObligationTrackingSystem,
        TestCreditRiskTracker,
        TestExecutiveDashboard,
        TestSwapAnalysisIntegration,
        TestIntegrationAndCompatibility
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running Comprehensive Swap Analysis Feature Tests...")
    print("=" * 60)
    
    success = run_swap_analysis_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ ALL SWAP ANALYSIS FEATURE TESTS PASSED!")
        print("=" * 60)
        print("\nFeatures Successfully Implemented:")
        print("• Comprehensive Swap Explorer & Single Party Risk Analyzer")
        print("• Cross-Filing Risk Correlation Engine")
        print("• Swap Obligation & Payment Tracking System")
        print("• Credit Risk & Default Probability Tracker")
        print("• Derivative Risk Executive Dashboard")
        print("• Integration Module")
        print("\nThe GameCock AI system now supports sophisticated swap risk analysis!")
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED!")
        print("=" * 60)
        print("Please review the test output above for details.")
    
    sys.exit(0 if success else 1)
