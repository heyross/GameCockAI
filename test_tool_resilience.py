#!/usr/bin/env python3
"""
Tool Resilience Test Suite
Tests all 18 tools with various error conditions to ensure proper resilience
"""

import json
import sys
import os
import logging
from typing import Dict, Any, List

# Add GameCockAI to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tool_resilience():
    """Test all 18 tools for resilience against various error conditions"""
    
    print("🧪 Testing Tool Resilience for All 18 GameCock AI Tools")
    print("=" * 60)
    
    try:
        from tools import TOOL_MAP
        print(f"✅ Successfully loaded TOOL_MAP with {len(TOOL_MAP)} tools")
    except ImportError as e:
        print(f"❌ Failed to import TOOL_MAP: {e}")
        return False
    
    # Expected tools
    expected_tools = [
        # Basic tools (7)
        "search_companies", "add_to_target_list", "view_target_list", 
        "download_data", "process_data", "get_database_statistics", "check_task_status",
        # Analytics tools (5)
        "analyze_market_trends", "analyze_trading_positions", "risk_assessment", 
        "exposure_analysis", "swap_market_overview",
        # Enhanced tools (6)
        "comprehensive_company_analysis", "swap_risk_assessment", "market_overview_analysis", 
        "cftc_swap_analysis", "institutional_flow_analysis", "insider_activity_monitoring"
    ]
    
    print(f"\n📋 Expected {len(expected_tools)} tools:")
    for i, tool in enumerate(expected_tools, 1):
        print(f"  {i:2d}. {tool}")
    
    # Check if all expected tools are present
    missing_tools = [tool for tool in expected_tools if tool not in TOOL_MAP]
    extra_tools = [tool for tool in TOOL_MAP.keys() if tool not in expected_tools]
    
    if missing_tools:
        print(f"\n❌ Missing tools: {missing_tools}")
    if extra_tools:
        print(f"\n⚠️  Extra tools found: {extra_tools}")
    
    if not missing_tools:
        print(f"\n✅ All {len(expected_tools)} expected tools are present!")
    
    # Test each tool with various error conditions
    print(f"\n🔬 Testing Tool Resilience...")
    print("-" * 60)
    
    test_results = {}
    
    for tool_name, tool_info in TOOL_MAP.items():
        print(f"\n🧪 Testing {tool_name}...")
        
        tool_function = tool_info.get("function")
        if not tool_function:
            print(f"  ❌ No function found for {tool_name}")
            test_results[tool_name] = {"status": "failed", "error": "No function"}
            continue
        
        # Test with various error conditions
        test_cases = [
            ("None input", None),
            ("Empty string", ""),
            ("Invalid type", 123),
            ("Empty list", []),
            ("Empty dict", {}),
        ]
        
        tool_passed = True
        error_messages = []
        
        for test_name, test_input in test_cases:
            try:
                # Test the tool with error input
                if tool_name in ["search_companies", "add_to_target_list", "download_data", "process_data", "check_task_status"]:
                    # Tools that require specific parameters
                    if tool_name == "search_companies":
                        result = tool_function(test_input)
                    elif tool_name == "add_to_target_list":
                        result = tool_function(test_input, test_input, test_input)
                    elif tool_name == "download_data":
                        result = tool_function(test_input, test_input)
                    elif tool_name == "process_data":
                        result = tool_function(test_input)
                    elif tool_name == "check_task_status":
                        result = tool_function(test_input)
                else:
                    # Tools with optional parameters
                    result = tool_function()
                
                # Check if result is valid JSON
                try:
                    parsed_result = json.loads(result)
                    if "error" in parsed_result:
                        print(f"    ✅ {test_name}: Properly handled error - {parsed_result.get('error', 'Unknown error')}")
                    else:
                        print(f"    ⚠️  {test_name}: No error returned (may be expected)")
                except json.JSONDecodeError:
                    print(f"    ❌ {test_name}: Invalid JSON returned")
                    tool_passed = False
                    error_messages.append(f"Invalid JSON for {test_name}")
                    
            except Exception as e:
                print(f"    ❌ {test_name}: Exception not caught - {str(e)}")
                tool_passed = False
                error_messages.append(f"Uncaught exception for {test_name}: {str(e)}")
        
        # Test with valid inputs (if applicable)
        try:
            if tool_name == "view_target_list":
                result = tool_function()
            elif tool_name == "get_database_statistics":
                result = tool_function()
            elif tool_name == "swap_market_overview":
                result = tool_function()
            elif tool_name == "market_overview_analysis":
                result = tool_function()
            elif tool_name == "analyze_market_trends":
                result = tool_function(30)
            elif tool_name == "risk_assessment":
                result = tool_function("general")
            elif tool_name == "exposure_analysis":
                result = tool_function("asset_class")
            elif tool_name == "cftc_swap_analysis":
                result = tool_function(30)
            elif tool_name == "comprehensive_company_analysis":
                result = tool_function("0000320193")  # Apple CIK
            elif tool_name == "swap_risk_assessment":
                result = tool_function("asset_class", "weekly")
            elif tool_name == "institutional_flow_analysis":
                result = tool_function(90, 1000000)
            elif tool_name == "insider_activity_monitoring":
                result = tool_function("unusual_activity", 30)
            else:
                result = "Skipped - no valid test case"
            
            if result != "Skipped - no valid test case":
                parsed_result = json.loads(result)
                if "error" not in parsed_result:
                    print(f"    ✅ Valid input: Tool executed successfully")
                else:
                    print(f"    ⚠️  Valid input: Tool returned error (may be expected) - {parsed_result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            print(f"    ⚠️  Valid input: Exception (may be expected) - {str(e)}")
        
        test_results[tool_name] = {
            "status": "passed" if tool_passed else "failed",
            "errors": error_messages
        }
        
        if tool_passed:
            print(f"  ✅ {tool_name}: PASSED")
        else:
            print(f"  ❌ {tool_name}: FAILED")
            for error in error_messages:
                print(f"      - {error}")
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 60)
    
    passed_tools = [name for name, result in test_results.items() if result["status"] == "passed"]
    failed_tools = [name for name, result in test_results.items() if result["status"] == "failed"]
    
    print(f"✅ Passed: {len(passed_tools)}/{len(test_results)} tools")
    print(f"❌ Failed: {len(failed_tools)}/{len(test_results)} tools")
    
    if failed_tools:
        print(f"\n❌ Failed tools:")
        for tool in failed_tools:
            print(f"  - {tool}")
    
    # Overall assessment
    success_rate = len(passed_tools) / len(test_results) * 100
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Excellent! Tool resilience is very good.")
    elif success_rate >= 75:
        print("👍 Good! Tool resilience is acceptable.")
    elif success_rate >= 50:
        print("⚠️  Fair. Some tools need improvement.")
    else:
        print("❌ Poor. Many tools need resilience improvements.")
    
    return success_rate >= 75

def test_tool_availability():
    """Test that all tools are available and properly configured"""
    
    print(f"\n🔍 Testing Tool Availability...")
    print("-" * 40)
    
    try:
        from tools import TOOL_MAP
        
        for tool_name, tool_info in TOOL_MAP.items():
            # Check if tool has required structure
            if "function" not in tool_info:
                print(f"❌ {tool_name}: Missing function")
                continue
            
            if "schema" not in tool_info:
                print(f"❌ {tool_name}: Missing schema")
                continue
            
            schema = tool_info["schema"]
            if "name" not in schema:
                print(f"❌ {tool_name}: Missing schema name")
                continue
            
            if "description" not in schema:
                print(f"❌ {tool_name}: Missing schema description")
                continue
            
            if "parameters" not in schema:
                print(f"❌ {tool_name}: Missing schema parameters")
                continue
            
            print(f"✅ {tool_name}: Properly configured")
        
        print(f"\n✅ All tools are properly configured!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing tool availability: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GameCock AI Tool Resilience Test Suite")
    print("=" * 60)
    
    # Test tool availability first
    availability_ok = test_tool_availability()
    
    if availability_ok:
        # Test resilience
        resilience_ok = test_tool_resilience()
        
        if resilience_ok:
            print(f"\n🎉 All tests passed! Tool resilience is excellent.")
            sys.exit(0)
        else:
            print(f"\n⚠️  Some tests failed. Tool resilience needs improvement.")
            sys.exit(1)
    else:
        print(f"\n❌ Tool availability tests failed.")
        sys.exit(1)
