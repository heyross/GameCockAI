"""
RAG Tool Orchestrator - Intelligent AI that uses existing GameCock application functionality
Instead of bypassing the application, this system leverages all built-in tools and workflows
"""

import json
import re
from typing import Dict, List, Any, Optional
import logging

# Import all existing tools
try:
    import sys
    import os
    gamecock_path = os.path.join(os.path.dirname(__file__), 'GameCockAI')
    if os.path.exists(gamecock_path) and gamecock_path not in sys.path:
        sys.path.append(gamecock_path)
    
    from GameCockAI.tools import TOOL_MAP
    from GameCockAI.company_data import TARGET_COMPANIES
    TOOLS_AVAILABLE = True
    
    # Verify we have all 18 tools as expected
    expected_tools = 18
    actual_tools = len(TOOL_MAP)
    if actual_tools == expected_tools:
        logging.info(f"✅ Tool orchestrator loaded all {actual_tools} tools successfully")
    else:
        logging.warning(f"⚠️ Expected {expected_tools} tools but loaded {actual_tools}")
        
    # Log tool categories for verification
    basic_tools = ['search_companies', 'add_to_target_list', 'view_target_list', 'download_data', 'process_data', 'get_database_statistics', 'check_task_status']
    analytics_tools = ['analyze_market_trends', 'analyze_trading_positions', 'risk_assessment', 'exposure_analysis', 'swap_market_overview']
    enhanced_tools = ['comprehensive_company_analysis', 'swap_risk_assessment', 'market_overview_analysis', 'cftc_swap_analysis', 'institutional_flow_analysis', 'insider_activity_monitoring']
    
    available_tools = list(TOOL_MAP.keys())
    missing_tools = []
    for tool_list, category in [(basic_tools, 'Basic'), (analytics_tools, 'Analytics'), (enhanced_tools, 'Enhanced')]:
        missing = [tool for tool in tool_list if tool not in available_tools]
        if missing:
            missing_tools.extend(missing)
            logging.warning(f"⚠️ Missing {category} tools: {missing}")
    
    if not missing_tools:
        logging.info("✅ All expected tools are available to Raven")
    else:
        logging.error(f"❌ Missing tools: {missing_tools}")
except ImportError as e:
    logging.warning(f"⚠️ Could not import tools: {e}")
    TOOL_MAP = {}
    TARGET_COMPANIES = []
    TOOLS_AVAILABLE = False

class RAGToolOrchestrator:
    """Intelligent RAG system that orchestrates existing application tools"""
    
    def __init__(self):
        self.tools = TOOL_MAP
        self.available_tools = list(TOOL_MAP.keys()) if TOOLS_AVAILABLE else []
        self.conversation_state = {}
        
    def query_with_tools(self, user_query: str, messages: Optional[List[Dict]] = None) -> str:
        """
        Process user query by intelligently using existing application tools
        
        This follows the proper workflow:
        1. Parse intent and identify required data
        2. Check if company needs to be added to targets  
        3. Use appropriate download/processing tools
        4. Apply analytics tools for analysis
        5. Generate comprehensive response
        """
        
        if not TOOLS_AVAILABLE:
            return "❌ Application tools are not available. Please check your installation."
        
        try:
            # Parse the user's intent and identify what they need
            intent_analysis = self._parse_query_intent(user_query)
            
            # Execute the appropriate workflow based on intent
            if intent_analysis['intent'] == 'data_overview':
                return self._handle_data_overview()
            elif intent_analysis['intent'] == 'company_analysis':
                return self._handle_company_analysis(intent_analysis)
            elif intent_analysis['intent'] == 'market_analysis':
                return self._handle_market_analysis(intent_analysis)
            elif intent_analysis['intent'] == 'tool_help':
                return self._handle_tool_help()
            else:
                return self._handle_general_query(intent_analysis)
                
        except Exception as e:
            logging.error(f"RAG orchestrator error: {e}")
            return f"I encountered an error processing your request: {str(e)}. Please try rephrasing your question."
    
    def _parse_query_intent(self, query: str) -> Dict[str, Any]:
        """Parse user query to understand intent and extract key information"""
        
        query_lower = query.lower()
        
        # Data overview queries
        if any(phrase in query_lower for phrase in ['what data', 'data access', 'data available', 'data sources']):
            return {
                'intent': 'data_overview',
                'query': query
            }
        
        # Tool help queries  
        if any(phrase in query_lower for phrase in ['what can you do', 'help', 'capabilities', 'tools available']):
            return {
                'intent': 'tool_help',
                'query': query
            }
        
        # Company-specific queries
        company_patterns = [
            r'(?:show|find|get|analyze)\s+(?:me\s+)?(\w+(?:\s+\w+)?)\s+(?:8-?k|10-?k|filings?|insider|holdings)',
            r'(\w+(?:\s+\w+)?)\s+(?:8-?k|10-?k|filings?|insider|holdings)',
            r'(?:apple|microsoft|tesla|amazon|google|meta|nvidia|berkshire|jpmorgan|goldman)',
        ]
        
        company_name = None
        for pattern in company_patterns:
            match = re.search(pattern, query_lower)
            if match and len(pattern) > 50:  # Only for the detailed patterns
                company_name = match.group(1).title()
                break
            elif any(company in query_lower for company in ['apple', 'microsoft', 'tesla', 'amazon', 'google', 'meta', 'nvidia', 'berkshire', 'jpmorgan', 'goldman']):
                # Extract company name
                for company in ['Apple', 'Microsoft', 'Tesla', 'Amazon', 'Google', 'Meta', 'NVIDIA', 'Berkshire', 'JPMorgan', 'Goldman']:
                    if company.lower() in query_lower:
                        company_name = company
                        break
        
        if company_name:
            # Determine data type needed
            data_type = 'general'
            if any(term in query_lower for term in ['8-k', '8k']):
                data_type = '8k_filings'
            elif any(term in query_lower for term in ['10-k', '10k']):
                data_type = '10k_filings'
            elif any(term in query_lower for term in ['insider', 'trading']):
                data_type = 'insider_transactions'
            elif any(term in query_lower for term in ['holdings', '13f']):
                data_type = '13f_holdings'
            elif any(term in query_lower for term in ['filing']):
                data_type = 'sec_filings'
                
            return {
                'intent': 'company_analysis',
                'company_name': company_name,
                'data_type': data_type,
                'query': query
            }
        
        # Market analysis queries
        if any(phrase in query_lower for phrase in ['market trends', 'swap market', 'trading positions', 'risk assessment', 'exposure analysis']):
            return {
                'intent': 'market_analysis',
                'analysis_type': self._identify_market_analysis_type(query_lower),
                'query': query
            }
        
        # General query
        return {
            'intent': 'general',
            'query': query
        }
    
    def _identify_market_analysis_type(self, query_lower: str) -> str:
        """Identify specific type of market analysis requested"""
        
        if 'trends' in query_lower:
            return 'market_trends'
        elif 'positions' in query_lower:
            return 'trading_positions'
        elif 'risk' in query_lower:
            return 'risk_assessment'
        elif 'exposure' in query_lower:
            return 'exposure_analysis'
        elif 'swap' in query_lower:
            return 'swap_overview'
        else:
            return 'general_market'
    
    def _handle_data_overview(self) -> str:
        """Handle requests for data overview using database statistics"""
        
        try:
            # Use existing tool to get database statistics
            if 'get_database_statistics' in self.tools:
                stats_result = self.tools['get_database_statistics']['function']()
                stats_data = json.loads(stats_result)
                
                # Use existing tool to view target companies
                targets_result = self.tools['view_target_list']['function']()
                targets_data = json.loads(targets_result)
                
                response = f"""
## 📊 **GameCock Data Access Summary**

### **Current Database:**
{self._format_database_stats(stats_data)}

### **Target Companies ({len(targets_data) if isinstance(targets_data, list) else 'Unknown'}):**
{self._format_target_companies(targets_data)}

### **Available Data Sources:**
- **SEC Data:** 8-K filings, 10-K filings, insider transactions, 13F holdings, Form D, N-Series
- **CFTC Data:** Swap derivatives (credit, rates, equity, commodities, forex)
- **Analytics:** {len([k for k in self.tools.keys() if 'analy' in k])} analysis tools available

### **What I Can Do:**
- Search and add companies to download targets
- Download and process SEC/CFTC data
- Perform comprehensive financial analysis
- Monitor insider trading and institutional flows
- Assess market risk and concentration

**Try asking:** "Show me Apple 8-K filings" or "Analyze market trends"
"""
                return response
                
            else:
                return "Database statistics tool not available. Please check your installation."
                
        except Exception as e:
            logging.error(f"Error getting data overview: {e}")
            return f"Error retrieving data overview: {str(e)}"
    
    def _handle_company_analysis(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle company-specific analysis requests"""
        
        company_name = intent_analysis['company_name']
        data_type = intent_analysis['data_type']
        
        try:
            # Step 1: Search for the company
            if 'search_companies' not in self.tools:
                return "❌ Company search functionality not available."
            
            search_result = self.tools['search_companies']['function'](company_name)
            search_data = json.loads(search_result)
            
            if 'error' in search_data:
                return f"❌ Error searching for {company_name}: {search_data['error']}"
            
            if 'message' in search_data and 'No companies found' in search_data['message']:
                return f"❌ No companies found matching '{company_name}'. Please try a different name or ticker symbol."
            
            # Step 2: Check if company is already in targets, if not add it
            company_info = search_data[0] if isinstance(search_data, list) else search_data
            cik = company_info.get('cik_str')
            ticker = company_info.get('ticker', 'N/A')
            title = company_info.get('title', company_name)
            
            # Check current targets
            current_targets = [comp.get('cik_str') for comp in TARGET_COMPANIES]
            
            if cik not in current_targets:
                if 'add_to_target_list' in self.tools:
                    add_result = self.tools['add_to_target_list']['function'](cik, ticker, title)
                    add_data = json.loads(add_result)
                    
                    if 'error' not in add_data:
                        target_status = f"✅ Added {title} to target list"
                    else:
                        target_status = f"⚠️ Could not add to targets: {add_data['error']}"
                else:
                    target_status = "⚠️ Cannot add to target list (function unavailable)"
            else:
                target_status = f"✅ {title} already in target list"
            
            # Step 3: Check what data is available and suggest next steps
            response = f"""
## 🏢 **{title} ({ticker}) Analysis**

**Company Found:** {title}
**CIK:** {cik}
**Status:** {target_status}

### **Next Steps for {data_type.replace('_', ' ').title()}:**

"""
            
            # Step 4: Suggest appropriate data download based on request
            if data_type in ['8k_filings', '10k_filings', 'sec_filings']:
                response += f"""
**📋 To get {title} SEC filings:**
1. **Download Data:** I can download SEC insider transaction data and Form 13F holdings
2. **Available Data Types:**
   - `insider_transactions` - Form 3, 4, 5 filings
   - `13f_holdings` - Institutional holdings data
   - `exchange_metrics` - Exchange-related data

**Would you like me to download this data?**
Type: "Download SEC insider transactions for {company_name}"
"""
            
            elif data_type == 'insider_transactions':
                response += f"""
**📈 For insider trading analysis:**
1. I can download and analyze insider transaction data
2. Use advanced analytics to detect unusual activity
3. Compare against historical patterns

**Available Actions:**
- Download: `download_data("sec", "insider_transactions")`  
- Analysis: `insider_activity_monitoring()` 
- Company Profile: `comprehensive_company_analysis("{cik}")`

**Would you like me to start the download and analysis?**
"""
            
            elif data_type == '13f_holdings':
                response += f"""
**🏦 For institutional holdings analysis:**
1. Download Form 13F data 
2. Analyze institutional flows and position changes
3. Compare against market trends

**Available Actions:**
- Download: `download_data("sec", "13f_holdings")`
- Analysis: `institutional_flow_analysis()`
- Peer Comparison: `company_peer_analysis("{cik}")`
"""
            
            # Step 5: Check if we have existing data and can run analytics
            if 'get_database_statistics' in self.tools:
                stats_result = self.tools['get_database_statistics']['function']()
                stats_data = json.loads(stats_result)
                
                if stats_data and any(table.get('count', 0) > 0 for table in stats_data.get('tables', [])):
                    response += f"""
### **🔍 Current Data Analysis Available:**

I can run these analytics on existing data:
- **Comprehensive Analysis:** `comprehensive_company_analysis("{cik}")`
- **Market Trends:** `analyze_market_trends()`
- **Risk Assessment:** `risk_assessment()`
- **Exposure Analysis:** `exposure_analysis()`

**Try:** "Run comprehensive analysis for {company_name}"
"""
            
            return response
            
        except Exception as e:
            logging.error(f"Error in company analysis: {e}")
            return f"❌ Error analyzing {company_name}: {str(e)}"
    
    def _handle_market_analysis(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle market analysis requests using existing analytics tools"""
        
        analysis_type = intent_analysis['analysis_type']
        
        try:
            response = f"## 📈 **Market Analysis: {analysis_type.replace('_', ' ').title()}**\n\n"
            
            # Execute the appropriate analytics tool
            if analysis_type == 'market_trends' and 'analyze_market_trends' in self.tools:
                result = self.tools['analyze_market_trends']['function']()
                result_data = json.loads(result)
                response += self._format_analytics_result("Market Trends", result_data)
                
            elif analysis_type == 'trading_positions' and 'analyze_trading_positions' in self.tools:
                result = self.tools['analyze_trading_positions']['function']()
                result_data = json.loads(result)
                response += self._format_analytics_result("Trading Positions", result_data)
                
            elif analysis_type == 'risk_assessment' and 'risk_assessment' in self.tools:
                result = self.tools['risk_assessment']['function']()
                result_data = json.loads(result)
                response += self._format_analytics_result("Risk Assessment", result_data)
                
            elif analysis_type == 'exposure_analysis' and 'exposure_analysis' in self.tools:
                result = self.tools['exposure_analysis']['function']()
                result_data = json.loads(result)
                response += self._format_analytics_result("Exposure Analysis", result_data)
                
            elif analysis_type == 'swap_overview' and 'swap_market_overview' in self.tools:
                result = self.tools['swap_market_overview']['function']()
                result_data = json.loads(result)
                response += self._format_analytics_result("Swap Market Overview", result_data)
                
            else:
                response += f"""
**Available Market Analytics:**
{self._list_available_analytics()}

**Try one of these commands:**
- "Analyze market trends"
- "Show swap market overview" 
- "Perform risk assessment"
- "Analyze trading positions"
"""
            
            return response
            
        except Exception as e:
            logging.error(f"Error in market analysis: {e}")
            return f"❌ Error performing {analysis_type}: {str(e)}"
    
    def _handle_tool_help(self) -> str:
        """Show available tools and capabilities"""
        
        if not TOOLS_AVAILABLE:
            return "❌ Tools are not currently available."
        
        # Explicit tool categorization matching the 18 tools
        tool_categories = {
            'Company Management (3 tools)': [
                'search_companies',
                'add_to_target_list', 
                'view_target_list'
            ],
            'Data Pipeline (4 tools)': [
                'download_data',
                'process_data', 
                'get_database_statistics',
                'check_task_status'
            ],
            'Basic Analytics (5 tools)': [
                'analyze_market_trends',
                'analyze_trading_positions',
                'risk_assessment', 
                'exposure_analysis',
                'swap_market_overview'
            ],
            'Enhanced Analytics (6 tools)': [
                'comprehensive_company_analysis',
                'swap_risk_assessment',
                'market_overview_analysis',
                'cftc_swap_analysis',
                'institutional_flow_analysis',
                'insider_activity_monitoring'
            ]
        }
        
        response = f"## 🛠️ **All {len(self.tools)} Raven Tools Available**\n\n"
        
        total_shown = 0
        for category, tool_list in tool_categories.items():
            available_tools = [tool for tool in tool_list if tool in self.tools]
            total_shown += len(available_tools)
            
            if available_tools:
                response += f"### **{category}:**\n"
                for tool in available_tools:
                    tool_info = self.tools[tool]['schema']
                    description = tool_info.get('description', 'No description')
                    response += f"- **{tool}:** {description}\n"
                response += "\n"
        
        # Show any additional tools not in our predefined categories  
        uncategorized = [tool for tool in self.tools.keys() 
                        if not any(tool in cat_tools for cat_tools in tool_categories.values())]
        if uncategorized:
            response += f"### **Other Tools ({len(uncategorized)}):**\n"
            for tool in uncategorized:
                tool_info = self.tools[tool]['schema']
                response += f"- **{tool}:** {tool_info.get('description', 'No description')}\n"
            total_shown += len(uncategorized)
            response += "\n"
        
        response += f"""
### **🎯 Example Commands:**
- **Company Research:** "Show me Apple 8-K filings"
- **Market Analysis:** "Analyze market trends for the last 30 days" 
- **Data Management:** "Download SEC insider transaction data"
- **Risk Assessment:** "Run swap risk assessment"
- **Comprehensive Analysis:** "Run comprehensive analysis for Tesla"

### **📊 System Status:**
- **Total Tools Loaded:** {len(self.tools)} tools
- **Tools Categorized:** {total_shown} tools  
- **All Systems:** {"✅ Operational" if len(self.tools) >= 18 else "⚠️ Some tools missing"}

**Type any question to get started!**
"""
        
        return response
    
    def _handle_general_query(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle general queries by suggesting appropriate tools"""
        
        query = intent_analysis['query']
        
        # Suggest relevant tools based on keywords
        suggestions = []
        
        if any(term in query.lower() for term in ['company', 'stock', 'ticker']):
            suggestions.append("Try: `search_companies('company_name')` to find a specific company")
        
        if any(term in query.lower() for term in ['download', 'data', 'get']):
            suggestions.append("Try: `download_data('sec', 'insider_transactions')` to download data")
        
        if any(term in query.lower() for term in ['analyze', 'analysis', 'trends']):
            suggestions.append("Try: `analyze_market_trends()` for market analysis")
        
        if not suggestions:
            suggestions = [
                "Ask about specific companies: 'Show me Apple filings'",
                "Request market analysis: 'Analyze swap market trends'", 
                "Get data overview: 'What data do you have access to?'"
            ]
        
        response = f"""
I understand you're asking: "{query}"

**Here's what I can help with:**
{chr(10).join(f'- {suggestion}' for suggestion in suggestions)}

**Available Tool Categories:**
- **Company Research:** Search, analyze, and track companies
- **Data Management:** Download and process SEC/CFTC data  
- **Market Analytics:** {len([k for k in self.tools.keys() if 'analy' in k])} analysis tools
- **Risk Assessment:** Comprehensive risk and exposure analysis

**For help:** Type "What can you do?" or "Help"
"""
        
        return response
    
    def _format_database_stats(self, stats_data: Dict) -> str:
        """Format database statistics for display"""
        
        if not stats_data or 'error' in stats_data:
            return "❌ Database statistics unavailable"
        
        if 'tables' in stats_data:
            table_info = []
            for table in stats_data['tables']:
                name = table.get('name', 'Unknown')
                count = table.get('count', 0)
                table_info.append(f"- **{name}:** {count:,} records")
            
            if table_info:
                return '\n'.join(table_info)
        
        return "Database information available"
    
    def _format_target_companies(self, targets_data) -> str:
        """Format target companies list"""
        
        if isinstance(targets_data, list) and targets_data:
            companies = []
            for target in targets_data[:5]:  # Show first 5
                name = target.get('title', 'Unknown')
                ticker = target.get('ticker', 'N/A')
                companies.append(f"- **{name}** ({ticker})")
            
            result = '\n'.join(companies)
            if len(targets_data) > 5:
                result += f"\n- ... and {len(targets_data) - 5} more"
            
            return result
        else:
            return "No target companies configured"
    
    def _format_analytics_result(self, analysis_name: str, result_data: Dict) -> str:
        """Format analytics results for display"""
        
        if 'error' in result_data:
            return f"❌ {analysis_name} failed: {result_data['error']}\n"
        
        response = f"### **{analysis_name} Results:**\n\n"
        
        # Add AI insights if available
        if 'ai_insights' in result_data:
            response += f"**🤖 AI Analysis:**\n{result_data['ai_insights']}\n\n"
        
        # Add key metrics
        if 'sql_results' in result_data:
            sql_results = result_data['sql_results']
            
            if isinstance(sql_results, dict):
                for key, value in sql_results.items():
                    if isinstance(value, (int, float)):
                        response += f"- **{key.replace('_', ' ').title()}:** {value:,.2f}\n"
                    elif isinstance(value, str):
                        response += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        response += f"\n**Analysis completed at:** {result_data.get('timestamp', 'Unknown time')}\n"
        
        return response
    
    def _list_available_analytics(self) -> str:
        """List all available analytics tools"""
        
        analytics_tools = [k for k in self.tools.keys() if any(term in k for term in ['analy', 'assess', 'monitor', 'overview'])]
        
        if analytics_tools:
            return '\n'.join(f"- {tool.replace('_', ' ').title()}" for tool in analytics_tools)
        else:
            return "No analytics tools available"


# Main query function for backward compatibility
def query_raven_with_tools(user_query: str, messages: Optional[List[Dict]] = None) -> str:
    """
    Main entry point for tool-orchestrated RAG queries
    Uses existing GameCock application functionality intelligently
    """
    
    orchestrator = RAGToolOrchestrator()
    return orchestrator.query_with_tools(user_query, messages)


# Also provide a simple interface
def query_raven_tools(user_query: str) -> str:
    """Simple interface for tool orchestration"""
    return query_raven_with_tools(user_query)


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = RAGToolOrchestrator()
    
    test_queries = [
        "What data do you have access to?",
        "Show me Apple 8-K filings",
        "Analyze market trends",
        "What can you do?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        result = orchestrator.query_with_tools(query)
        print(result)
