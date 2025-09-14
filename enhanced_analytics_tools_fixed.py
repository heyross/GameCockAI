"""
Enhanced Analytics Tools for GameCock AI - Fixed Version
Adapted to work with actual database schema and current data availability
"""

import json
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
# Import from the correct database module (GameCockAI/database.py)
try:
    from .database import SessionLocal, CFTCSwap
except ImportError:
    # Fallback for when running from GameCockAI directory  
    from database import SessionLocal, CFTCSwap
from sqlalchemy import text, func, and_, or_
import ollama

# Set up logging
logger = logging.getLogger(__name__)

# Error handling decorator for enhanced analytics tools
def handle_enhanced_analytics_errors(func):
    """Decorator to provide consistent error handling for enhanced analytics tools"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in enhanced analytics tool {func.__name__}: {str(e)}")
            return json.dumps({
                "error": f"Enhanced analytics tool execution failed: {str(e)}",
                "tool": func.__name__,
                "suggestion": "Please check your database connection and data availability"
            })
    return wrapper

class CrossDatasetAnalyticsEngine:
    """Advanced analytics engine adapted for current database structure"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def execute_cross_dataset_query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytical queries adapted to current database structure"""
        
        query_handlers = {
            'company_comprehensive_profile': self._get_company_profile_basic,
            'institutional_flow_analysis': self._placeholder_institutional_flow,
            'insider_activity_monitoring': self._placeholder_insider_activity,
            'swap_risk_assessment': self._assess_swap_risk_basic,
            'fund_stability_analysis': self._placeholder_fund_stability,
            'company_peer_analysis': self._placeholder_peer_analysis,
            'market_overview': self._market_overview_basic,
            'cftc_swap_analysis': self._analyze_cftc_swaps
        }
        
        if query_type not in query_handlers:
            return {"error": f"Unknown query type: {query_type}"}
        
        try:
            # Execute the analysis
            sql_results = query_handlers[query_type](params)
            
            # Generate AI insights from the results
            ai_insights = self._generate_ai_insights(query_type, sql_results, params)
            
            return {
                "query_type": query_type,
                "parameters": params,
                "sql_results": sql_results,
                "ai_insights": ai_insights,
                "timestamp": datetime.now().isoformat(),
                "data_sources": self._identify_data_sources(query_type)
            }
            
        except Exception as e:
            return {"error": f"Analytics error: {str(e)}"}
    
    def _get_company_profile_basic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Basic company profile using available data"""
        
        cik = params.get('cik', '').strip()
        
        if not cik:
            return {"message": "CIK parameter required for company analysis"}
        
        # Since most tables don't exist yet, provide a basic response
        return {
            "company_info": {
                "cik": cik,
                "analysis_note": "Company-specific analysis will be enhanced as more data sources are loaded"
            },
            "available_data_sources": ["CFTC Swap Data"],
            "recommendation": "Load SEC and Form data to enable comprehensive company analysis"
        }
    
    def _placeholder_institutional_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for institutional flow analysis"""
        return {
            "analysis_status": "Data source not available",
            "required_tables": ["form13f_submissions", "form13f_info_tables"],
            "recommendation": "Load Form 13F data to enable institutional flow analysis"
        }
    
    def _placeholder_insider_activity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for insider activity monitoring"""
        return {
            "analysis_status": "Data source not available", 
            "required_tables": ["sec_submissions", "sec_non_deriv_trans", "sec_reporting_owners"],
            "recommendation": "Load SEC insider transaction data to enable insider activity monitoring"
        }
    
    def _assess_swap_risk_basic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Basic swap risk assessment using available CFTC data"""
        
        risk_dimension = params.get('risk_dimension', 'asset_class')
        
        # Query available CFTC swap data
        basic_stats_query = text("""
            SELECT 
                asset_class,
                COUNT(*) as transaction_count,
                SUM(notional_amount) as total_notional,
                AVG(notional_amount) as avg_notional,
                MIN(execution_timestamp) as earliest_transaction,
                MAX(execution_timestamp) as latest_transaction,
                currency,
                COUNT(DISTINCT currency) as currency_diversity
            FROM cftc_swap_data
            WHERE notional_amount IS NOT NULL
            GROUP BY asset_class, currency
            ORDER BY total_notional DESC
        """)
        
        try:
            basic_stats = self.db.execute(basic_stats_query).fetchall()
            
            if not basic_stats:
                return {
                    "message": "No CFTC swap data found",
                    "recommendation": "Load CFTC swap data to enable risk assessment"
                }
            
            # Convert to list of dictionaries
            stats_data = [dict(row._mapping) for row in basic_stats]
            
            # Calculate some basic risk metrics
            total_notional = sum(float(row.get('total_notional', 0) or 0) for row in stats_data)
            asset_classes = set(row.get('asset_class') for row in stats_data if row.get('asset_class'))
            
            return {
                "basic_risk_metrics": {
                    "total_notional_amount": total_notional,
                    "asset_class_count": len(asset_classes),
                    "asset_classes": list(asset_classes),
                    "total_transactions": sum(int(row.get('transaction_count', 0) or 0) for row in stats_data)
                },
                "detailed_stats": stats_data,
                "analysis_note": "Basic analysis using available CFTC swap data"
            }
            
        except Exception as e:
            return {"error": f"CFTC swap analysis failed: {str(e)}"}
    
    def _placeholder_fund_stability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for fund stability analysis"""
        return {
            "analysis_status": "Data source not available",
            "required_tables": ["nmfp_submissions", "nmfp_series_level_info"],
            "recommendation": "Load N-MFP money market fund data to enable stability analysis"
        }
    
    def _placeholder_peer_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for peer analysis"""
        return {
            "analysis_status": "Data source not available",
            "required_tables": ["sec_10k_submissions", "sec_8k_submissions"],
            "recommendation": "Load SEC filing data to enable peer comparison analysis"
        }
    
    def _market_overview_basic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Basic market overview using available data"""
        
        # Get basic database statistics
        overview_query = text("""
            SELECT 
                COUNT(*) as total_swaps,
                COUNT(DISTINCT asset_class) as asset_classes,
                COUNT(DISTINCT currency) as currencies,
                SUM(notional_amount) as total_notional,
                AVG(notional_amount) as avg_notional,
                MIN(execution_timestamp) as earliest_date,
                MAX(execution_timestamp) as latest_date
            FROM cftc_swap_data
            WHERE notional_amount IS NOT NULL
        """)
        
        try:
            overview_result = self.db.execute(overview_query).fetchone()
            
            if overview_result:
                return {
                    "market_overview": dict(overview_result._mapping),
                    "data_source": "CFTC Swap Data",
                    "coverage_note": "Overview based on available CFTC swap transaction data"
                }
            else:
                return {
                    "message": "No market data available",
                    "recommendation": "Load financial data to enable market overview"
                }
                
        except Exception as e:
            return {"error": f"Market overview failed: {str(e)}"}
    
    def _analyze_cftc_swaps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed CFTC swap analysis"""
        
        timeframe_days = params.get('timeframe_days', 30)
        
        # Time-based analysis
        time_analysis_query = text("""
            SELECT 
                date(execution_timestamp) as trade_date,
                COUNT(*) as daily_trades,
                SUM(notional_amount) as daily_notional,
                asset_class
            FROM cftc_swap_data
            WHERE execution_timestamp >= date('now', '-:days days')
            AND notional_amount IS NOT NULL
            GROUP BY date(execution_timestamp), asset_class
            ORDER BY trade_date DESC
        """)
        
        try:
            time_analysis = self.db.execute(time_analysis_query, {"days": timeframe_days}).fetchall()
            
            return {
                "time_series_analysis": [dict(row._mapping) for row in time_analysis],
                "analysis_period_days": timeframe_days,
                "data_source": "CFTC Swap Data"
            }
            
        except Exception as e:
            return {"error": f"CFTC swap analysis failed: {str(e)}"}
    
    def _identify_data_sources(self, query_type: str) -> List[str]:
        """Identify which data sources are available/required"""
        
        source_mapping = {
            'company_comprehensive_profile': ['CFTC Swap Data (limited)'],
            'institutional_flow_analysis': ['Form 13F Data (not loaded)'],
            'insider_activity_monitoring': ['SEC Insider Data (not loaded)'],
            'swap_risk_assessment': ['CFTC Swap Data'],
            'fund_stability_analysis': ['N-MFP Fund Data (not loaded)'],
            'company_peer_analysis': ['SEC Filing Data (not loaded)'],
            'market_overview': ['CFTC Swap Data'],
            'cftc_swap_analysis': ['CFTC Swap Data']
        }
        
        return source_mapping.get(query_type, ['Unknown'])
    
    def _generate_ai_insights(self, query_type: str, sql_results: Dict[str, Any], params: Dict[str, Any]) -> str:
        """Generate AI insights adapted to available data"""
        
        prompt = f"""
        As Raven, analyze the following {query_type} results from the GameCock financial database:

        Query Type: {query_type}
        Parameters: {json.dumps(params, indent=2)}
        Data Sources: {', '.join(self._identify_data_sources(query_type))}
        
        Results: {json.dumps(sql_results, indent=2, default=str)[:2000]}
        
        Please provide:
        1. Analysis of available data and key insights
        2. Data limitations and what's missing
        3. Recommendations for enhancing the analysis
        4. Actionable next steps
        
        Keep the response concise and focused on what can be determined from the available data.
        """
        
        try:
            response = ollama.chat(
                model='raven-enhanced',
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"AI insight generation not available: {str(e)}"


# Fixed analytics functions that work with current database structure
@handle_enhanced_analytics_errors
def comprehensive_company_analysis(cik: str, include_subsidiaries: bool = True):
    """Company analysis adapted to available data"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('company_comprehensive_profile', {
                'cik': cik,
                'include_subsidiaries': include_subsidiaries
            })
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Comprehensive company analysis failed: {str(e)}")
        return json.dumps({
            "error": "Comprehensive company analysis failed",
            "suggestion": "Please check your database connection and data availability"
        })

@handle_enhanced_analytics_errors
def institutional_flow_analysis(timeframe_days: int = 90, min_position_value: float = 1000000):
    """Institutional flow analysis placeholder"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('institutional_flow_analysis', {
                'timeframe_days': timeframe_days,
                'min_position_value': min_position_value
            })
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Institutional flow analysis failed: {str(e)}")
        return json.dumps({
            "error": "Institutional flow analysis failed",
            "suggestion": "Please check your database connection and data availability"
        })

@handle_enhanced_analytics_errors
def insider_activity_monitoring(analysis_type: str = "unusual_activity", lookback_days: int = 30):
    """Insider activity monitoring placeholder"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('insider_activity_monitoring', {
                'analysis_type': analysis_type,
                'lookback_days': lookback_days
            })
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Insider activity monitoring failed: {str(e)}")
        return json.dumps({
            "error": "Insider activity monitoring failed",
            "suggestion": "Please check your database connection and data availability"
        })

@handle_enhanced_analytics_errors
def swap_risk_assessment(risk_dimension: str = "asset_class", aggregation_level: str = "weekly"):
    """CFTC swap risk assessment using available data"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('swap_risk_assessment', {
                'risk_dimension': risk_dimension,
                'aggregation_level': aggregation_level
            })
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Swap risk assessment failed: {str(e)}")
        return json.dumps({
            "error": "Swap risk assessment failed",
            "suggestion": "Please check your database connection and data availability"
        })

@handle_enhanced_analytics_errors
def fund_stability_analysis(fund_category: str = "all", stress_scenario: bool = False):
    """Fund stability analysis placeholder"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('fund_stability_analysis', {
                'fund_category': fund_category,
                'stress_scenario': stress_scenario
            })
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Fund stability analysis failed: {str(e)}")
        return json.dumps({
            "error": "Fund stability analysis failed",
            "suggestion": "Please check your database connection and data availability"
        })

@handle_enhanced_analytics_errors
def company_peer_analysis(cik: str, peer_selection: str = "industry"):
    """Company peer analysis placeholder"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('company_peer_analysis', {
                'cik': cik,
                'peer_selection': peer_selection
            })
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Company peer analysis failed: {str(e)}")
        return json.dumps({
            "error": "Company peer analysis failed",
            "suggestion": "Please check your database connection and data availability"
        })

@handle_enhanced_analytics_errors
def market_overview_analysis():
    """Basic market overview using available CFTC data"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('market_overview', {})
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Market overview analysis failed: {str(e)}")
        return json.dumps({
            "error": "Market overview analysis failed",
            "suggestion": "Please check your database connection and data availability"
        })

@handle_enhanced_analytics_errors
def cftc_swap_analysis(timeframe_days: int = 30):
    """Detailed CFTC swap analysis"""
    try:
        with CrossDatasetAnalyticsEngine() as engine:
            results = engine.execute_cross_dataset_query('cftc_swap_analysis', {
                'timeframe_days': timeframe_days
            })
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"CFTC swap analysis failed: {str(e)}")
        return json.dumps({
            "error": "CFTC swap analysis failed",
            "suggestion": "Please check your database connection and data availability"
        })

# Fixed TOOL_MAP with working functions
ENHANCED_ANALYTICS_TOOLS_FIXED = {
    "comprehensive_company_analysis": {
        "function": comprehensive_company_analysis,
        "schema": {
            "name": "comprehensive_company_analysis",
            "description": "Company analysis using available financial data sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "cik": {"type": "string", "description": "Company CIK identifier (required)"},
                    "include_subsidiaries": {"type": "boolean", "description": "Include subsidiary analysis (default: true)"}
                },
                "required": ["cik"]
            }
        }
    },
    "swap_risk_assessment": {
        "function": swap_risk_assessment,
        "schema": {
            "name": "swap_risk_assessment",
            "description": "CFTC swap market risk analysis using available swap transaction data",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_dimension": {"type": "string", "description": "Risk analysis dimension: 'asset_class', 'currency', 'notional' (default: 'asset_class')"},
                    "aggregation_level": {"type": "string", "description": "Time aggregation: 'daily', 'weekly', 'monthly' (default: 'weekly')"}
                },
                "required": []
            }
        }
    },
    "market_overview_analysis": {
        "function": market_overview_analysis,
        "schema": {
            "name": "market_overview_analysis",
            "description": "Basic market overview using available CFTC swap data",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    "cftc_swap_analysis": {
        "function": cftc_swap_analysis,
        "schema": {
            "name": "cftc_swap_analysis",
            "description": "Detailed analysis of CFTC swap transactions over time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeframe_days": {"type": "integer", "description": "Analysis timeframe in days (default: 30)"}
                },
                "required": []
            }
        }
    },
    "institutional_flow_analysis": {
        "function": institutional_flow_analysis,
        "schema": {
            "name": "institutional_flow_analysis",
            "description": "Institutional flow analysis (placeholder - requires Form 13F data)",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeframe_days": {"type": "integer", "description": "Analysis timeframe (default: 90)"},
                    "min_position_value": {"type": "number", "description": "Minimum position value (default: 1000000)"}
                },
                "required": []
            }
        }
    },
    "insider_activity_monitoring": {
        "function": insider_activity_monitoring,
        "schema": {
            "name": "insider_activity_monitoring",
            "description": "Insider activity monitoring (placeholder - requires SEC insider data)",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_type": {"type": "string", "description": "Analysis type (default: 'unusual_activity')"},
                    "lookback_days": {"type": "integer", "description": "Lookback period (default: 30)"}
                },
                "required": []
            }
        }
    }
}
