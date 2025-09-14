"""
Advanced Analytics Tools for GameCock AI
Provides structured SQL query capabilities with RAG integration
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from database import SessionLocal, CFTCSwap
from sqlalchemy import text, func, and_, or_
import ollama

class AnalyticsEngine:
    """Main analytics engine that combines SQL queries with AI analysis"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def execute_analytical_query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a structured analytical query and return results with AI insights"""
        
        query_handlers = {
            'market_trends': self._analyze_market_trends,
            'trading_positions': self._analyze_trading_positions,
            'risk_assessment': self._assess_risk,
            'company_comparison': self._compare_companies,
            'exposure_analysis': self._analyze_exposure,
            'swap_overview': self._swap_market_overview,
            'liquidity_analysis': self._analyze_liquidity
        }
        
        if query_type not in query_handlers:
            return {"error": f"Unknown query type: {query_type}"}
        
        try:
            # Execute the SQL analysis
            sql_results = query_handlers[query_type](params)
            
            # Generate AI insights from the results
            ai_insights = self._generate_ai_insights(query_type, sql_results, params)
            
            return {
                "query_type": query_type,
                "parameters": params,
                "sql_results": sql_results,
                "ai_insights": ai_insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Analytics error: {str(e)}"}
    
    def _analyze_market_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market trends over time"""
        
        # Default parameters
        days_back = params.get('days_back', 30)
        asset_class = params.get('asset_class', None)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Base query for trend analysis
        query = self.db.query(
            func.date(CFTCSwap.execution_timestamp).label('trade_date'),
            func.count(CFTCSwap.id).label('trade_count'),
            func.sum(CFTCSwap.notional_amount).label('total_notional'),
            func.avg(CFTCSwap.notional_amount).label('avg_notional'),
            CFTCSwap.asset_class
        ).filter(
            and_(
                CFTCSwap.execution_timestamp >= start_date,
                CFTCSwap.execution_timestamp <= end_date
            )
        )
        
        if asset_class:
            query = query.filter(CFTCSwap.asset_class == asset_class)
        
        query = query.group_by(
            func.date(CFTCSwap.execution_timestamp),
            CFTCSwap.asset_class
        ).order_by(func.date(CFTCSwap.execution_timestamp))
        
        results = query.all()
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'trade_date': r.trade_date,
            'trade_count': r.trade_count,
            'total_notional': float(r.total_notional or 0),
            'avg_notional': float(r.avg_notional or 0),
            'asset_class': r.asset_class
        } for r in results])
        
        # Calculate trend metrics
        trend_analysis = {}
        if not df.empty:
            # Daily growth rates
            df_summary = df.groupby('trade_date').agg({
                'trade_count': 'sum',
                'total_notional': 'sum'
            }).reset_index()
            
            if len(df_summary) > 1:
                df_summary['volume_change'] = df_summary['total_notional'].pct_change()
                df_summary['count_change'] = df_summary['trade_count'].pct_change()
                
                trend_analysis = {
                    'avg_daily_volume': df_summary['total_notional'].mean(),
                    'avg_daily_trades': df_summary['trade_count'].mean(),
                    'volume_volatility': df_summary['total_notional'].std(),
                    'last_7_days_growth': df_summary['volume_change'].tail(7).mean(),
                    'peak_volume_date': df_summary.loc[df_summary['total_notional'].idxmax(), 'trade_date'].isoformat(),
                    'peak_volume': df_summary['total_notional'].max()
                }
        
        return {
            'period': f"{start_date.date()} to {end_date.date()}",
            'total_records': len(results),
            'daily_data': df.to_dict('records') if not df.empty else [],
            'trend_metrics': trend_analysis,
            'asset_classes': df['asset_class'].unique().tolist() if not df.empty else []
        }
    
    def _analyze_trading_positions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trading positions and concentrations"""
        
        company_cik = params.get('company_cik', None)
        asset_class = params.get('asset_class', None)
        
        # Position analysis query
        query = self.db.query(
            CFTCSwap.asset_class,
            CFTCSwap.currency,
            func.count(CFTCSwap.id).label('position_count'),
            func.sum(CFTCSwap.notional_amount).label('total_exposure'),
            func.avg(CFTCSwap.notional_amount).label('avg_position_size'),
            func.min(CFTCSwap.notional_amount).label('min_position'),
            func.max(CFTCSwap.notional_amount).label('max_position')
        ).filter(CFTCSwap.notional_amount.isnot(None))
        
        if company_cik:
            # Note: You'll need to add company relationship to CFTC data
            pass  # Will implement once company mapping is added
            
        if asset_class:
            query = query.filter(CFTCSwap.asset_class == asset_class)
        
        query = query.group_by(CFTCSwap.asset_class, CFTCSwap.currency)
        results = query.all()
        
        # Calculate concentration metrics
        position_data = []
        total_exposure = 0
        
        for r in results:
            exposure = float(r.total_exposure or 0)
            total_exposure += exposure
            
            position_data.append({
                'asset_class': r.asset_class,
                'currency': r.currency,
                'position_count': r.position_count,
                'total_exposure': exposure,
                'avg_position_size': float(r.avg_position_size or 0),
                'min_position': float(r.min_position or 0),
                'max_position': float(r.max_position or 0)
            })
        
        # Calculate concentration ratios
        concentration_analysis = {}
        if position_data:
            sorted_positions = sorted(position_data, key=lambda x: x['total_exposure'], reverse=True)
            
            concentration_analysis = {
                'total_market_exposure': total_exposure,
                'top_3_concentration': sum(p['total_exposure'] for p in sorted_positions[:3]) / total_exposure if total_exposure > 0 else 0,
                'herfindahl_index': sum((p['total_exposure'] / total_exposure) ** 2 for p in position_data) if total_exposure > 0 else 0,
                'asset_class_count': len(set(p['asset_class'] for p in position_data)),
                'currency_count': len(set(p['currency'] for p in position_data))
            }
        
        return {
            'position_data': position_data,
            'concentration_analysis': concentration_analysis,
            'total_positions': len(position_data)
        }
    
    def _assess_risk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform risk assessment analysis"""
        
        # Placeholder for risk assessment logic
        # This would include:
        # - Counterparty concentration
        # - Maturity profile analysis
        # - Currency exposure
        # - Sector concentration
        
        return {
            "risk_metrics": {
                "counterparty_concentration": "Not yet implemented",
                "maturity_risk": "Not yet implemented",
                "currency_risk": "Not yet implemented"
            },
            "implementation_note": "Risk assessment features will be implemented as more data becomes available"
        }
    
    def _compare_companies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple companies across various metrics"""
        
        # Placeholder for company comparison
        return {
            "comparison_note": "Company comparison will be implemented once company-specific data mapping is established"
        }
    
    def _analyze_exposure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market exposure by various dimensions"""
        
        # Asset class exposure analysis
        exposure_query = self.db.query(
            CFTCSwap.asset_class,
            func.count(CFTCSwap.id).label('trade_count'),
            func.sum(CFTCSwap.notional_amount).label('total_notional')
        ).filter(CFTCSwap.notional_amount.isnot(None))
        
        exposure_query = exposure_query.group_by(CFTCSwap.asset_class)
        results = exposure_query.all()
        
        exposure_data = []
        total_notional = 0
        
        for r in results:
            notional = float(r.total_notional or 0)
            total_notional += notional
            
            exposure_data.append({
                'asset_class': r.asset_class,
                'trade_count': r.trade_count,
                'total_notional': notional
            })
        
        # Calculate percentages
        for item in exposure_data:
            item['percentage_of_total'] = (item['total_notional'] / total_notional * 100) if total_notional > 0 else 0
        
        return {
            'exposure_by_asset_class': exposure_data,
            'total_market_notional': total_notional,
            'asset_class_count': len(exposure_data)
        }
    
    def _swap_market_overview(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive swap market overview"""
        
        # Market size and activity
        overview_query = self.db.query(
            func.count(CFTCSwap.id).label('total_swaps'),
            func.sum(CFTCSwap.notional_amount).label('total_notional'),
            func.avg(CFTCSwap.notional_amount).label('avg_notional'),
            func.count(func.distinct(CFTCSwap.asset_class)).label('asset_classes'),
            func.count(func.distinct(CFTCSwap.currency)).label('currencies')
        ).filter(CFTCSwap.notional_amount.isnot(None))
        
        result = overview_query.first()
        
        return {
            'market_overview': {
                'total_swap_count': result.total_swaps or 0,
                'total_notional_amount': float(result.total_notional or 0),
                'average_swap_size': float(result.avg_notional or 0),
                'unique_asset_classes': result.asset_classes or 0,
                'unique_currencies': result.currencies or 0
            }
        }
    
    def _analyze_liquidity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market liquidity metrics"""
        
        # Liquidity analysis placeholder
        return {
            "liquidity_note": "Liquidity analysis will be enhanced with additional market data"
        }
    
    def _generate_ai_insights(self, query_type: str, sql_results: Dict[str, Any], params: Dict[str, Any]) -> str:
        """Generate AI-powered insights from SQL query results"""
        
        # Create a comprehensive prompt for the AI
        prompt = f"""
        As Raven, analyze the following {query_type} results and provide insights:

        Query Parameters: {json.dumps(params, indent=2)}
        
        SQL Results: {json.dumps(sql_results, indent=2, default=str)}
        
        Please provide:
        1. Key findings and trends
        2. Notable patterns or anomalies  
        3. Market implications
        4. Risk considerations
        5. Actionable recommendations
        
        Keep the analysis concise but thorough, suitable for financial professionals.
        """
        
        try:
            response = ollama.chat(
                model='raven-enhanced',
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"AI insight generation failed: {str(e)}"


# Analytics tool functions for the TOOL_MAP
def analyze_market_trends(days_back: int = 30, asset_class: str = None):
    """Analyze market trends over a specified period"""
    with AnalyticsEngine() as engine:
        results = engine.execute_analytical_query('market_trends', {
            'days_back': days_back,
            'asset_class': asset_class
        })
    return json.dumps(results, default=str)

def analyze_trading_positions(company_cik: str = None, asset_class: str = None):
    """Analyze trading positions and concentrations"""
    with AnalyticsEngine() as engine:
        results = engine.execute_analytical_query('trading_positions', {
            'company_cik': company_cik,
            'asset_class': asset_class
        })
    return json.dumps(results, default=str)

def risk_assessment(assessment_type: str = 'general'):
    """Perform risk assessment analysis"""
    with AnalyticsEngine() as engine:
        results = engine.execute_analytical_query('risk_assessment', {
            'assessment_type': assessment_type
        })
    return json.dumps(results, default=str)

def compare_companies(company_list: list):
    """Compare multiple companies across various metrics"""
    with AnalyticsEngine() as engine:
        results = engine.execute_analytical_query('company_comparison', {
            'companies': company_list
        })
    return json.dumps(results, default=str)

def exposure_analysis(dimension: str = 'asset_class'):
    """Analyze market exposure by various dimensions"""
    with AnalyticsEngine() as engine:
        results = engine.execute_analytical_query('exposure_analysis', {
            'dimension': dimension
        })
    return json.dumps(results, default=str)

def swap_market_overview():
    """Provide comprehensive swap market overview"""
    with AnalyticsEngine() as engine:
        results = engine.execute_analytical_query('swap_overview', {})
    return json.dumps(results, default=str)

def liquidity_analysis(timeframe: str = '30d'):
    """Analyze market liquidity metrics"""
    with AnalyticsEngine() as engine:
        results = engine.execute_analytical_query('liquidity_analysis', {
            'timeframe': timeframe
        })
    return json.dumps(results, default=str)


# Enhanced TOOL_MAP with analytics functions
ANALYTICS_TOOLS = {
    "analyze_market_trends": {
        "function": analyze_market_trends,
        "schema": {
            "name": "analyze_market_trends",
            "description": "Analyze market trends over a specified time period with AI insights",
            "parameters": {
                "type": "object",
                "properties": {
                    "days_back": {"type": "integer", "description": "Number of days to analyze (default: 30)"},
                    "asset_class": {"type": "string", "description": "Specific asset class to analyze (optional)"}
                },
                "required": []
            }
        }
    },
    "analyze_trading_positions": {
        "function": analyze_trading_positions,
        "schema": {
            "name": "analyze_trading_positions", 
            "description": "Analyze trading positions and concentration risks",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_cik": {"type": "string", "description": "Specific company CIK to analyze (optional)"},
                    "asset_class": {"type": "string", "description": "Specific asset class to analyze (optional)"}
                },
                "required": []
            }
        }
    },
    "risk_assessment": {
        "function": risk_assessment,
        "schema": {
            "name": "risk_assessment",
            "description": "Perform comprehensive risk assessment with AI analysis",
            "parameters": {
                "type": "object", 
                "properties": {
                    "assessment_type": {"type": "string", "description": "Type of risk assessment (default: 'general')"}
                },
                "required": []
            }
        }
    },
    "exposure_analysis": {
        "function": exposure_analysis,
        "schema": {
            "name": "exposure_analysis",
            "description": "Analyze market exposure across different dimensions",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimension": {"type": "string", "description": "Analysis dimension (default: 'asset_class')"}
                },
                "required": []
            }
        }
    },
    "swap_market_overview": {
        "function": swap_market_overview,
        "schema": {
            "name": "swap_market_overview", 
            "description": "Get comprehensive swap market overview with AI insights",
            "parameters": {"type": "object", "properties": {}}
        }
    }
}
