"""
Integration Tests for Complete Workflow
Tests the full pipeline from download to analysis.
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
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
    from temporal_analysis_tools import TemporalAnalysisEngine, analyze_risk_evolution
    from database import SessionLocal, Sec10KDocument, Sec10KSubmission
    from test_base import BaseIntegrationTest
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False

@unittest.skipUnless(IMPORTS_AVAILABLE, "Required imports not available")
class TestIntegrationWorkflow(BaseIntegrationTest):
    """Test complete workflow from processing to analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.db = SessionLocal()
        
        # Create test filing content
        self.test_filing_content = """
<SEC-HEADER>
ACCESSION NUMBER: 0001234567-23-000001
CONFORMED PERIOD OF REPORT: 20231231
</SEC-HEADER>

<DOCUMENT>
<TYPE>10-K
<SEQUENCE>1

Item 1. Business

GameStop Corp. is a specialty retailer of video game products and collectibles. 
The Company operates through its GameStop and EB Games brands.

Item 1A. Risk Factors

Our business is subject to various risks and uncertainties, including:
- Market competition from online retailers
- Technology changes affecting physical media
- Economic conditions impacting consumer spending

Item 7. Management's Discussion and Analysis

The following discussion should be read in conjunction with our consolidated financial statements.
We have experienced significant changes in our business model and strategic direction.

Item 8. Financial Statements

Our consolidated financial statements are presented below.
</DOCUMENT>
        """
        
        # Create test file
        self.test_file_path = os.path.join(self.temp_dir, "test_10k.txt")
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(self.test_filing_content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if hasattr(self.db, 'close'):
            self.db.close()
    
    def test_complete_workflow(self):
        """Test complete workflow from processing to analysis."""
        test_cik = "0001234567"
        test_accession = "0001234567-23-000001"
        
        try:
            # Step 1: Process filing with enhanced processor
            processor = EnhancedSECProcessor(db_session=self.db)
            sections = processor.process_filing_with_sections(
                self.test_file_path, test_accession, '10-K'
            )
            
            # Verify sections were extracted
            self.assertIsInstance(sections, dict)
            self.assertGreater(len(sections), 0)
            
            # Step 2: Verify data was saved to database
            saved_docs = self.db.query(Sec10KDocument).filter(
                Sec10KDocument.accession_number == test_accession
            ).all()
            
            self.assertGreater(len(saved_docs), 0)
            
            # Step 3: Create test submission record
            submission = Sec10KSubmission(
                accession_number=test_accession,
                cik=test_cik,
                company_name="GameStop Corp.",
                form_type="10-K",
                filing_date=datetime(2023, 3, 15),
                period_of_report=datetime(2022, 12, 31)
            )
            self.db.add(submission)
            self.db.commit()
            
            # Step 4: Test temporal analysis
            engine = TemporalAnalysisEngine(db_session=self.db)
            analysis_result = engine.analyze_risk_evolution(test_cik, [2023])
            
            # Verify analysis worked
            self.assertIsInstance(analysis_result, dict)
            self.assertNotIn('error', analysis_result)
            self.assertEqual(analysis_result['company_cik'], test_cik)
            
            # Step 5: Test convenience function
            result_text = analyze_risk_evolution(test_cik, [2023])
            self.assertIsInstance(result_text, str)
            self.assertIn('Risk Evolution Analysis', result_text)
            
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
    
    def test_multi_year_analysis(self):
        """Test analysis across multiple years."""
        test_cik = "0001234567"
        years = [2021, 2022, 2023]
        
        try:
            # Create test data for multiple years
            for year in years:
                accession = f"0001234567-{str(year)[2:]}-03150001"
                
                # Create submission
                submission = Sec10KSubmission(
                    accession_number=accession,
                    cik=test_cik,
                    company_name="Test Company",
                    form_type="10-K",
                    filing_date=datetime(year, 3, 15),
                    period_of_report=datetime(year, 12, 31)
                )
                self.db.add(submission)
                
                # Create risk factors document
                risk_doc = Sec10KDocument(
                    accession_number=accession,
                    section="risk_factors",
                    sequence=1,
                    content=f"Risk factors for {year} - evolving business risks and market conditions.",
                    word_count=50 + year  # Increasing word count over time
                )
                self.db.add(risk_doc)
            
            self.db.commit()
            
            # Test multi-year analysis
            engine = TemporalAnalysisEngine(db_session=self.db)
            result = engine.analyze_risk_evolution(test_cik, years)
            
            # Verify multi-year analysis
            self.assertNotIn('error', result)
            self.assertEqual(result['total_filings'], len(years))
            self.assertEqual(len(result['yearly_breakdown']), len(years))
            
            # Verify trend analysis
            summary = result['summary']
            self.assertIn('increased', summary)  # Word count should increase over time
            
        except Exception as e:
            self.fail(f"Multi-year analysis test failed: {e}")
        finally:
            # Clean up test data
            try:
                for year in years:
                    accession = f"0001234567-{str(year)[2:]}-03150001"
                    self.db.query(Sec10KDocument).filter(
                        Sec10KDocument.accession_number == accession
                    ).delete()
                    self.db.query(Sec10KSubmission).filter(
                        Sec10KSubmission.accession_number == accession
                    ).delete()
                self.db.commit()
            except:
                pass
    
    def test_error_handling_workflow(self):
        """Test error handling throughout the workflow."""
        # Test with invalid file
        processor = EnhancedSECProcessor(db_session=self.db)
        result = processor.process_filing_with_sections(
            "non_existent_file.txt", "test", "10-K"
        )
        
        # Should handle gracefully
        self.assertEqual(result, {})
        
        # Test analysis with no data
        engine = TemporalAnalysisEngine(db_session=self.db)
        result = engine.analyze_risk_evolution("nonexistent_cik", [2023])
        
        # Should return error message
        self.assertIn('error', result)
        self.assertIn('No risk factor data found', result['error'])


if __name__ == '__main__':
    unittest.main()
