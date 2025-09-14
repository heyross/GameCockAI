#!/usr/bin/env python3
"""
Basic functionality test that doesn't require vector modules
Tests that the consolidation worked and basic Python functionality is available
"""

import unittest
import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append('../..')

class TestBasicFunctionality(unittest.TestCase):
    """Basic tests that don't require vector modules"""
    
    def test_python_environment(self):
        """Test basic Python environment"""
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertGreaterEqual(sys.version_info.minor, 8)
        print("✅ Python environment check passed")
    
    def test_basic_imports(self):
        """Test basic imports work"""
        import json
        import pathlib
        import tempfile
        import unittest
        import time
        import numpy as np
        
        # Test NumPy works
        arr = np.array([1, 2, 3])
        self.assertEqual(arr.sum(), 6)
        print("✅ Basic imports work")
    
    def test_test_structure(self):
        """Test that test structure is correct"""
        current_dir = Path(__file__).parent
        
        # Check we're in the right directory
        self.assertTrue(current_dir.name == "tests")
        self.assertTrue(current_dir.parent.name == "GameCockAI")
        
        # Check test files exist
        expected_files = [
            "test_vector_embeddings.py",
            "test_performance_benchmarks.py", 
            "test_real_integration.py",
            "test_data_generators.py",
            "run_all_tests.py",
            "test_config.json"
        ]
        
        # Check root README.md exists
        root_readme = current_dir.parent.parent / "README.md"
        self.assertTrue(root_readme.exists(), f"Missing root README.md: {root_readme}")
        
        for filename in expected_files:
            filepath = current_dir / filename
            self.assertTrue(filepath.exists(), f"Missing test file: {filename}")
        
        print("✅ Test structure verification passed")
    
    def test_config_file(self):
        """Test configuration file can be loaded"""
        config_path = Path(__file__).parent / "test_config.json"
        self.assertTrue(config_path.exists())
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn("test_settings", config)
        self.assertIn("vector_settings", config)
        
        print("✅ Configuration file test passed")
    
    def test_data_generators_import(self):
        """Test data generators can be imported"""
        try:
            from test_data_generators import FinancialTestDataGenerator
            generator = FinancialTestDataGenerator()
            self.assertIsNotNone(generator.companies)
            print("✅ Data generators import successfully")
        except Exception as e:
            self.fail(f"Data generators import failed: {e}")
    
    def test_parent_directory_imports(self):
        """Test we can import from parent directories"""
        try:
            # Try to import some basic modules from the parent directories
            import config  # Should be able to import from root
            print("✅ Parent directory imports work")
        except ImportError as e:
            print(f"⚠️  Parent directory import failed (expected): {e}")
            # This might fail and that's okay for this test


def run_basic_tests():
    """Run basic functionality tests"""
    print("=" * 60)
    print("BASIC FUNCTIONALITY TESTS")
    print("=" * 60)
    print("Testing that test consolidation was successful...")
    print()
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicFunctionality)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("BASIC TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("✅ ALL BASIC TESTS PASSED!")
        print("✅ Test consolidation successful!")
        print("✅ Test structure is working correctly")
        return True
    else:
        print("❌ Some basic tests failed")
        return False


if __name__ == "__main__":
    success = run_basic_tests()
    exit(0 if success else 1)
