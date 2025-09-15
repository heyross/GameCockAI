#!/usr/bin/env python3
"""
Comprehensive Test Runner for GameCock AI Vector Embeddings
Runs all test suites and generates detailed reports
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add src directory to path - handle both relative and absolute paths
import os
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Test suite imports
try:
    from test_vector_embeddings import run_all_tests as run_unit_tests
    from test_performance_benchmarks import run_performance_benchmarks
    from test_real_integration import run_real_integration_tests
    from test_data_generators import FinancialTestDataGenerator
    TESTS_AVAILABLE = True
except ImportError as e:
    TESTS_AVAILABLE = False
    print(f"⚠️  Test modules not fully available: {e}")

class TestSuiteRunner:
    """Comprehensive test suite runner and reporter"""
    
    def __init__(self, output_dir: str = "./test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.test_results = {
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "test_suites": {},
            "summary": {},
            "environment": {},
            "recommendations": []
        }
        
        self.test_suites = [
            {
                "name": "Unit Tests",
                "function": run_unit_tests,
                "description": "Comprehensive unit tests with mocked dependencies",
                "critical": True
            },
            {
                "name": "Enhanced SEC Processing Tests",
                "function": self._run_enhanced_sec_tests,
                "description": "Tests for enhanced SEC section extraction and temporal analysis",
                "critical": True
            },
            {
                "name": "Performance Benchmarks", 
                "function": run_performance_benchmarks,
                "description": "Performance and scalability benchmarks",
                "critical": False
            },
            {
                "name": "Real Integration Tests",
                "function": run_real_integration_tests,
                "description": "End-to-end integration tests with real components",
                "critical": True
            }
        ]
        
        print(f"🧪 Test Suite Runner initialized")
        print(f"📁 Results directory: {self.output_dir}")
    
    def collect_environment_info(self):
        """Collect environment information for test context"""
        import platform
        
        env_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "current_directory": os.getcwd(),
            "test_time": datetime.now().isoformat()
        }
        
        # Check for available packages
        try:
            import numpy
            env_info["numpy_version"] = numpy.__version__
        except ImportError:
            env_info["numpy_version"] = "Not available"
        
        try:
            import torch
            env_info["torch_version"] = torch.__version__
            env_info["cuda_available"] = torch.cuda.is_available()
        except ImportError:
            env_info["torch_version"] = "Not available"
            env_info["cuda_available"] = False
        
        try:
            import chromadb
            env_info["chromadb_version"] = chromadb.__version__
        except ImportError:
            env_info["chromadb_version"] = "Not available"
        
        # Check if vector modules are available
        try:
            from vector_db import GameCockVectorDB
            env_info["vector_modules_available"] = True
        except ImportError:
            env_info["vector_modules_available"] = False
        
        self.test_results["environment"] = env_info
        return env_info
    
    def _run_enhanced_sec_tests(self) -> bool:
        """Run enhanced SEC processing and temporal analysis tests."""
        try:
            import unittest
            from test_enhanced_sec_processor import TestEnhancedSECProcessor, TestEnhancedSECProcessorIntegration
            from test_temporal_analysis_tools import (
                TestTemporalAnalysisEngine, 
                TestTemporalAnalysisConvenienceFunctions,
                TestTemporalAnalysisIntegration
            )
            from test_integration_workflow import TestIntegrationWorkflow
            
            # Create test suite
            test_suite = unittest.TestSuite()
            
            # Add test classes
            test_classes = [
                TestEnhancedSECProcessor,
                TestEnhancedSECProcessorIntegration,
                TestTemporalAnalysisEngine,
                TestTemporalAnalysisConvenienceFunctions,
                TestTemporalAnalysisIntegration,
                TestIntegrationWorkflow
            ]
            
            for test_class in test_classes:
                test_suite.addTest(unittest.makeSuite(test_class))
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
            result = runner.run(test_suite)
            
            return result.wasSuccessful()
            
        except ImportError as e:
            print(f"⚠️ Enhanced SEC tests not available: {e}")
            return False
        except Exception as e:
            print(f"❌ Enhanced SEC tests failed: {e}")
            return False
    
    def run_all_tests(self, 
                     skip_performance: bool = False,
                     skip_integration: bool = False,
                     verbose: bool = True) -> bool:
        """
        Run all test suites and generate comprehensive report
        
        Args:
            skip_performance: Skip performance benchmarks
            skip_integration: Skip integration tests 
            verbose: Enable verbose output
            
        Returns:
            Overall success status
        """
        print("🚀 Starting GameCock AI Vector Embeddings Test Suite")
        print("=" * 70)
        
        if not TESTS_AVAILABLE:
            print("❌ Test modules not available - cannot run tests")
            return False
        
        self.test_results["start_time"] = datetime.now().isoformat()
        start_timestamp = time.time()
        
        # Collect environment information
        env_info = self.collect_environment_info()
        if verbose:
            print("🔍 Environment Information:")
            print(f"  Python: {env_info['python_version'].split()[0]}")
            print(f"  Platform: {env_info['platform']}")
            print(f"  Vector modules: {'✅' if env_info['vector_modules_available'] else '❌'}")
            print(f"  CUDA available: {'✅' if env_info['cuda_available'] else '❌'}")
            print()
        
        overall_success = True
        
        # Run each test suite
        for suite_config in self.test_suites:
            suite_name = suite_config["name"]
            
            # Check skip conditions
            if skip_performance and "Performance" in suite_name:
                print(f"⏭️  Skipping {suite_name} (requested)")
                continue
            
            if skip_integration and "Integration" in suite_name:
                print(f"⏭️  Skipping {suite_name} (requested)")
                continue
            
            print(f"📋 Running {suite_name}...")
            print(f"   {suite_config['description']}")
            
            suite_start = time.time()
            
            try:
                # Run the test suite
                suite_success = suite_config["function"]()
                suite_duration = time.time() - suite_start
                
                # Record results
                self.test_results["test_suites"][suite_name] = {
                    "success": suite_success,
                    "duration": suite_duration,
                    "critical": suite_config["critical"],
                    "description": suite_config["description"]
                }
                
                if suite_success:
                    print(f"✅ {suite_name} completed successfully ({suite_duration:.1f}s)")
                else:
                    print(f"❌ {suite_name} failed ({suite_duration:.1f}s)")
                    
                    if suite_config["critical"]:
                        overall_success = False
                        print(f"💥 Critical test suite failed - overall test run marked as failed")
                
            except Exception as e:
                suite_duration = time.time() - suite_start
                
                print(f"💥 {suite_name} crashed: {str(e)}")
                
                self.test_results["test_suites"][suite_name] = {
                    "success": False,
                    "duration": suite_duration,
                    "critical": suite_config["critical"],
                    "error": str(e),
                    "description": suite_config["description"]
                }
                
                if suite_config["critical"]:
                    overall_success = False
            
            print()
        
        # Finalize results
        end_timestamp = time.time()
        total_duration = end_timestamp - start_timestamp
        
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["duration"] = total_duration
        
        # Generate summary
        self._generate_summary()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Save detailed results
        self._save_results()
        
        # Print final report
        self._print_final_report(verbose)
        
        return overall_success
    
    def _generate_summary(self):
        """Generate test summary statistics"""
        suites_run = len(self.test_results["test_suites"])
        suites_passed = sum(1 for result in self.test_results["test_suites"].values() if result["success"])
        suites_failed = suites_run - suites_passed
        
        critical_suites = [s for s in self.test_results["test_suites"].values() if s["critical"]]
        critical_passed = sum(1 for s in critical_suites if s["success"])
        critical_failed = len(critical_suites) - critical_passed
        
        total_duration = self.test_results["duration"]
        
        self.test_results["summary"] = {
            "suites_run": suites_run,
            "suites_passed": suites_passed,
            "suites_failed": suites_failed,
            "critical_suites_total": len(critical_suites),
            "critical_suites_passed": critical_passed,
            "critical_suites_failed": critical_failed,
            "total_duration": total_duration,
            "overall_success": critical_failed == 0,
            "pass_rate": (suites_passed / suites_run * 100) if suites_run > 0 else 0
        }
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        env = self.test_results["environment"]
        summary = self.test_results["summary"]
        
        # Environment-based recommendations
        if not env.get("vector_modules_available", False):
            recommendations.append({
                "type": "critical",
                "message": "Vector modules not available - run 'python vector_setup.py' to install"
            })
        
        if not env.get("cuda_available", False):
            recommendations.append({
                "type": "performance",
                "message": "CUDA not available - consider GPU acceleration for better performance"
            })
        
        # Test results-based recommendations
        if summary["critical_suites_failed"] > 0:
            recommendations.append({
                "type": "critical",
                "message": "Critical test suites failed - system may not be production ready"
            })
        
        if summary["pass_rate"] < 100:
            recommendations.append({
                "type": "warning",
                "message": f"Test pass rate {summary['pass_rate']:.1f}% - investigate failures"
            })
        
        # Performance recommendations
        if summary["total_duration"] > 300:  # 5 minutes
            recommendations.append({
                "type": "performance",
                "message": "Test suite took over 5 minutes - consider optimizing test environment"
            })
        
        # Success recommendations
        if summary["overall_success"]:
            recommendations.append({
                "type": "success",
                "message": "All critical tests passed - system ready for deployment"
            })
        
        self.test_results["recommendations"] = recommendations
    
    def _save_results(self):
        """Save detailed test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.output_dir / f"test_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        # Save text report
        text_file = self.output_dir / f"test_report_{timestamp}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_text_report())
        
        print(f"📄 Results saved:")
        print(f"  JSON: {json_file}")
        print(f"  Text: {text_file}")
    
    def _generate_text_report(self) -> str:
        """Generate detailed text report"""
        lines = [
            "🧪 GameCock AI Vector Embeddings Test Report",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {self.test_results['duration']:.1f} seconds",
            ""
        ]
        
        # Environment section
        lines.extend([
            "🔍 ENVIRONMENT",
            "-" * 20
        ])
        
        env = self.test_results["environment"]
        lines.append(f"Python: {env['python_version'].split()[0]}")
        lines.append(f"Platform: {env['platform']}")
        lines.append(f"Vector modules: {'Available' if env['vector_modules_available'] else 'Not available'}")
        lines.append(f"CUDA support: {'Available' if env['cuda_available'] else 'Not available'}")
        lines.append("")
        
        # Summary section
        lines.extend([
            "📊 SUMMARY",
            "-" * 20
        ])
        
        summary = self.test_results["summary"]
        lines.append(f"Test suites run: {summary['suites_run']}")
        lines.append(f"Passed: {summary['suites_passed']}")
        lines.append(f"Failed: {summary['suites_failed']}")
        lines.append(f"Pass rate: {summary['pass_rate']:.1f}%")
        lines.append(f"Overall success: {'✅ Yes' if summary['overall_success'] else '❌ No'}")
        lines.append("")
        
        # Individual test suite results
        lines.extend([
            "📋 TEST SUITE RESULTS",
            "-" * 20
        ])
        
        for suite_name, result in self.test_results["test_suites"].items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            critical = " (CRITICAL)" if result["critical"] else ""
            duration = f"{result['duration']:.1f}s"
            
            lines.append(f"{suite_name}: {status}{critical} - {duration}")
            if "error" in result:
                lines.append(f"  Error: {result['error']}")
        
        lines.append("")
        
        # Recommendations section
        lines.extend([
            "💡 RECOMMENDATIONS",
            "-" * 20
        ])
        
        for rec in self.test_results["recommendations"]:
            icon = {
                "critical": "🚨",
                "warning": "⚠️ ",
                "performance": "⚡",
                "success": "✅"
            }.get(rec["type"], "ℹ️ ")
            
            lines.append(f"{icon} {rec['message']}")
        
        return "\n".join(lines)
    
    def _print_final_report(self, verbose: bool = True):
        """Print final test report to console"""
        print("=" * 70)
        print("🏁 FINAL TEST REPORT")
        print("=" * 70)
        
        summary = self.test_results["summary"]
        
        print(f"📊 Summary:")
        print(f"  Test suites run: {summary['suites_run']}")
        print(f"  Passed: {summary['suites_passed']}")
        print(f"  Failed: {summary['suites_failed']}")
        print(f"  Pass rate: {summary['pass_rate']:.1f}%")
        print(f"  Duration: {summary['total_duration']:.1f} seconds")
        
        print(f"\n🎯 Overall Result:")
        if summary["overall_success"]:
            print("✅ SUCCESS - All critical tests passed!")
            print("   Your vector embeddings system is ready for deployment.")
        else:
            print("❌ FAILURE - Critical tests failed!")
            print("   Please review failures before deploying.")
        
        # Show critical recommendations
        critical_recs = [r for r in self.test_results["recommendations"] if r["type"] == "critical"]
        if critical_recs:
            print(f"\n🚨 Critical Issues:")
            for rec in critical_recs:
                print(f"  • {rec['message']}")
        
        print(f"\n📁 Detailed results saved to: {self.output_dir}")


def setup_test_environment():
    """Set up test environment and generate test data"""
    print("🏗️  Setting up test environment...")
    
    # Create test data directory
    test_data_dir = Path("./test_data")
    test_data_dir.mkdir(exist_ok=True)
    
    # Generate test data if needed
    try:
        from test_data_generators import FinancialTestDataGenerator
        
        generator = FinancialTestDataGenerator()
        generator.save_test_data_to_files(str(test_data_dir))
        
        print(f"✅ Test data generated in {test_data_dir}")
        return True
        
    except Exception as e:
        print(f"⚠️  Failed to generate test data: {e}")
        return False


def check_prerequisites():
    """Check if all prerequisites are available"""
    print("🔍 Checking prerequisites...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check required packages
    required_packages = [
        "numpy", "json", "pathlib", "tempfile", "unittest"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            issues.append(f"Missing package: {package}")
    
    # Check test modules
    if not TESTS_AVAILABLE:
        issues.append("Test modules not available")
    
    if issues:
        print("❌ Prerequisites not met:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ All prerequisites met")
        return True


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(
        description="GameCock AI Vector Embeddings Test Suite Runner"
    )
    
    parser.add_argument(
        "--skip-performance", 
        action="store_true",
        help="Skip performance benchmark tests"
    )
    
    parser.add_argument(
        "--skip-integration",
        action="store_true", 
        help="Skip real integration tests"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./test_results",
        help="Output directory for test results"
    )
    
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only set up test environment, don't run tests"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Cannot run tests - prerequisites not met")
        return 1
    
    # Set up test environment
    setup_success = setup_test_environment()
    if not setup_success:
        print("⚠️  Test environment setup had issues")
    
    if args.setup_only:
        print("✅ Test environment setup complete")
        return 0
    
    # Run tests
    runner = TestSuiteRunner(output_dir=args.output_dir)
    
    success = runner.run_all_tests(
        skip_performance=args.skip_performance,
        skip_integration=args.skip_integration,
        verbose=args.verbose
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
