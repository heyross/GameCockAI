import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from company_manager import get_company_map, find_company

class TestCompanyManager(unittest.TestCase):

    @patch('company_manager.requests.get')
    def test_get_company_map_success(self, mock_get):
        """Test successful retrieval and processing of the company map."""
        # Mock data similar to the SEC's JSON structure
        mock_data = [
            {'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'},
            {'cik_str': 789019, 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'}
        ]
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        df = get_company_map()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        # Check if CIK is padded correctly
        self.assertEqual(df.iloc[0]['cik_str'], '0000320193')

    @patch('company_manager.requests.get')
    def test_get_company_map_request_failure(self, mock_get):
        """Test handling of a network error during company map download."""
        mock_get.side_effect = RequestException("Network Error")
        df = get_company_map()
        self.assertIsNone(df)

    @patch('company_manager.requests.get')
    def test_find_company(self, mock_get):
        """Test finding a company by ticker and name."""
        mock_data = [
            {'cik_str': '320193', 'ticker': 'AAPL', 'title': 'Apple Inc.'},
            {'cik_str': '789019', 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'},
            {'cik_str': '1045810', 'ticker': 'NVDA', 'title': 'NVIDIA CORP'}
        ]
        # Create a DataFrame from the mock data
        df = pd.DataFrame(mock_data)

        # Test search by ticker (case-insensitive)
        results_ticker = find_company(df, 'aapl')
        self.assertEqual(len(results_ticker), 1)
        self.assertEqual(results_ticker[0]['title'], 'Apple Inc.')

        # Test search by name (partial, case-insensitive)
        results_name = find_company(df, 'micro')
        self.assertEqual(len(results_name), 1)
        self.assertEqual(results_name[0]['ticker'], 'MSFT')

        # Test no results found
        results_none = find_company(df, 'nonexistent')
        self.assertEqual(len(results_none), 0)

if __name__ == '__main__':
    unittest.main()
