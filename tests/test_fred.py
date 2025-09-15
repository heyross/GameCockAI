"""Test cases for FRED API integration."""
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, ANY
import pandas as pd
import numpy as np
from src.data_sources.fred import FREDClient, download_fred_swap_data, logger

# Disable logging during tests
logger.disabled = True

class TestFREDClient(unittest.TestCase):
    """Test cases for FREDClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        os.environ["FRED_API_KEY"] = self.api_key
        
        # Initialize the client
        self.client = FREDClient(api_key=self.api_key)
        
    def test_initialization(self):
        """Test FRED client initialization."""
        # Verify client was created
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.api_key, self.api_key)
    
    def test_download_swap_data(self):
        """Test downloading swap data."""
        # Mock the client methods directly on the instance
        with patch.object(self.client, 'get_available_series') as mock_series, \
             patch.object(self.client, 'get_swap_rates') as mock_rates:
            
            # Setup mocks
            mock_series.return_value = [
                {'id': 'DGS10', 'title': '10-Year Treasury'},
                {'id': 'FEDFUNDS', 'title': 'Fed Funds Rate'}
            ]

            # Create test data
            dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
            mock_rates.return_value = pd.DataFrame({
                'date': dates,
                'value': [3.5 + 0.1 * i for i in range(len(dates))]
            })

            # Run test
            with patch('pandas.DataFrame.to_csv') as mock_to_csv, \
                 patch('os.makedirs') as mock_makedirs:
                result = download_fred_swap_data(days=30)

                # Verify the function returns a list with file paths
                self.assertIsInstance(result, list)
                # Should have exactly 2 entries: one for each series
                self.assertEqual(len(result), 2)
                # Check that we have file paths
                for filepath in result:
                    self.assertIsInstance(filepath, str)

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
        series = self.client.get_available_series()
        self.assertIsInstance(series, list)
        self.assertGreater(len(series), 0)
        self.assertIn('id', series[0])
        self.assertIn('title', series[0])
    
    def test_get_swap_rates(self):
        """Test getting swap rates."""
        rates = self.client.get_swap_rates('SWAPRATE')
        self.assertIsInstance(rates, pd.DataFrame)
        self.assertGreater(len(rates), 0)
        self.assertIn('date', rates.columns)
        self.assertIn('value', rates.columns)
    
    def test_get_swap_rate_summary(self):
        """Test getting swap rate summary."""
        summary = self.client.get_swap_rate_summary()
        self.assertIsInstance(summary, dict)
        self.assertGreater(len(summary), 0)
        
        expected_fields = ['current_rate', 'avg_30d', 'avg_90d', 'volatility']
        for field in expected_fields:
            self.assertIn(field, summary)

if __name__ == "__main__":
    unittest.main()
