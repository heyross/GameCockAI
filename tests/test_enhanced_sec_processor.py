"""
Comprehensive tests for the Enhanced SEC Processor
Tests section extraction, database operations, and error handling.
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
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
    from enhanced_sec_processor import EnhancedSECProcessor
    from database import SessionLocal, Sec10KDocument, Sec8KItem, Sec10KSubmission, Sec8KSubmission
    from test_base import BaseIntegrationTest
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False

@unittest.skipUnless(IMPORTS_AVAILABLE, "Required imports not available")
class TestEnhancedSECProcessor(unittest.TestCase):
    """Test suite for EnhancedSECProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = EnhancedSECProcessor()
        
        # Create mock database session
        self.mock_db = Mock()
        self.processor.db = self.mock_db
        
        # Sample 10-K content with sections
        self.sample_10k_content = """
        <SEC-HEADER>
        ACCESSION NUMBER: 0001234567-23-000001
        CONFORMED PERIOD OF REPORT: 20231231
        </SEC-HEADER>
        
        <DOCUMENT>
        <TYPE>10-K
        <SEQUENCE>1
        <FILENAME>gme-10k-2023.txt
        
        Item 1. Business
        
        GameStop Corp. is a specialty retailer of video game products and collectibles. 
        The Company operates through its GameStop and EB Games brands.
        
        Item 1A. Risk Factors
        
        Our business is subject to various risks and uncertainties, including:
        - Market competition
        - Technology changes
        - Economic conditions
        
        Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations
        
        The following discussion should be read in conjunction with our consolidated financial statements.
        We have experienced significant changes in our business model.
        
        Item 8. Financial Statements and Supplementary Data
        
        Our consolidated financial statements are presented below.
        </DOCUMENT>
        """
        
        # Sample 8-K content with items
        self.sample_8k_content = """
        <SEC-HEADER>
        ACCESSION NUMBER: 0001234567-23-000002
        CONFORMED PERIOD OF REPORT: 20230315
        </SEC-HEADER>
        
        <DOCUMENT>
        <TYPE>8-K
        <SEQUENCE>1
        <FILENAME>gme-8k-2023.txt
        
        Item 1.01 Entry into a Material Definitive Agreement
        
        On March 15, 2023, GameStop Corp. entered into a new distribution agreement.
        
        Item 2.02 Results of Operations and Financial Condition
        
        The Company reported quarterly results showing improved performance.
        
        Item 5.02 Departure of Directors or Certain Officers
        
        The Company announced the departure of its Chief Financial Officer.
        </DOCUMENT>
        """
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if hasattr(self.processor, 'db') and hasattr(self.processor.db, 'close'):
            self.processor.db.close()
    
    def test_init(self):
        """Test processor initialization."""
        processor = EnhancedSECProcessor()
        self.assertIsNotNone(processor.db)
        self.assertIsNotNone(processor.section_patterns)
        self.assertIsNotNone(processor.item8k_patterns)
        
        # Test with custom database session
        mock_db = Mock()
        processor = EnhancedSECProcessor(db_session=mock_db)
        self.assertEqual(processor.db, mock_db)
    
    def test_section_patterns_defined(self):
        """Test that all required section patterns are defined."""
        expected_sections = ['business', 'risk_factors', 'mdna', 'financial_statements', 'controls']
        
        for section in expected_sections:
            self.assertIn(section, self.processor.section_patterns)
            self.assertIsInstance(self.processor.section_patterns[section], list)
            self.assertGreater(len(self.processor.section_patterns[section]), 0)
    
    def test_8k_item_patterns_defined(self):
        """Test that 8-K item patterns are properly defined."""
        expected_items = ['1.01', '2.02', '5.02', '8.01']
        
        for item in expected_items:
            self.assertIn(item, self.processor.item8k_patterns)
            self.assertIsInstance(self.processor.item8k_patterns[item], str)
            self.assertGreater(len(self.processor.item8k_patterns[item]), 0)
    
    def test_clean_content(self):
        """Test content cleaning functionality."""
        dirty_content = """
        <html>
        <body>
        <p>This is a test   with   multiple    spaces.</p>
        <br><br>
        <div>And line breaks</div>
        </body>
        </html>
        """
        
        cleaned = self.processor._clean_content(dirty_content)
        
        # Should remove HTML tags
        self.assertNotIn('<html>', cleaned)
        self.assertNotIn('<body>', cleaned)
        self.assertNotIn('<p>', cleaned)
        
        # Should normalize whitespace
        self.assertNotIn('   ', cleaned)  # Multiple spaces
        self.assertIn('This is a test with multiple spaces.', cleaned)
    
    def test_extract_sections_from_10k(self):
        """Test 10-K section extraction."""
        # Create temporary file with sample content
        test_file = os.path.join(self.temp_dir, 'test_10k.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_10k_content)
        
        sections = self.processor.extract_sections_from_10k(test_file, '0001234567-23-000001')
        
        # Should extract multiple sections
        self.assertIsInstance(sections, dict)
        self.assertGreater(len(sections), 0)
        
        # Check for expected sections
        expected_sections = ['business', 'risk_factors', 'mdna']
        for section in expected_sections:
            if section in sections:
                self.assertIsInstance(sections[section], str)
                self.assertGreater(len(sections[section]), 50)  # Minimum content length
    
    def test_extract_items_from_8k(self):
        """Test 8-K item extraction."""
        # Create temporary file with sample content
        test_file = os.path.join(self.temp_dir, 'test_8k.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_8k_content)
        
        items = self.processor.extract_items_from_8k(test_file, '0001234567-23-000002')
        
        # Should extract multiple items
        self.assertIsInstance(items, dict)
        self.assertGreater(len(items), 0)
        
        # Check for expected items
        expected_items = ['1.01', '2.02', '5.02']
        for item in expected_items:
            if item in items:
                self.assertIsInstance(items[item], dict)
                self.assertIn('title', items[item])
                self.assertIn('content', items[item])
                self.assertGreater(len(items[item]['content']), 20)
    
    def test_extract_sections_with_missing_file(self):
        """Test section extraction with non-existent file."""
        non_existent_file = os.path.join(self.temp_dir, 'non_existent.txt')
        
        sections = self.processor.extract_sections_from_10k(non_existent_file, 'test')
        
        # Should return empty dict on error
        self.assertEqual(sections, {})
    
    def test_extract_sections_with_malformed_content(self):
        """Test section extraction with malformed content."""
        malformed_content = "This is not a proper SEC filing document."
        
        test_file = os.path.join(self.temp_dir, 'malformed.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(malformed_content)
        
        sections = self.processor.extract_sections_from_10k(test_file, 'test')
        
        # Should handle gracefully and return empty dict
        self.assertEqual(sections, {})
    
    def test_save_sections_to_database(self):
        """Test saving sections to database."""
        # Mock database operations
        self.mock_db.query.return_value.filter.return_value.delete.return_value = None
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        
        sections = {
            'business': 'Sample business description content.',
            'risk_factors': 'Sample risk factors content.',
            'mdna': 'Sample MD&A content.'
        }
        
        result = self.processor.save_sections_to_database('0001234567-23-000001', sections, '10-K')
        
        # Should not raise exception
        self.assertIsNone(result)
        
        # Verify database operations were called
        self.mock_db.query.assert_called()
        self.mock_db.add.assert_called()
        self.mock_db.commit.assert_called()
    
    def test_save_sections_to_database_with_error(self):
        """Test database error handling."""
        # Mock database error
        self.mock_db.query.side_effect = Exception("Database error")
        self.mock_db.rollback.return_value = None
        
        sections = {'business': 'Sample content'}
        
        # Should handle error gracefully
        result = self.processor.save_sections_to_database('test', sections, '10-K')
        self.assertIsNone(result)
        
        # Should call rollback
        self.mock_db.rollback.assert_called()
    
    def test_save_8k_items_to_database(self):
        """Test saving 8-K items to database."""
        # Mock database operations
        self.mock_db.query.return_value.filter.return_value.delete.return_value = None
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        
        items = {
            '1.01': {'title': 'Entry into Agreement', 'content': 'Sample content'},
            '2.02': {'title': 'Results', 'content': 'Sample results content'}
        }
        
        result = self.processor.save_8k_items_to_database('0001234567-23-000002', items)
        
        # Should not raise exception
        self.assertIsNone(result)
        
        # Verify database operations were called
        self.mock_db.query.assert_called()
        self.mock_db.add.assert_called()
        self.mock_db.commit.assert_called()
    
    def test_process_filing_with_sections_10k(self):
        """Test processing 10-K filing with section extraction."""
        # Create temporary file
        test_file = os.path.join(self.temp_dir, 'test_10k.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_10k_content)
        
        # Mock database operations
        self.mock_db.query.return_value.filter.return_value.delete.return_value = None
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        
        result = self.processor.process_filing_with_sections(
            test_file, '0001234567-23-000001', '10-K'
        )
        
        # Should return extracted sections
        self.assertIsInstance(result, dict)
    
    def test_process_filing_with_sections_8k(self):
        """Test processing 8-K filing with item extraction."""
        # Create temporary file
        test_file = os.path.join(self.temp_dir, 'test_8k.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_8k_content)
        
        # Mock database operations
        self.mock_db.query.return_value.filter.return_value.delete.return_value = None
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        
        result = self.processor.process_filing_with_sections(
            test_file, '0001234567-23-000002', '8-K'
        )
        
        # Should return extracted items
        self.assertIsInstance(result, dict)
    
    def test_process_filing_with_unsupported_type(self):
        """Test processing unsupported filing type."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write("Sample content")
        
        result = self.processor.process_filing_with_sections(
            test_file, 'test', 'S-4'
        )
        
        # Should return empty dict for unsupported types
        self.assertEqual(result, {})
    
    def test_find_section_end(self):
        """Test finding section end boundaries."""
        content = "Item 1. Business\nThis is business content.\nItem 2. Properties\nThis is properties content."
        start_pos = content.find("Item 1. Business")
        
        end_pos = self.processor._find_section_end(content, start_pos)
        
        # Should find the next item
        self.assertGreater(end_pos, start_pos)
        self.assertLess(end_pos, len(content))
    
    def test_find_8k_item_end(self):
        """Test finding 8-K item end boundaries."""
        content = "Item 1.01 Agreement\nThis is agreement content.\nItem 2.02 Results\nThis is results content."
        start_pos = content.find("Item 1.01")
        
        end_pos = self.processor._find_8k_item_end(content, start_pos, "1.01")
        
        # Should find the next item
        self.assertGreater(end_pos, start_pos)
        self.assertLess(end_pos, len(content))
    
    def test_extract_section_by_patterns(self):
        """Test section extraction using multiple patterns."""
        content = "BUSINESS DESCRIPTION\nThis is our business description content."
        patterns = [r'BUSINESS\s*[:\-]?', r'Item\s+1\.?\s*[:\-]?\s*Business']
        
        result = self.processor._extract_section_by_patterns(content, patterns)
        
        # Should extract content
        self.assertIsNotNone(result)
        self.assertIn("business description", result.lower())
    
    def test_extract_8k_item(self):
        """Test 8-K item extraction."""
        content = "Item 1.01 Entry into Material Definitive Agreement\nThis is the agreement content."
        
        result = self.processor._extract_8k_item(content, "1.01", "Entry into Material Definitive Agreement")
        
        # Should extract content
        self.assertIsNotNone(result)
        self.assertIn("agreement", result.lower())
    
    def test_minimum_content_length_filtering(self):
        """Test that sections with insufficient content are filtered out."""
        # Create content with very short sections
        short_content = """
        Item 1. Business
        Short.
        
        Item 1A. Risk Factors
        Very brief risk discussion.
        
        Item 7. Management's Discussion and Analysis
        This is a much longer section that provides detailed analysis of the company's financial performance, market conditions, and strategic initiatives. It includes comprehensive discussion of revenue trends, cost management, competitive positioning, and future outlook.
        """
        
        test_file = os.path.join(self.temp_dir, 'short_content.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(short_content)
        
        sections = self.processor.extract_sections_from_10k(test_file, 'test')
        
        # Should only extract sections with sufficient content
        for section_name, content in sections.items():
            self.assertGreater(len(content), 100)  # Minimum content length


class TestEnhancedSECProcessorIntegration(BaseIntegrationTest):
    """Integration tests for EnhancedSECProcessor with real database."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        super().setUp()
        self.processor = EnhancedSECProcessor(db_session=SessionLocal())
    
    def test_real_database_operations(self):
        """Test actual database operations with real session."""
        # Create test sections
        sections = {
            'business': 'This is a comprehensive business description that meets the minimum length requirements for proper database storage and retrieval.',
            'risk_factors': 'This is a detailed risk factors section that discusses various business risks and uncertainties that could affect the company\'s operations and financial performance.',
            'mdna': 'This is an extensive management discussion and analysis section that provides detailed insights into the company\'s financial condition, results of operations, and future prospects.'
        }
        
        test_accession = '0001234567-23-000001'
        
        try:
            # Save to database
            self.processor.save_sections_to_database(test_accession, sections, '10-K')
            
            # Verify data was saved
            saved_docs = self.db.query(Sec10KDocument).filter(
                Sec10KDocument.accession_number == test_accession
            ).all()
            
            self.assertEqual(len(saved_docs), len(sections))
            
            # Verify content
            for doc in saved_docs:
                self.assertIn(doc.section, sections)
                self.assertEqual(doc.content, sections[doc.section])
                self.assertGreater(doc.word_count, 0)
            
        except Exception as e:
            self.fail(f"Database operations failed: {e}")
        finally:
            # Clean up test data
            try:
                self.db.query(Sec10KDocument).filter(
                    Sec10KDocument.accession_number == test_accession
                ).delete()
                self.db.commit()
            except:
                pass


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add unit tests
    test_suite.addTest(unittest.makeSuite(TestEnhancedSECProcessor))
    
    # Add integration tests
    test_suite.addTest(unittest.makeSuite(TestEnhancedSECProcessorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
