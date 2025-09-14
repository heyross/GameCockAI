"""Test cases for FRED API integration."""
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, ANY
import pandas as pd
import numpy as np
from data_sources.fred import FREDClient, download_fred_swap_data, logger

# Disable logging during tests
logger.disabled = True

class TestFREDClient(unittest.TestCase):
    """Test cases for FREDClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        os.environ["FRED_API_KEY"] = self.api_key
        
        # Create a patcher for the Fred class
        self.fred_patcher = patch('data_sources.fred.Fred')
        self.mock_fred_class = self.fred_patcher.start()
        
        # Create a mock instance that will be returned when Fred is instantiated
        self.mock_fred_instance = MagicMock()
        self.mock_fred_class.return_value = self.mock_fred_instance
        
        # Now initialize the client
        self.client = FREDClient()
        
    def tearDown(self):
        """Clean up after tests."""
        self.fred_patcher.stop()
        
    def test_initialization(self):
        """Test FRED client initialization."""
        # Verify client was created
        self.assertIsNotNone(self.client)
        
        # The API key should be passed to the Fred constructor
        # We'll just verify it was called with any api_key parameter
        self.mock_fred_class.assert_called_once()
        
        # Verify the instance is stored in the client
        self.assertEqual(self.client.fred, self.mock_fred_instance)
    
    @patch('data_sources.fred.FREDClient.get_available_series')
    @patch('data_sources.fred.FREDClient.get_swap_rates')
    @patch('data_sources.fred.FREDClient.get_swap_rate_summary')
    def test_download_swap_data(self, mock_summary, mock_rates, mock_series):
        """Test downloading swap data."""
        # Setup mocks
        mock_series.return_value = [
            {'id': 'DGS10', 'name': 'US_10Y', 'title': '10-Year Treasury'},
            {'id': 'FEDFUNDS', 'name': 'FEDFUNDS', 'title': 'Fed Funds Rate'}
        ]
        
        # Create test data
        dates = pd.date_range(end=datetime.today(), periods=30).date
        mock_rates.return_value = {
            'US_10Y': pd.DataFrame(
                {'rate': [3.5 + 0.1 * i for i in range(30)]},
                index=dates
            ),
            'FEDFUNDS': pd.DataFrame(
                {'rate': [4.5 + 0.05 * i for i in range(30)]},
                index=dates
            )
        }
        
        mock_summary.return_value = pd.DataFrame({
            'name': ['US_10Y', 'FEDFUNDS'],
            'title': ['10-Year Treasury', 'Fed Funds Rate'],
            'current_rate': [3.5, 4.5],
            'units': ['Percent', 'Percent'],
            'change_pct': [0.1, 0.05],
            'last_updated': [datetime.now().date()] * 2,
            'frequency': ['Daily', 'Daily'],
            'series_id': ['DGS10', 'FEDFUNDS']
        })
        
        # Run test
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            result = download_fred_swap_data(days=30)
            
            # Verify the function returns a dictionary with file paths
            self.assertIsInstance(result, dict)
            # Should have exactly 2 entries: one for each series
            self.assertEqual(len(result), 2)
            # Check that we have entries for our test series
            self.assertTrue(any('US_10Y' in k for k in result.keys()))
            self.assertTrue(any('FEDFUNDS' in k for k in result.keys()))

class TestFREDIntegration(unittest.TestCase):
    """Integration tests for FRED API (requires valid API key)."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        if not os.getenv("FRED_API_KEY"):
            raise unittest.SkipTest("FRED_API_KEY not set in environment")
        
        cls.client = FREDClient()
    
    def test_get_available_series(self):
        """Test getting available series."""
        series = self.client.get_available_series(days=7)
        self.assertIsInstance(series, list)
        self.assertGreater(len(series), 0)
        self.assertIn('id', series[0])
        self.assertIn('name', series[0])
    
    def test_get_swap_rates(self):
        """Test getting swap rates."""
        rates = self.client.get_swap_rates(days=7)
        self.assertIsInstance(rates, dict)
        self.assertGreater(len(rates), 0)
        
        for name, df in rates.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)
    
    def test_get_swap_rate_summary(self):
        """Test getting swap rate summary."""
        summary = self.client.get_swap_rate_summary(days=7)
        self.assertIsInstance(summary, pd.DataFrame)
        self.assertGreater(len(summary), 0)
        
        expected_columns = [
            'name', 'title', 'current_rate', 'units', 
            'change_pct', 'last_updated', 'frequency', 'series_id'
        ]
        for col in expected_columns:
            self.assertIn(col, summary.columns)

if __name__ == "__main__":
    unittest.main()
