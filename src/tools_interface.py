"""
Tools Interface for GameCock AI - Unified Function Access
Provides a clean interface to all available tools and analytics
"""

import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_available_data_sources() -> Dict[str, Any]:
    """
    Get information about all available data sources in the GameCock system
    """
    try:
        # Import from the REAL database module with all tables (GameCockAI/database.py)
        from ..database import get_db_stats
        from ..config import (
            CFTC_CREDIT_SOURCE_DIR, CFTC_RATES_SOURCE_DIR, CFTC_EQUITY_SOURCE_DIR,
            CFTC_COMMODITIES_SOURCE_DIR, CFTC_FOREX_SOURCE_DIR, INSIDER_SOURCE_DIR,
            THRTNF_SOURCE_DIR, EXCHANGE_SOURCE_DIR, NCEN_SOURCE_DIR, NPORT_SOURCE_DIR,
            FORMD_SOURCE_DIR
        )
        import os
        
        # Get database statistics
        db_stats = get_db_stats()
        
        # Check data directories
        data_dirs = {
            'CFTC Credit': CFTC_CREDIT_SOURCE_DIR,
            'CFTC Rates': CFTC_RATES_SOURCE_DIR,
            'CFTC Equity': CFTC_EQUITY_SOURCE_DIR,
            'CFTC Commodities': CFTC_COMMODITIES_SOURCE_DIR,
            'CFTC Forex': CFTC_FOREX_SOURCE_DIR,
            'SEC Insider Trading': INSIDER_SOURCE_DIR,
            'Form 13F': THRTNF_SOURCE_DIR,
            'Exchange Metrics': EXCHANGE_SOURCE_DIR,
            'Form N-CEN': NCEN_SOURCE_DIR,
            'Form N-PORT': NPORT_SOURCE_DIR,
            'Form D': FORMD_SOURCE_DIR
        }
        
        data_availability = {}
        for name, path in data_dirs.items():
            if os.path.exists(path):
                file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                data_availability[name] = {'path': path, 'files': file_count}
            else:
                data_availability[name] = {'path': path, 'files': 0}
        
        # Check FRED data
        fred_data_path = "GameCockAI/data/fred"
        if os.path.exists(fred_data_path):
            fred_files = [f for f in os.listdir(fred_data_path) if f.endswith('.csv')]
            data_availability['FRED Economic Data'] = {
                'path': fred_data_path, 
                'files': len(fred_files),
                'series': fred_files
            }
        
        return {
            'database_stats': db_stats,
            'data_sources': data_availability,
            'total_tables': len(db_stats),
            'total_records': sum(db_stats.values()),
            'summary': generate_data_summary(db_stats, data_availability)
        }
        
    except Exception as e:
        logger.error(f"Error getting data sources: {e}")
        return {'error': str(e)}

def generate_data_summary(db_stats: Dict, data_availability: Dict) -> str:
    """Generate a human-readable summary of available data"""
    
    summary = f"""
🎯 **GameCock Financial Data System Summary**

📊 **Database Statistics:**
- Total Tables: {len(db_stats)}
- Total Records: {sum(db_stats.values()):,}

📁 **Data Sources Available:**

**SEC (Securities and Exchange Commission):**
- Insider Trading Data: {data_availability.get('SEC Insider Trading', {}).get('files', 0)} files
- Form 13F Institutional Holdings: {data_availability.get('Form 13F', {}).get('files', 0)} files  
- Form D Private Placements: {data_availability.get('Form D', {}).get('files', 0)} files
- Exchange Trading Metrics: {data_availability.get('Exchange Metrics', {}).get('files', 0)} files
- Form N-CEN Fund Census: {data_availability.get('Form N-CEN', {}).get('files', 0)} files
- Form N-PORT Portfolio Reports: {data_availability.get('Form N-PORT', {}).get('files', 0)} files

**CFTC (Commodity Futures Trading Commission):**
- Credit Derivatives: {data_availability.get('CFTC Credit', {}).get('files', 0)} files
- Interest Rate Swaps: {data_availability.get('CFTC Rates', {}).get('files', 0)} files
- Equity Derivatives: {data_availability.get('CFTC Equity', {}).get('files', 0)} files
- Commodities: {data_availability.get('CFTC Commodities', {}).get('files', 0)} files
- Foreign Exchange: {data_availability.get('CFTC Forex', {}).get('files', 0)} files

**FRED (Federal Reserve Economic Data):**
- Interest Rate Series: {data_availability.get('FRED Economic Data', {}).get('files', 0)} files
"""

    # Add top database tables by record count
    if db_stats:
        top_tables = sorted(db_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        summary += "\n**Top Database Tables by Records:**\n"
        for table, count in top_tables:
            summary += f"- {table}: {count:,} records\n"
    
    # Add available FRED series if any
    fred_series = data_availability.get('FRED Economic Data', {}).get('series', [])
    if fred_series:
        summary += f"\n**FRED Data Series ({len(fred_series)} available):**\n"
        for series in fred_series[:10]:  # Show first 10
            series_name = series.replace('.csv', '').replace('_', ' ')
            summary += f"- {series_name}\n"
        if len(fred_series) > 10:
            summary += f"- ... and {len(fred_series) - 10} more series\n"
    
    return summary

def get_system_capabilities() -> Dict[str, Any]:
    """Get information about system capabilities and available tools"""
    
    capabilities = {
        'data_access': [
            'SEC regulatory filings (10-K, 8-K, insider trading)',
            'CFTC derivatives and swap data', 
            'Federal Reserve economic indicators',
            'Institutional investment holdings (13F)',
            'Private placement offerings (Form D)',
            'Money market fund data (N-series forms)'
        ],
        'analytics': [
            'Company profile analysis',
            'Market trend analysis', 
            'Risk assessment and exposure analysis',
            'Cross-dataset correlation studies',
            'Regulatory timeline analysis',
            'Institutional flow monitoring'
        ],
        'ai_features': [
            'Natural language queries',
            'Semantic search across datasets',
            'Vector embeddings for enhanced search',
            'Tool-enabled AI assistant (Raven)',
            'Automated data processing',
            'Cross-dataset relationship mapping'
        ],
        'data_management': [
            'Automated data downloading',
            'Database management and exports', 
            'Background task processing',
            'Data validation and quality checks',
            'Company watchlist management',
            'Historical data archiving'
        ]
    }
    
    # Check what tools are actually available
    available_tools = []
    try:
        from ..tools import TOOL_MAP
        available_tools = list(TOOL_MAP.keys())
    except ImportError:
        pass
    
    capabilities['available_tools'] = available_tools
    
    return capabilities

def get_data_access_summary() -> str:
    """Generate a comprehensive summary of data access for the RAG system"""
    
    try:
        data_info = get_available_data_sources()
        capabilities = get_system_capabilities()
        
        summary = f"""
I have access to a comprehensive financial data system with the following capabilities:

{data_info.get('summary', 'Data summary not available')}

🔧 **System Capabilities:**

**Data Access & Processing:**
{chr(10).join('• ' + cap for cap in capabilities['data_access'])}

**Analytics & Insights:**
{chr(10).join('• ' + cap for cap in capabilities['analytics'])}

**AI Features:**
{chr(10).join('• ' + cap for cap in capabilities['ai_features'])}

**Available Tools:** {len(capabilities.get('available_tools', []))} tools loaded
{chr(10).join('• ' + tool for tool in capabilities.get('available_tools', [])[:10])}

**Query Examples:**
• "Show me insider trading activity for Apple"
• "Analyze SOFR vs Fed Funds rate trends" 
• "What are the largest institutional holdings in tech?"
• "Compare swap market concentration across asset classes"
• "Search for companies in my watchlist"

The system can process natural language queries, execute complex analytics across multiple data sources, and provide insights with supporting evidence from the underlying data.
"""
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating data access summary: {e}")
        return f"Error accessing data summary: {e}"

if __name__ == "__main__":
    # Test the tools interface
    print("Testing Tools Interface...")
    
    data_sources = get_available_data_sources()
    print(f"Found {data_sources.get('total_tables', 0)} tables with {data_sources.get('total_records', 0):,} records")
    
    summary = get_data_access_summary()
    print(summary[:500] + "...")
