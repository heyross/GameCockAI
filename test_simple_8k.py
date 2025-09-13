#!/usr/bin/env python3
"""Simple test to verify 8K processor parsing without database."""

import os
import tempfile
from processor_8k import SEC8KProcessor

def test_parsing_only():
    """Test just the parsing functionality without database."""
    
    # Create a simple test file
    sample_content = '''<SEC-HEADER>
<ACCEPTANCE-DATETIME>20230101120000</ACCEPTANCE-DATETIME>
<FILING-DATE>2023-01-01</FILING-DATE>
<PERIOD>20230101</PERIOD>
<COMPANY-CONFORMED-NAME>TEST CORP</COMPANY-CONFORMED-NAME>
<CIK>0001234567</CIK>
<TYPE>8-K</TYPE>
<ITEMS>1.01</ITEMS>
</SEC-HEADER>
<DOCUMENT>
<TYPE>8-K</TYPE>
<TEXT>
<html><body>
<p>Item 1.01 Entry into a Material Definitive Agreement.</p>
<p>On January 1, 2023, the Company entered into a material definitive agreement.</p>
</body></html>
</TEXT>
</DOCUMENT>
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        # Test without database session
        processor = SEC8KProcessor(db_session=None)
        
        # Test metadata extraction
        metadata = processor.extract_filing_metadata(temp_file)
        print("Extracted metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        # Test items parsing
        items = processor.parse_filing_items(temp_file)
        print(f"\nExtracted {len(items)} items:")
        for item in items:
            print(f"  {item['item_number']}: {item['item_title'][:50]}...")
        
        # Verify expected values
        assert metadata.get('cik') == '0001234567', f"Expected CIK 0001234567, got {metadata.get('cik')}"
        assert metadata.get('company_name') == 'TEST CORP', f"Expected 'TEST CORP', got {metadata.get('company_name')}"
        assert metadata.get('form_type') == '8-K', f"Expected '8-K', got {metadata.get('form_type')}"
        assert len(items) > 0, "Expected at least one item"
        
        print("\n✅ All parsing tests passed!")
        
    finally:
        os.unlink(temp_file)

if __name__ == '__main__':
    test_parsing_only()
