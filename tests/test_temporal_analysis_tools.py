"""
Comprehensive tests for Temporal Analysis Tools
Tests risk evolution, management view analysis, and comparative analysis.
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Add GameCockAI directory to path
gamecock_dir = os.path.dirname(current_dir)
if gamecock_dir not in sys.path:
    sys.path.insert(0, gamecock_dir)

try:
    from temporal_analysis_tools import (
        TemporalAnalysisEngine,
        analyze_risk_evolution,
        analyze_management_view_evolution,
        compare_company_risks,
        analyze_company_events
    )
    from database import SessionLocal, Sec10KDocument, Sec8KItem, Sec10KSubmission, Sec8KSubmission
    from test_base import BaseIntegrationTest
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False

@unittest.skipUnless(IMPORTS_AVAILABLE, "Required imports not available")
class TestTemporalAnalysisEngine(unittest.TestCase):
    """Test suite for TemporalAnalysisEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.engine = TemporalAnalysisEngine(db_session=self.mock_db)
        
        # Sample test data
        self.sample_cik = "0001234567"
        self.sample_years = [2020, 2021, 2022, 2023, 2024]
        
        # Mock database query results
        self.mock_risk_sections = [
            Mock(
                accession_number="0001234567-20-000001",
                section="risk_factors",
                content="Risk factors for 2020",
                word_count=500
            ),
            Mock(
                accession_number="0001234567-21-000001",
                section="risk_factors", 
                content="Risk factors for 2021",
                word_count=600
            ),
            Mock(
                accession_number="0001234567-22-000001",
                section="risk_factors",
                content="Risk factors for 2022",
                word_count=700
            )
        ]
        
        self.mock_mdna_sections = [
            Mock(
                accession_number="0001234567-20-000001",
                section="mdna",
                content="MD&A for 2020",
                word_count=800
            ),
            Mock(
                accession_number="0001234567-21-000001",
                section="mdna",
                content="MD&A for 2021", 
                word_count=900
            )
        ]
        
        self.mock_8k_items = [
            Mock(
                accession_number="0001234567-23-000001",
                item_number="1.01",
                item_title="Entry into Material Definitive Agreement",
                content="Agreement content"
            ),
            Mock(
                accession_number="0001234567-23-000002",
                item_number="2.02",
                item_title="Results of Operations and Financial Condition",
                content="Results content"
            )
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self.engine, 'db') and hasattr(self.engine.db, 'close'):
            self.engine.db.close()
    
    def test_init(self):
        """Test engine initialization."""
        engine = TemporalAnalysisEngine()
        self.assertIsNotNone(engine.db)
        
        # Test with custom database session
        mock_db = Mock()
        engine = TemporalAnalysisEngine(db_session=mock_db)
        self.assertEqual(engine.db, mock_db)
    
    def test_analyze_risk_evolution_success(self):
        """Test successful risk evolution analysis."""
        # Mock database queries
        self.mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = self.mock_risk_sections
        
        # Mock filing date queries
        def mock_filing_date_query(accession_number):
            mock_result = Mock()
            if "20-000001" in accession_number:
                mock_result.scalar.return_value = datetime(2020, 3, 15)
            elif "21-000001" in accession_number:
                mock_result.scalar.return_value = datetime(2021, 3, 15)
            elif "22-000001" in accession_number:
                mock_result.scalar.return_value = datetime(2022, 3, 15)
            return mock_result
        
        self.mock_db.query.return_value.filter.return_value.scalar.side_effect = [
            datetime(2020, 3, 15),
            datetime(2021, 3, 15), 
            datetime(2022, 3, 15)
        ]
        
        result = self.engine.analyze_risk_evolution(self.sample_cik, [2020, 2021, 2022])
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('company_cik', result)
        self.assertIn('analysis_period', result)
        self.assertIn('total_filings', result)
        self.assertIn('yearly_breakdown', result)
        self.assertIn('summary', result)
        
        # Verify data
        self.assertEqual(result['company_cik'], self.sample_cik)
        self.assertEqual(result['total_filings'], 3)
        self.assertIn('2020', result['yearly_breakdown'])
        self.assertIn('2021', result['yearly_breakdown'])
        self.assertIn('2022', result['yearly_breakdown'])
    
    def test_analyze_risk_evolution_no_data(self):
        """Test risk evolution analysis with no data."""
        # Mock empty database query
        self.mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        result = self.engine.analyze_risk_evolution(self.sample_cik, [2020, 2021, 2022])
        
        # Should return error message
        self.assertIn('error', result)
        self.assertIn('No risk factor data found', result['error'])
    
    def test_analyze_risk_evolution_with_error(self):
        """Test risk evolution analysis with database error."""
        # Mock database error
        self.mock_db.query.side_effect = Exception("Database connection error")
        
        result = self.engine.analyze_risk_evolution(self.sample_cik, [2020, 2021, 2022])
        
        # Should return error message
        self.assertIn('error', result)
        self.assertIn('Database connection error', result['error'])
    
    def test_analyze_management_view_evolution_success(self):
        """Test successful management view evolution analysis."""
        # Mock database queries
        self.mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = self.mock_mdna_sections
        
        # Mock filing date queries
        self.mock_db.query.return_value.filter.return_value.scalar.side_effect = [
            datetime(2020, 3, 15),
            datetime(2021, 3, 15)
        ]
        
        result = self.engine.analyze_management_view_evolution(self.sample_cik, [2020, 2021])
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('company_cik', result)
        self.assertIn('analysis_period', result)
        self.assertIn('total_filings', result)
        self.assertIn('yearly_breakdown', result)
        self.assertIn('summary', result)
        
        # Verify data
        self.assertEqual(result['company_cik'], self.sample_cik)
        self.assertEqual(result['total_filings'], 2)
        self.assertIn('2020', result['yearly_breakdown'])
        self.assertIn('2021', result['yearly_breakdown'])
    
    def test_compare_risk_factors_across_companies(self):
        """Test comparing risk factors across multiple companies."""
        company_ciks = ["0001234567", "0000987654"]
        year = 2023
        
        # Mock database queries for each company
        def mock_query_side_effect(*args, **kwargs):
            mock_result = Mock()
            if "0001234567" in str(args):
                mock_result.all.return_value = [
                    Mock(section="risk_factors", word_count=500, content="Company 1 risks")
                ]
            else:
                mock_result.all.return_value = [
                    Mock(section="risk_factors", word_count=300, content="Company 2 risks")
                ]
            return mock_result
        
        self.mock_db.query.return_value.join.return_value.filter.side_effect = mock_query_side_effect
        
        result = self.engine.compare_risk_factors_across_companies(company_ciks, year)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('comparison_year', result)
        self.assertIn('companies_analyzed', result)
        self.assertIn('comparison_data', result)
        self.assertIn('summary', result)
        
        # Verify data
        self.assertEqual(result['comparison_year'], year)
        self.assertEqual(result['companies_analyzed'], 2)
        self.assertIn('0001234567', result['comparison_data'])
        self.assertIn('0000987654', result['comparison_data'])
    
    def test_analyze_8k_event_patterns(self):
        """Test 8-K event pattern analysis."""
        # Mock database queries
        self.mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = self.mock_8k_items
        
        result = self.engine.analyze_8k_event_patterns(self.sample_cik, 12)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('company_cik', result)
        self.assertIn('analysis_period_months', result)
        self.assertIn('total_events', result)
        self.assertIn('item_breakdown', result)
        self.assertIn('summary', result)
        
        # Verify data
        self.assertEqual(result['company_cik'], self.sample_cik)
        self.assertEqual(result['analysis_period_months'], 12)
        self.assertEqual(result['total_events'], 2)
        self.assertIn('1.01', result['item_breakdown'])
        self.assertIn('2.02', result['item_breakdown'])
    
    def test_analyze_8k_event_patterns_no_data(self):
        """Test 8-K event analysis with no data."""
        # Mock empty database query
        self.mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        result = self.engine.analyze_8k_event_patterns(self.sample_cik, 12)
        
        # Should return error message
        self.assertIn('error', result)
        self.assertIn('No 8-K data found', result['error'])
    
    def test_generate_risk_evolution_summary(self):
        """Test risk evolution summary generation."""
        risk_analysis = {
            2020: {'filing_count': 1, 'total_words': 500, 'content_samples': [], 'filing_dates': []},
            2021: {'filing_count': 1, 'total_words': 600, 'content_samples': [], 'filing_dates': []},
            2022: {'filing_count': 1, 'total_words': 700, 'content_samples': [], 'filing_dates': []}
        }
        
        summary = self.engine._generate_risk_evolution_summary(risk_analysis)
        
        # Should generate meaningful summary
        self.assertIsInstance(summary, str)
        self.assertIn('increased', summary)  # Word count increased
        self.assertIn('2020', summary)
        self.assertIn('2022', summary)
        self.assertIn('500', summary)
        self.assertIn('700', summary)
    
    def test_generate_mdna_evolution_summary(self):
        """Test MD&A evolution summary generation."""
        mdna_analysis = {
            2020: {'filing_count': 1, 'total_words': 800, 'content_samples': [], 'filing_dates': []},
            2021: {'filing_count': 1, 'total_words': 900, 'content_samples': [], 'filing_dates': []}
        }
        
        summary = self.engine._generate_mdna_evolution_summary(mdna_analysis)
        
        # Should generate meaningful summary
        self.assertIsInstance(summary, str)
        self.assertIn('increased', summary)  # Word count increased
        self.assertIn('2020', summary)
        self.assertIn('2021', summary)
        self.assertIn('800', summary)
        self.assertIn('900', summary)
    
    def test_generate_comparative_risk_summary(self):
        """Test comparative risk summary generation."""
        comparison_data = {
            '0001234567': {'filing_count': 2, 'total_words': 1000, 'content_samples': []},
            '0000987654': {'filing_count': 1, 'total_words': 500, 'content_samples': []}
        }
        
        summary = self.engine._generate_comparative_risk_summary(comparison_data)
        
        # Should generate meaningful summary
        self.assertIsInstance(summary, str)
        self.assertIn('2 companies', summary)
        self.assertIn('0001234567', summary)  # Company with most words
        self.assertIn('1000', summary)
        self.assertIn('1.5', summary)  # Average filings per company
    
    def test_generate_8k_pattern_summary(self):
        """Test 8-K pattern summary generation."""
        item_analysis = {
            '1.01': {'count': 3, 'title': 'Entry into Agreement', 'recent_examples': []},
            '2.02': {'count': 2, 'title': 'Results', 'recent_examples': []},
            '5.02': {'count': 1, 'title': 'Executive Departure', 'recent_examples': []}
        }
        
        summary = self.engine._generate_8k_pattern_summary(item_analysis)
        
        # Should generate meaningful summary
        self.assertIsInstance(summary, str)
        self.assertIn('6', summary)  # Total events
        self.assertIn('1.01', summary)  # Most common
        self.assertIn('3', summary)  # Count of most common
        self.assertIn('3', summary)  # Unique event types


class TestTemporalAnalysisConvenienceFunctions(unittest.TestCase):
    """Test suite for convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_cik = "0001234567"
        self.sample_years = [2020, 2021, 2022]
    
    @patch('temporal_analysis_tools.TemporalAnalysisEngine')
    def test_analyze_risk_evolution_function(self, mock_engine_class):
        """Test analyze_risk_evolution convenience function."""
        # Mock engine instance
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        
        # Mock analysis result
        mock_result = {
            'company_cik': self.sample_cik,
            'analysis_period': '2020-2022',
            'total_filings': 3,
            'yearly_breakdown': {
                2020: {'filing_count': 1, 'total_words': 500, 'content_samples': [], 'filing_dates': []},
                2021: {'filing_count': 1, 'total_words': 600, 'content_samples': [], 'filing_dates': []},
                2022: {'filing_count': 1, 'total_words': 700, 'content_samples': [], 'filing_dates': []}
            },
            'summary': 'Risk discussion increased from 2020 to 2022'
        }
        mock_engine.analyze_risk_evolution.return_value = mock_result
        
        result = analyze_risk_evolution(self.sample_cik, self.sample_years)
        
        # Verify function was called correctly
        mock_engine.analyze_risk_evolution.assert_called_once_with(self.sample_cik, self.sample_years)
        
        # Verify result formatting
        self.assertIsInstance(result, str)
        self.assertIn('Risk Evolution Analysis', result)
        self.assertIn(self.sample_cik, result)
        self.assertIn('2020-2022', result)
        self.assertIn('increased from 2020 to 2022', result)
    
    @patch('temporal_analysis_tools.TemporalAnalysisEngine')
    def test_analyze_risk_evolution_with_error(self, mock_engine_class):
        """Test analyze_risk_evolution with error."""
        # Mock engine instance
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        
        # Mock error result
        mock_engine.analyze_risk_evolution.return_value = {'error': 'Database connection failed'}
        
        result = analyze_risk_evolution(self.sample_cik, self.sample_years)
        
        # Should return error message
        self.assertIn('Error:', result)
        self.assertIn('Database connection failed', result)
    
    @patch('temporal_analysis_tools.TemporalAnalysisEngine')
    def test_analyze_management_view_evolution_function(self, mock_engine_class):
        """Test analyze_management_view_evolution convenience function."""
        # Mock engine instance
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        
        # Mock analysis result
        mock_result = {
            'company_cik': self.sample_cik,
            'analysis_period': '2020-2022',
            'total_filings': 2,
            'yearly_breakdown': {
                2020: {'filing_count': 1, 'total_words': 800, 'content_samples': [], 'filing_dates': []},
                2021: {'filing_count': 1, 'total_words': 900, 'content_samples': [], 'filing_dates': []}
            },
            'summary': 'Management discussion increased from 2020 to 2021'
        }
        mock_engine.analyze_management_view_evolution.return_value = mock_result
        
        result = analyze_management_view_evolution(self.sample_cik, self.sample_years)
        
        # Verify function was called correctly
        mock_engine.analyze_management_view_evolution.assert_called_once_with(self.sample_cik, self.sample_years)
        
        # Verify result formatting
        self.assertIsInstance(result, str)
        self.assertIn('Management View Evolution Analysis', result)
        self.assertIn(self.sample_cik, result)
        self.assertIn('increased from 2020 to 2021', result)
    
    @patch('temporal_analysis_tools.TemporalAnalysisEngine')
    def test_compare_company_risks_function(self, mock_engine_class):
        """Test compare_company_risks convenience function."""
        # Mock engine instance
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        
        # Mock comparison result
        mock_result = {
            'comparison_year': 2023,
            'companies_analyzed': 2,
            'comparison_data': {
                '0001234567': {'filing_count': 2, 'total_words': 1000, 'content_samples': []},
                '0000987654': {'filing_count': 1, 'total_words': 500, 'content_samples': []}
            },
            'summary': 'Company 0001234567 has most comprehensive risk discussion'
        }
        mock_engine.compare_risk_factors_across_companies.return_value = mock_result
        
        company_ciks = ['0001234567', '0000987654']
        year = 2023
        
        result = compare_company_risks(company_ciks, year)
        
        # Verify function was called correctly
        mock_engine.compare_risk_factors_across_companies.assert_called_once_with(company_ciks, year)
        
        # Verify result formatting
        self.assertIsInstance(result, str)
        self.assertIn('Comparative Risk Analysis', result)
        self.assertIn('2023', result)
        self.assertIn('0001234567', result)
        self.assertIn('0000987654', result)
    
    @patch('temporal_analysis_tools.TemporalAnalysisEngine')
    def test_analyze_company_events_function(self, mock_engine_class):
        """Test analyze_company_events convenience function."""
        # Mock engine instance
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        
        # Mock events result
        mock_result = {
            'company_cik': self.sample_cik,
            'analysis_period_months': 12,
            'total_events': 5,
            'item_breakdown': {
                '1.01': {'count': 3, 'title': 'Entry into Agreement', 'recent_examples': []},
                '2.02': {'count': 2, 'title': 'Results', 'recent_examples': []}
            },
            'summary': 'Total 8-K events: 5. Most common: 1.01 with 3 occurrences'
        }
        mock_engine.analyze_8k_event_patterns.return_value = mock_result
        
        result = analyze_company_events(self.sample_cik, 12)
        
        # Verify function was called correctly
        mock_engine.analyze_8k_event_patterns.assert_called_once_with(self.sample_cik, 12)
        
        # Verify result formatting
        self.assertIsInstance(result, str)
        self.assertIn('8-K Event Analysis', result)
        self.assertIn(self.sample_cik, result)
        self.assertIn('12 months', result)
        self.assertIn('1.01', result)
        self.assertIn('3 events', result)


class TestTemporalAnalysisIntegration(BaseIntegrationTest):
    """Integration tests for temporal analysis with real database."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        super().setUp()
        self.engine = TemporalAnalysisEngine(db_session=SessionLocal())
        self.test_cik = "0001234567"
    
    def test_real_database_risk_analysis(self):
        """Test risk analysis with real database operations."""
        # Create test data
        test_accession = "0001234567-23-000001"
        
        # Create test submission
        submission = Sec10KSubmission(
            accession_number=test_accession,
            cik=self.test_cik,
            company_name="Test Company",
            form_type="10-K",
            filing_date=datetime(2023, 3, 15),
            period_of_report=datetime(2022, 12, 31)
        )
        
        # Create test risk section
        risk_doc = Sec10KDocument(
            accession_number=test_accession,
            section="risk_factors",
            sequence=1,
            content="This is a comprehensive risk factors section that discusses various business risks and uncertainties.",
            word_count=25
        )
        
        try:
            # Save test data
            self.db.add(submission)
            self.db.add(risk_doc)
            self.db.commit()
            
            # Test analysis
            result = self.engine.analyze_risk_evolution(self.test_cik, [2023])
            
            # Verify result
            self.assertIsInstance(result, dict)
            self.assertNotIn('error', result)
            self.assertEqual(result['company_cik'], self.test_cik)
            self.assertEqual(result['total_filings'], 1)
            self.assertIn('2023', result['yearly_breakdown'])
            
        except Exception as e:
            self.fail(f"Integration test failed: {e}")
        finally:
            # Clean up test data
            try:
                self.db.query(Sec10KDocument).filter(
                    Sec10KDocument.accession_number == test_accession
                ).delete()
                self.db.query(Sec10KSubmission).filter(
                    Sec10KSubmission.accession_number == test_accession
                ).delete()
                self.db.commit()
            except:
                pass


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add unit tests
    test_suite.addTest(unittest.makeSuite(TestTemporalAnalysisEngine))
    test_suite.addTest(unittest.makeSuite(TestTemporalAnalysisConvenienceFunctions))
    
    # Add integration tests
    test_suite.addTest(unittest.makeSuite(TestTemporalAnalysisIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
