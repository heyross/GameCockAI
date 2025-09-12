import unittest
import os
import shutil
from unittest.mock import patch, MagicMock, call
from requests.exceptions import RequestException

# Add the project root to the Python path to allow for absolute imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from downloader import download_file, download_archives

class TestDownloader(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for testing downloads."""
        self.test_dir = "test_temp_downloads"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up the temporary directory after tests."""
        shutil.rmtree(self.test_dir)

    @patch('downloader.requests.get')
    def test_download_file_success(self, mock_get):
        """Test successful download of a single file."""
        # Mock the requests.get call to return a successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b'test', b'data']
        mock_get.return_value = mock_response

        url = "http://example.com/testfile.zip"
        result = download_file(url, self.test_dir)

        self.assertTrue(result)
        # Check that the file was created and contains the correct data
        file_path = os.path.join(self.test_dir, "testfile.zip")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'rb') as f:
            self.assertEqual(f.read(), b'testdata')

    def test_download_file_already_exists(self):
        """Test that an existing file is not re-downloaded."""
        # Create a dummy file
        file_path = os.path.join(self.test_dir, "existing.zip")
        with open(file_path, 'w') as f:
            f.write('original data')

        # The download_file function should return True without trying to download
        with patch('downloader.requests.get') as mock_get:
            result = download_file("http://example.com/existing.zip", self.test_dir)
            self.assertTrue(result)
            mock_get.assert_not_called() # Ensure no network request was made

    @patch('downloader.requests.get')
    def test_download_file_failure(self, mock_get):
        """Test handling of a failed download."""
        # Mock requests.get to raise an exception
        mock_get.side_effect = RequestException("Network Error")

        result = download_file("http://example.com/fail.zip", self.test_dir)
        self.assertFalse(result)
        # Ensure the failed file was not created
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "fail.zip")))

    @patch('downloader.download_file')
    def test_download_archives(self, mock_download_file):
        """Test the parallel downloading of multiple archives."""
        mock_download_file.return_value = True
        urls = [
            "http://example.com/file1.zip",
            "http://example.com/file2.zip",
            "http://example.com/file3.zip"
        ]

        download_archives(urls, self.test_dir)

        # Check that download_file was called for each URL
        self.assertEqual(mock_download_file.call_count, len(urls))
        expected_calls = [call(url, self.test_dir, 0) for url in urls]
        mock_download_file.assert_has_calls(expected_calls, any_order=True)

if __name__ == '__main__':
    unittest.main()
