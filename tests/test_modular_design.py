#!/usr/bin/env python3
"""
Test script to verify the modular design is working correctly.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🧪 Testing modular design imports...")
    
    try:
        # Test main modules
        from src.data_sources import fred, cftc, sec
        print("✅ Data sources imported successfully")
        
        from src.processor import process_formd_data, process_formd_quarter, process_nmfp_data
        print("✅ Processor functions imported successfully")
        
        from src.downloader import download_file, download_archives, extract_formd_filings
        print("✅ Downloader functions imported successfully")
        
        from company_data import TARGET_COMPANIES, save_target_companies
        print("✅ Company data imported successfully")
        
        from company_manager import get_company_map, find_company
        print("✅ Company manager imported successfully")
        
        from database import SessionLocal
        print("✅ Database imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key modules."""
    print("\n🔧 Testing basic functionality...")
    
    try:
        # Test FRED client
        from src.data_sources.fred import FREDClient
        client = FREDClient()
        series = client.get_available_series()
        print(f"✅ FRED client working - found {len(series)} series")
        
        # Test company data
        from company_data import TARGET_COMPANIES
        print(f"✅ Target companies loaded - {len(TARGET_COMPANIES)} companies")
        
        # Test config
        from config import SEC_USER_AGENT, FORMD_SOURCE_DIR
        print(f"✅ Config loaded - SEC_USER_AGENT: {SEC_USER_AGENT[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def test_worker_process():
    """Test that the worker process can be imported and initialized."""
    print("\n⚙️ Testing worker process...")
    
    try:
        from worker import Task, task_queue
        print("✅ Worker process imported successfully")
        
        # Test that we can create a task
        task = Task(lambda: "test")
        print("✅ Worker task created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 GameCock AI Modular Design Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_worker_process
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modular design is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
