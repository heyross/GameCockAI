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
            intent = intent_analysis['intent']
            
            if intent == 'data_overview':
                return self._handle_data_overview()
            elif intent == 'tool_help':
                return self._handle_tool_help()
            elif intent == 'add_company_to_list':
                return self._handle_add_company_to_list(intent_analysis)
            elif intent == 'view_target_list':
                return self._handle_view_target_list()
            elif intent == 'search_company':
                return self._handle_search_company(intent_analysis)
            elif intent == 'download_data':
                return self._handle_download_data(intent_analysis)
            elif intent == 'process_data':
                return self._handle_process_data(intent_analysis)
            elif intent == 'market_trends_analysis':
                return self._handle_market_trends_analysis(intent_analysis)
            elif intent == 'risk_assessment':
                return self._handle_risk_assessment(intent_analysis)
            elif intent == 'trading_positions_analysis':
                return self._handle_trading_positions_analysis(intent_analysis)
            elif intent == 'exposure_analysis':
                return self._handle_exposure_analysis(intent_analysis)
            elif intent == 'swap_analysis':
                return self._handle_swap_analysis(intent_analysis)
            elif intent == 'company_analysis':
                return self._handle_company_analysis(intent_analysis)
            elif intent == 'check_task_status':
                return self._handle_check_task_status(intent_analysis)
            else:
                return self._handle_general_query(intent_analysis)
                
        except Exception as e:
            logging.error(f"RAG orchestrator error: {e}")
            return f"I encountered an error processing your request: {str(e)}. Please try rephrasing your question."
    
    def _parse_query_intent(self, query: str) -> Dict[str, Any]:
        """Parse user query to understand intent and extract key information"""
        
        query_lower = query.lower()
        
        # 1. DATA OVERVIEW QUERIES
        if any(phrase in query_lower for phrase in [
            'what data', 'data access', 'data available', 'data sources', 
            'what do you have', 'show me data', 'database stats', 'statistics'
        ]):
            return {
                'intent': 'data_overview',
                'query': query
            }
        
        # 2. TOOL HELP QUERIES  
        if any(phrase in query_lower for phrase in [
            'what can you do', 'help', 'capabilities', 'tools available',
            'what tools', 'show me tools', 'list tools'
        ]):
            return {
                'intent': 'tool_help',
                'query': query
            }
        
        # 3. COMPANY MANAGEMENT QUERIES
        # Add company to list
        if any(phrase in query_lower for phrase in [
            'add', 'to the list', 'to targets', 'to companies', 'track'
        ]):
            company_name = self._extract_company_name(query_lower)
            if company_name:
                return {
                    'intent': 'add_company_to_list',
                    'company_name': company_name,
                    'query': query
                }
        
        # View target list
        if any(phrase in query_lower for phrase in [
            'show my companies', 'target list', 'my targets', 'view companies',
            'list companies', 'what companies', 'show targets', 'my companies'
        ]):
            return {
                'intent': 'view_target_list',
                'query': query
            }
        
        # Search for company
        if any(phrase in query_lower for phrase in [
            'search for', 'find company', 'look up', 'company info'
        ]):
            company_name = self._extract_company_name(query_lower)
            if company_name:
                return {
                    'intent': 'search_company',
                    'company_name': company_name,
                    'query': query
                }
        
        # 4. TASK STATUS QUERIES (check before other patterns)
        if any(phrase in query_lower for phrase in [
            'status', 'check status', 'task status', 'download status', 'check'
        ]):
            task_id = self._extract_task_id(query_lower)
            if task_id:
                return {
                    'intent': 'check_task_status',
                    'task_id': task_id,
                    'query': query
                }
        
        # 5. ANALYTICS QUERIES (specific patterns first)
        # Market trends
        if any(phrase in query_lower for phrase in [
            'market trends', 'trends', 'market analysis', 'market overview'
        ]):
            return {
                'intent': 'market_trends_analysis',
                'query': query,
                'timeframe': self._extract_timeframe(query_lower)
            }
        
        # Risk assessment
        if any(phrase in query_lower for phrase in [
            'risk', 'risk assessment', 'assess risk', 'risk analysis'
        ]):
            return {
                'intent': 'risk_assessment',
                'query': query,
                'risk_type': self._extract_risk_type(query_lower)
            }
        
        # Trading positions
        if any(phrase in query_lower for phrase in [
            'trading positions', 'positions', 'position analysis', 'concentration'
        ]):
            return {
                'intent': 'trading_positions_analysis',
                'query': query,
                'company': self._extract_company_name(query_lower)
            }
        
        # Exposure analysis
        if any(phrase in query_lower for phrase in [
            'exposure', 'exposure analysis', 'market exposure'
        ]):
            return {
                'intent': 'exposure_analysis',
                'query': query
            }
        
        # Swap market
        if any(phrase in query_lower for phrase in [
            'swap', 'swap market', 'swap analysis', 'derivatives'
        ]):
            return {
                'intent': 'swap_analysis',
                'query': query
            }
        
        # 6. DATA DOWNLOAD QUERIES (after analytics)
        if any(phrase in query_lower for phrase in [
            'download', 'get data', 'fetch data', 'pull data', 'retrieve data'
        ]):
            return self._parse_download_intent(query_lower, query)
        
        # 7. DATA PROCESSING QUERIES
        if any(phrase in query_lower for phrase in [
            'process', 'analyze data', 'run analysis', 'process data'
        ]):
            return self._parse_processing_intent(query_lower, query)
        
        # 8. COMPANY-SPECIFIC ANALYSIS (after other patterns)
        company_name = self._extract_company_name(query_lower)
        if company_name:
            return self._parse_company_analysis_intent(query_lower, query, company_name)
        
        # 9. GENERAL QUERY
        return {
            'intent': 'general',
            'query': query
        }
    
    def _extract_company_name(self, query_lower: str) -> Optional[str]:
        """Extract company name from query using multiple patterns"""
        
        # Common company names
        common_companies = [
            'apple', 'microsoft', 'tesla', 'amazon', 'google', 'meta', 'nvidia', 
            'berkshire', 'jpmorgan', 'goldman', 'koss', 'netflix', 'uber', 'airbnb',
            'paypal', 'visa', 'mastercard', 'coca-cola', 'pepsi', 'walmart', 'target'
        ]
        
        # Check for common companies first
        for company in common_companies:
            if company in query_lower:
                return company.title()
        
        # Pattern-based extraction
        patterns = [
            r'(?:add|search for|find|show me|analyze|get)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)',
            r'([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+(?:company|corp|inc|ltd|llc)',
            r'([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+(?:to the list|to targets|to companies)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                company_name = match.group(1).strip()
                # Filter out common words that aren't company names
                if company_name.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'to', 'for', 'of', 'in', 'on', 'at', 'by']:
                    return company_name.title()
        
        return None
    
    def _extract_timeframe(self, query_lower: str) -> int:
        """Extract timeframe from query (default: 30 days)"""
        
        # Look for specific time periods
        if 'last week' in query_lower or 'past week' in query_lower:
            return 7
        elif 'last month' in query_lower or 'past month' in query_lower:
            return 30
        elif 'last 3 months' in query_lower or 'past 3 months' in query_lower:
            return 90
        elif 'last year' in query_lower or 'past year' in query_lower:
            return 365
        
        # Look for number + days/weeks/months
        number_match = re.search(r'(\d+)\s*(?:days?|weeks?|months?)', query_lower)
        if number_match:
            number = int(number_match.group(1))
            if 'week' in query_lower:
                return number * 7
            elif 'month' in query_lower:
                return number * 30
            else:
                return number
        
        return 30  # Default
    
    def _extract_risk_type(self, query_lower: str) -> str:
        """Extract risk type from query"""
        
        if 'market' in query_lower:
            return 'market_risk'
        elif 'credit' in query_lower:
            return 'credit_risk'
        elif 'liquidity' in query_lower:
            return 'liquidity_risk'
        elif 'operational' in query_lower:
            return 'operational_risk'
        else:
            return 'general'
    
    def _extract_task_id(self, query_lower: str) -> Optional[str]:
        """Extract task ID from query"""
        
        # Look for UUID-like patterns or task IDs
        task_id_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', query_lower)
        if task_id_match:
            return task_id_match.group(1)
        
        # Look for simple task IDs
        simple_id_match = re.search(r'task[_\s]*id[:\s]*([a-zA-Z0-9]+)', query_lower)
        if simple_id_match:
            return simple_id_match.group(1)
        
        return None
    
    def _parse_download_intent(self, query_lower: str, query: str) -> Dict[str, Any]:
        """Parse download-related queries"""
        
        # Determine data source
        source = 'sec'  # Default
        if 'cftc' in query_lower:
            source = 'cftc'
        elif 'sec' in query_lower:
            source = 'sec'
        
        # Determine data type
        data_type = 'insider_transactions'  # Default
        if 'insider' in query_lower:
            data_type = 'insider_transactions'
        elif '13f' in query_lower or 'holdings' in query_lower:
            data_type = '13f_holdings'
        elif '8-k' in query_lower or '8k' in query_lower:
            data_type = '8k_filings'
        elif '10-k' in query_lower or '10k' in query_lower:
            data_type = '10k_filings'
        elif 'credit' in query_lower:
            data_type = 'credit'
        elif 'commodities' in query_lower:
            data_type = 'commodities'
        elif 'rates' in query_lower:
            data_type = 'rates'
        elif 'equity' in query_lower:
            data_type = 'equity'
        elif 'forex' in query_lower:
            data_type = 'forex'
        
        return {
            'intent': 'download_data',
            'source': source,
            'data_type': data_type,
            'query': query
        }
    
    def _parse_processing_intent(self, query_lower: str, query: str) -> Dict[str, Any]:
        """Parse data processing queries"""
        
        # Determine what to process
        source_dir = 'credit'  # Default
        if 'insider' in query_lower:
            source_dir = 'insider_transactions'
        elif '13f' in query_lower or 'holdings' in query_lower:
            source_dir = '13f_holdings'
        elif 'credit' in query_lower:
            source_dir = 'credit'
        elif 'commodities' in query_lower:
            source_dir = 'commodities'
        elif 'rates' in query_lower:
            source_dir = 'rates'
        elif 'equity' in query_lower:
            source_dir = 'equity'
        elif 'forex' in query_lower:
            source_dir = 'forex'
        
        return {
            'intent': 'process_data',
            'source_dir': source_dir,
            'query': query
        }
    
    def _parse_company_analysis_intent(self, query_lower: str, query: str, company_name: str) -> Dict[str, Any]:
        """Parse company-specific analysis queries"""
        
        # Determine analysis type
        analysis_type = 'general'
        if '8-k' in query_lower or '8k' in query_lower:
            analysis_type = '8k_filings'
        elif '10-k' in query_lower or '10k' in query_lower:
            analysis_type = '10k_filings'
        elif 'insider' in query_lower or 'trading' in query_lower:
            analysis_type = 'insider_transactions'
        elif 'holdings' in query_lower or '13f' in query_lower:
            analysis_type = '13f_holdings'
        elif 'comprehensive' in query_lower or 'full analysis' in query_lower:
            analysis_type = 'comprehensive'
        elif 'peer' in query_lower or 'compare' in query_lower:
            analysis_type = 'peer_analysis'
        
        return {
            'intent': 'company_analysis',
            'company_name': company_name,
            'analysis_type': analysis_type,
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
    
    def _handle_add_company_to_list(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle requests to add a company to the target list"""
        
        company_name = intent_analysis['company_name']
        
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
            
            # Step 2: Extract company information
            company_info = search_data[0] if isinstance(search_data, list) else search_data
            cik = company_info.get('cik_str')
            ticker = company_info.get('ticker', 'N/A')
            title = company_info.get('title', company_name)
            
            # Step 3: Check if company is already in targets
            current_targets = [comp.get('cik_str') for comp in TARGET_COMPANIES]
            
            if cik in current_targets:
                return f"✅ {title} ({ticker}) is already in your target list!"
            
            # Step 4: Add company to target list
            if 'add_to_target_list' in self.tools:
                add_result = self.tools['add_to_target_list']['function'](cik, ticker, title)
                add_data = json.loads(add_result)
                
                if 'error' not in add_data:
                    return f"""✅ **Successfully added {title} to your target list!**

**Company Details:**
- **Name:** {title}
- **Ticker:** {ticker}
- **CIK:** {cik}

**Next Steps:**
- You can now download data for {title} using the Download Data menu
- Run analysis on {title} using the analytics tools
- View all your target companies anytime

**Would you like me to:**
- Download recent SEC filings for {title}?
- Run a comprehensive analysis of {title}?
- Show you what data is available for {title}?"""
                else:
                    return f"❌ Could not add {title} to target list: {add_data['error']}"
            else:
                return "❌ Cannot add to target list (function unavailable)"
                
        except Exception as e:
            logging.error(f"Error adding company to list: {e}")
            return f"❌ Error adding {company_name} to target list: {str(e)}"
    
    def _handle_view_target_list(self) -> str:
        """Handle requests to view the target company list"""
        
        try:
            if 'view_target_list' not in self.tools:
                return "❌ Target list functionality not available."
            
            result = self.tools['view_target_list']['function']()
            target_data = json.loads(result)
            
            if 'error' in target_data:
                return f"❌ Error retrieving target list: {target_data['error']}"
            
            if not target_data or len(target_data) == 0:
                return """📋 **Your Target Company List is Empty**

**To add companies to your list, you can:**
- Say: "Add Apple to my targets"
- Say: "Search for Tesla and add it to the list"
- Use the main menu: Select Target Companies

**Once you have companies in your list, I can:**
- Download their SEC and CFTC data
- Run comprehensive analysis
- Monitor their filings and activities
- Track insider trading patterns"""
            
            response = f"""📋 **Your Target Companies ({len(target_data)} companies)**

"""
            for i, company in enumerate(target_data, 1):
                name = company.get('title', 'Unknown')
                ticker = company.get('ticker', 'N/A')
                cik = company.get('cik_str', 'N/A')
                response += f"{i}. **{name}** ({ticker}) - CIK: {cik}\n"
            
            response += f"""

**What you can do with these companies:**
- Download their latest SEC filings
- Run comprehensive analysis
- Monitor insider trading activity
- Compare against industry peers

**Try asking:**
- "Download SEC data for all my targets"
- "Run comprehensive analysis for {target_data[0].get('title', 'Apple')}"
- "Show me insider activity for my companies"
"""
            return response
            
        except Exception as e:
            logging.error(f"Error viewing target list: {e}")
            return f"❌ Error retrieving target list: {str(e)}"
    
    def _handle_search_company(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle company search requests"""
        
        company_name = intent_analysis['company_name']
        
        try:
            if 'search_companies' not in self.tools:
                return "❌ Company search functionality not available."
            
            search_result = self.tools['search_companies']['function'](company_name)
            search_data = json.loads(search_result)
            
            if 'error' in search_data:
                return f"❌ Error searching for {company_name}: {search_data['error']}"
            
            if 'message' in search_data and 'No companies found' in search_data['message']:
                return f"❌ No companies found matching '{company_name}'. Please try a different name or ticker symbol."
            
            # Format the search results
            if isinstance(search_data, list):
                response = f"""🔍 **Search Results for "{company_name}"**

Found {len(search_data)} companies:

"""
                for i, company in enumerate(search_data[:5], 1):  # Show top 5
                    name = company.get('title', 'Unknown')
                    ticker = company.get('ticker', 'N/A')
                    cik = company.get('cik_str', 'N/A')
                    response += f"{i}. **{name}** ({ticker}) - CIK: {cik}\n"
                
                if len(search_data) > 5:
                    response += f"\n... and {len(search_data) - 5} more companies\n"
                
                response += f"""

**What you can do:**
- Add to targets: "Add {search_data[0].get('title', 'this company')} to my list"
- Get analysis: "Show me {search_data[0].get('title', 'this company')} 8-K filings"
- Download data: "Download SEC data for {search_data[0].get('title', 'this company')}"
"""
            else:
                # Single company result
                company = search_data
                name = company.get('title', 'Unknown')
                ticker = company.get('ticker', 'N/A')
                cik = company.get('cik_str', 'N/A')
                
                response = f"""🔍 **Found: {name}**

**Company Details:**
- **Name:** {name}
- **Ticker:** {ticker}
- **CIK:** {cik}

**What you can do:**
- Add to targets: "Add {name} to my list"
- Get analysis: "Show me {name} 8-K filings"
- Download data: "Download SEC data for {name}"
- Run analysis: "Run comprehensive analysis for {name}"
"""
            
            return response
            
        except Exception as e:
            logging.error(f"Error searching for company: {e}")
            return f"❌ Error searching for {company_name}: {str(e)}"
    
    def _handle_download_data(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle data download requests"""
        
        source = intent_analysis.get('source', 'sec')
        data_type = intent_analysis.get('data_type', 'insider_transactions')
        
        try:
            if 'download_data' not in self.tools:
                return "❌ Data download functionality not available."
            
            result = self.tools['download_data']['function'](source, data_type)
            download_data = json.loads(result)
            
            if 'error' in download_data:
                return f"❌ Error downloading {data_type} data: {download_data['error']}"
            
            task_id = download_data.get('task_id', 'Unknown')
            
            return f"""📥 **Download Started Successfully**

**Download Details:**
- **Source:** {source.upper()}
- **Data Type:** {data_type.replace('_', ' ').title()}
- **Task ID:** {task_id}

**What happens next:**
- The download is running in the background
- You can continue using other features while it downloads
- Check status anytime: "Check status for task {task_id}"

**After download completes, you can:**
- Process the data: "Process {data_type} data"
- Run analysis on the new data
- View database statistics to see the new records

**Note:** Large downloads may take several minutes to complete."""
            
        except Exception as e:
            logging.error(f"Error downloading data: {e}")
            return f"❌ Error downloading {data_type} data: {str(e)}"
    
    def _handle_process_data(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle data processing requests"""
        
        source_dir = intent_analysis.get('source_dir', 'credit')
        
        try:
            if 'process_data' not in self.tools:
                return "❌ Data processing functionality not available."
            
            result = self.tools['process_data']['function'](source_dir)
            process_data = json.loads(result)
            
            if 'error' in process_data:
                return f"❌ Error processing {source_dir} data: {process_data['error']}"
            
            task_id = process_data.get('task_id', 'Unknown')
            
            return f"""⚙️ **Data Processing Started**

**Processing Details:**
- **Data Type:** {source_dir.replace('_', ' ').title()}
- **Task ID:** {task_id}

**What happens next:**
- Raw data is being processed and loaded into the database
- This may take several minutes depending on data size
- Check status anytime: "Check status for task {task_id}"

**After processing completes, you can:**
- Run analytics on the processed data
- View database statistics to see new records
- Perform comprehensive analysis

**Note:** Processing large datasets may take time. You can continue using other features."""
            
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            return f"❌ Error processing {source_dir} data: {str(e)}"
    
    def _handle_market_trends_analysis(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle market trends analysis requests"""
        
        timeframe = intent_analysis.get('timeframe', 30)
        
        try:
            if 'analyze_market_trends' not in self.tools:
                return "❌ Market trends analysis not available."
            
            result = self.tools['analyze_market_trends']['function'](timeframe)
            analysis_data = json.loads(result)
            
            if 'error' in analysis_data:
                return f"❌ Error analyzing market trends: {analysis_data['error']}"
            
            return f"""📊 **Market Trends Analysis ({timeframe} days)**

{analysis_data.get('summary', 'Analysis completed successfully.')}

**Key Insights:**
- Analysis period: Last {timeframe} days
- Data sources: CFTC swap data, SEC filings
- AI-powered insights included

**What you can do next:**
- Run risk assessment: "Assess market risk"
- Analyze trading positions: "Analyze trading positions"
- Get exposure analysis: "Show me market exposure"
- Download more recent data: "Download latest CFTC data"
"""
            
        except Exception as e:
            logging.error(f"Error analyzing market trends: {e}")
            return f"❌ Error analyzing market trends: {str(e)}"
    
    def _handle_risk_assessment(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle risk assessment requests"""
        
        risk_type = intent_analysis.get('risk_type', 'general')
        
        try:
            if 'risk_assessment' not in self.tools:
                return "❌ Risk assessment not available."
            
            result = self.tools['risk_assessment']['function'](risk_type)
            risk_data = json.loads(result)
            
            if 'error' in risk_data:
                return f"❌ Error performing risk assessment: {risk_data['error']}"
            
            return f"""⚠️ **Risk Assessment ({risk_type.replace('_', ' ').title()})**

{risk_data.get('summary', 'Risk assessment completed successfully.')}

**Assessment Details:**
- Risk type: {risk_type.replace('_', ' ').title()}
- Analysis includes: Market data, trading positions, exposure metrics
- AI-powered risk scoring included

**What you can do next:**
- Get exposure analysis: "Show me market exposure"
- Analyze trading positions: "Analyze trading positions"
- Run swap risk assessment: "Assess swap market risk"
- Download fresh data: "Download latest CFTC data"
"""
            
        except Exception as e:
            logging.error(f"Error performing risk assessment: {e}")
            return f"❌ Error performing risk assessment: {str(e)}"
    
    def _handle_trading_positions_analysis(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle trading positions analysis requests"""
        
        company = intent_analysis.get('company')
        
        try:
            if 'analyze_trading_positions' not in self.tools:
                return "❌ Trading positions analysis not available."
            
            result = self.tools['analyze_trading_positions']['function'](company)
            positions_data = json.loads(result)
            
            if 'error' in positions_data:
                return f"❌ Error analyzing trading positions: {positions_data['error']}"
            
            company_text = f" for {company}" if company else ""
            
            return f"""📈 **Trading Positions Analysis{company_text}**

{positions_data.get('summary', 'Trading positions analysis completed successfully.')}

**Analysis Details:**
- Focus: Trading positions and concentration risks
- Data sources: CFTC swap data, SEC filings
- AI-powered concentration analysis included

**What you can do next:**
- Get risk assessment: "Assess risk"
- Analyze market exposure: "Show me exposure analysis"
- Run comprehensive company analysis: "Run comprehensive analysis for {company or 'your targets'}"
- Download fresh data: "Download latest CFTC data"
"""
            
        except Exception as e:
            logging.error(f"Error analyzing trading positions: {e}")
            return f"❌ Error analyzing trading positions: {str(e)}"
    
    def _handle_exposure_analysis(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle exposure analysis requests"""
        
        try:
            if 'exposure_analysis' not in self.tools:
                return "❌ Exposure analysis not available."
            
            result = self.tools['exposure_analysis']['function']()
            exposure_data = json.loads(result)
            
            if 'error' in exposure_data:
                return f"❌ Error performing exposure analysis: {exposure_data['error']}"
            
            return f"""📊 **Market Exposure Analysis**

{exposure_data.get('summary', 'Exposure analysis completed successfully.')}

**Analysis Details:**
- Dimensions: Asset class, currency, notional amounts
- Data sources: CFTC swap data, SEC filings
- AI-powered exposure insights included

**What you can do next:**
- Get risk assessment: "Assess risk"
- Analyze trading positions: "Analyze trading positions"
- Run market trends analysis: "Show me market trends"
- Download fresh data: "Download latest CFTC data"
"""
            
        except Exception as e:
            logging.error(f"Error performing exposure analysis: {e}")
            return f"❌ Error performing exposure analysis: {str(e)}"
    
    def _handle_swap_analysis(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle swap market analysis requests"""
        
        try:
            if 'swap_market_overview' not in self.tools:
                return "❌ Swap market analysis not available."
            
            result = self.tools['swap_market_overview']['function']()
            swap_data = json.loads(result)
            
            if 'error' in swap_data:
                return f"❌ Error analyzing swap market: {swap_data['error']}"
            
            return f"""🔄 **Swap Market Analysis**

{swap_data.get('summary', 'Swap market analysis completed successfully.')}

**Analysis Details:**
- Market overview: CFTC swap derivatives data
- Asset classes: Credit, rates, equity, commodities, forex
- AI-powered market insights included

**What you can do next:**
- Get risk assessment: "Assess swap risk"
- Analyze market trends: "Show me market trends"
- Get exposure analysis: "Show me exposure analysis"
- Download fresh data: "Download latest CFTC data"
"""
            
        except Exception as e:
            logging.error(f"Error analyzing swap market: {e}")
            return f"❌ Error analyzing swap market: {str(e)}"
    
    def _handle_check_task_status(self, intent_analysis: Dict[str, Any]) -> str:
        """Handle task status check requests"""
        
        task_id = intent_analysis.get('task_id')
        
        try:
            if 'check_task_status' not in self.tools:
                return "❌ Task status checking not available."
            
            result = self.tools['check_task_status']['function'](task_id)
            status_data = json.loads(result)
            
            if 'error' in status_data:
                return f"❌ Error checking task status: {status_data['error']}"
            
            status = status_data.get('status', 'Unknown')
            message = status_data.get('message', 'No additional information')
            
            return f"""📋 **Task Status Check**

**Task ID:** {task_id}
**Status:** {status}
**Message:** {message}

**What this means:**
- **Completed:** Task finished successfully
- **Running:** Task is still in progress
- **Failed:** Task encountered an error
- **Pending:** Task is waiting to start

**Next steps:**
- If completed: You can now use the processed data
- If running: Check back in a few minutes
- If failed: Try running the task again or contact support
"""
            
        except Exception as e:
            logging.error(f"Error checking task status: {e}")
            return f"❌ Error checking task status: {str(e)}"
    
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
