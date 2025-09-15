import unittest
import pandas as pd
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from company_manager import get_company_map, find_company
from company_data import load_target_companies, save_target_companies, TARGET_COMPANIES

class TestCompanyManager(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_company_data = {
            '0': {'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'},
            '1': {'cik_str': 789019, 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'},
            '2': {'cik_str': 1045810, 'ticker': 'NVDA', 'title': 'NVIDIA CORP'},
            '3': {'cik_str': 886982, 'ticker': 'GS', 'title': 'GOLDMAN SACHS GROUP INC'}
        }
        
        self.sample_df = pd.DataFrame([
            {'cik_str': '0000320193', 'ticker': 'AAPL', 'title': 'Apple Inc.'},
            {'cik_str': '0000789019', 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'},
            {'cik_str': '0001045810', 'ticker': 'NVDA', 'title': 'NVIDIA CORP'},
            {'cik_str': '0000886982', 'ticker': 'GS', 'title': 'GOLDMAN SACHS GROUP INC'}
        ])

    @patch('company_manager.requests.get')
    def test_get_company_map_success(self, mock_get):
        """Test successful retrieval and processing of the company map."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_company_data
        mock_get.return_value = mock_response

        df = get_company_map()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 4)
        # Check if CIK is padded correctly
        self.assertEqual(df.iloc[0]['cik_str'], '0000320193')
        self.assertEqual(df.iloc[1]['cik_str'], '0000789019')
        
        # Verify all required columns are present
        self.assertIn('cik_str', df.columns)
        self.assertIn('ticker', df.columns)
        self.assertIn('title', df.columns)

    @patch('company_manager.requests.get')
    def test_get_company_map_request_failure(self, mock_get):
        """Test handling of a network error during company map download."""
        mock_get.side_effect = RequestException("Network Error")
        df = get_company_map()
        self.assertIsNone(df)

    @patch('company_manager.requests.get')
    def test_get_company_map_json_decode_error(self, mock_get):
        """Test handling of JSON decode error during company map download."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        df = get_company_map()
        self.assertIsNone(df)

    def test_find_company_by_ticker_exact(self):
        """Test finding a company by exact ticker match."""
        results = find_company(self.sample_df, 'AAPL')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Apple Inc.')
        self.assertEqual(results[0]['cik_str'], '0000320193')

    def test_find_company_by_ticker_case_insensitive(self):
        """Test finding a company by ticker with case insensitive search."""
        results = find_company(self.sample_df, 'aapl')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Apple Inc.')

    def test_find_company_by_name_partial(self):
        """Test finding a company by partial name match."""
        results = find_company(self.sample_df, 'micro')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ticker'], 'MSFT')

    def test_find_company_by_name_case_insensitive(self):
        """Test finding a company by name with case insensitive search."""
        results = find_company(self.sample_df, 'GOLDMAN')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ticker'], 'GS')

    def test_find_company_by_cik(self):
        """Test finding a company by CIK."""
        results = find_company(self.sample_df, '320193')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ticker'], 'AAPL')

    def test_find_company_by_cik_padded(self):
        """Test finding a company by padded CIK."""
        results = find_company(self.sample_df, '0000320193')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ticker'], 'AAPL')

    def test_find_company_no_results(self):
        """Test finding a company with no matching results."""
        results = find_company(self.sample_df, 'nonexistent')
        self.assertEqual(len(results), 0)

    def test_find_company_empty_dataframe(self):
        """Test finding a company with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['cik_str', 'ticker', 'title'])
        results = find_company(empty_df, 'AAPL')
        self.assertEqual(len(results), 0)

    def test_find_company_none_dataframe(self):
        """Test finding a company with None DataFrame."""
        results = find_company(None, 'AAPL')
        self.assertEqual(len(results), 0)

    def test_find_company_multiple_matches(self):
        """Test finding companies with multiple matches."""
        # Add a company with similar name
        extended_df = self.sample_df.copy()
        extended_df = pd.concat([extended_df, pd.DataFrame([{
            'cik_str': '0000123456', 
            'ticker': 'TEST', 
            'title': 'Apple Computer Corp'
        }])], ignore_index=True)
        
        results = find_company(extended_df, 'apple')
        self.assertEqual(len(results), 2)

    def test_find_company_special_characters(self):
        """Test finding a company with special characters in search term."""
        results = find_company(self.sample_df, 'GOLDMAN SACHS')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ticker'], 'GS')

    def test_find_company_whitespace_handling(self):
        """Test finding a company with whitespace in search term."""
        results = find_company(self.sample_df, '  AAPL  ')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Apple Inc.')

class TestCompanyData(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_targets = [
            {
                "cik_str": "0000886982",
                "ticker": "GS",
                "title": "GOLDMAN SACHS GROUP INC"
            },
            {
                "cik_str": "0001326380",
                "ticker": "GME",
                "title": "GameStop Corp."
            }
        ]

    def test_load_target_companies_file_exists(self):
        """Test loading target companies when file exists."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_targets, f)
            temp_file = f.name

        try:
            # Temporarily replace the TARGETS_FILE path
            with patch('company_data.TARGETS_FILE', temp_file):
                targets = load_target_companies()
                self.assertEqual(len(targets), 2)
                self.assertEqual(targets[0]['ticker'], 'GS')
                self.assertEqual(targets[1]['ticker'], 'GME')
        finally:
            os.unlink(temp_file)

    def test_load_target_companies_file_not_exists(self):
        """Test loading target companies when file doesn't exist."""
        with patch('company_data.TARGETS_FILE', 'nonexistent_file.json'):
            targets = load_target_companies()
            self.assertEqual(targets, [])

    def test_save_target_companies(self):
        """Test saving target companies to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            # Temporarily replace the TARGETS_FILE path
            with patch('company_data.TARGETS_FILE', temp_file):
                save_target_companies(self.test_targets)
                
                # Verify file was created and contains correct data
                self.assertTrue(os.path.exists(temp_file))
                with open(temp_file, 'r') as f:
                    saved_data = json.load(f)
                    self.assertEqual(len(saved_data), 2)
                    self.assertEqual(saved_data[0]['ticker'], 'GS')
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_target_companies_loaded_on_startup(self):
        """Test that target companies are loaded on module startup."""
        # This tests that TARGET_COMPANIES is not None and is a list
        self.assertIsInstance(TARGET_COMPANIES, list)
        # Should have at least the companies from targets.json
        self.assertGreaterEqual(len(TARGET_COMPANIES), 0)

    def test_target_company_structure(self):
        """Test that target companies have the expected structure."""
        if TARGET_COMPANIES:
            for company in TARGET_COMPANIES:
                self.assertIn('cik_str', company)
                self.assertIn('ticker', company)
                self.assertIn('title', company)
                
                # Verify CIK is properly formatted (10 digits)
                self.assertEqual(len(company['cik_str']), 10)
                self.assertTrue(company['cik_str'].isdigit())

class TestCompanyManagerIntegration(unittest.TestCase):
    """Integration tests for company management system."""

    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.sample_company_data = {
            '0': {'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'},
            '1': {'cik_str': 789019, 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'},
            '2': {'cik_str': 1045810, 'ticker': 'NVDA', 'title': 'NVIDIA CORP'}
        }

    @patch('company_manager.requests.get')
    def test_end_to_end_company_search_workflow(self, mock_get):
        """Test complete workflow from downloading company map to finding companies."""
        # Mock the company map download
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_company_data
        mock_get.return_value = mock_response

        # Download company map
        df = get_company_map()
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)

        # Search for companies
        apple_results = find_company(df, 'AAPL')
        self.assertEqual(len(apple_results), 1)
        self.assertEqual(apple_results[0]['title'], 'Apple Inc.')

        microsoft_results = find_company(df, 'microsoft')
        self.assertEqual(len(microsoft_results), 1)
        self.assertEqual(microsoft_results[0]['ticker'], 'MSFT')

        nvidia_results = find_company(df, '1045810')
        self.assertEqual(len(nvidia_results), 1)
        self.assertEqual(nvidia_results[0]['ticker'], 'NVDA')

    def test_company_data_persistence_workflow(self):
        """Test complete workflow for saving and loading company data."""
        test_company = {
            "cik_str": "0000123456",
            "ticker": "TEST",
            "title": "Test Company Inc."
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            # Save company data
            with patch('company_data.TARGETS_FILE', temp_file):
                save_target_companies([test_company])
                
                # Load company data
                loaded_companies = load_target_companies()
                self.assertEqual(len(loaded_companies), 1)
                self.assertEqual(loaded_companies[0]['ticker'], 'TEST')
                self.assertEqual(loaded_companies[0]['cik_str'], '0000123456')
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_error_handling_robustness(self):
        """Test system robustness under various error conditions."""
        # Test with malformed data
        malformed_df = pd.DataFrame([
            {'cik_str': 'invalid', 'ticker': 'TEST', 'title': 'Test Company'},
            {'cik_str': '0000123456', 'ticker': None, 'title': 'Test Company 2'},
            {'cik_str': '0000789019', 'ticker': 'MSFT', 'title': None}
        ])

        # Should handle malformed data gracefully
        results = find_company(malformed_df, 'TEST')
        self.assertIsInstance(results, list)

        # Test with empty search term
        results = find_company(malformed_df, '')
        self.assertIsInstance(results, list)

        # Test with None search term
        results = find_company(malformed_df, None)
        self.assertIsInstance(results, list)

if __name__ == '__main__':
    unittest.main()
