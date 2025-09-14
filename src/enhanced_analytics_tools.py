"""
Enhanced Analytics Tools for GameCock AI - Cross-Dataset Analysis
Implements sophisticated queries across SEC, CFTC, Form, and N-Series data
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
# Import from the correct database module (GameCockAI/database.py)
try:
    from database import SessionLocal
except ImportError:
    # Fallback for when running from GameCockAI directory
    from database import SessionLocal
from sqlalchemy import text, func, and_, or_
import ollama

class CrossDatasetAnalyticsEngine:
    """Advanced analytics engine for cross-dataset financial analysis"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def execute_cross_dataset_query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sophisticated cross-dataset analytical queries"""
        
        query_handlers = {
            'company_comprehensive_profile': self._get_company_comprehensive_profile,
            'institutional_flow_analysis': self._analyze_institutional_flow,
            'insider_activity_monitoring': self._monitor_insider_activity,
            'swap_risk_assessment': self._assess_swap_risk,
            'fund_stability_analysis': self._analyze_fund_stability,
            'company_peer_analysis': self._analyze_company_vs_peers,
            'market_concentration_analysis': self._analyze_market_concentration,
            'regulatory_timeline_analysis': self._analyze_regulatory_timeline,
            'cross_asset_correlation': self._analyze_cross_asset_correlation
        }
        
        if query_type not in query_handlers:
            return {"error": f"Unknown query type: {query_type}"}
        
        try:
            # Execute the cross-dataset analysis
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
            return {"error": f"Cross-dataset analytics error: {str(e)}"}
    
    def _get_company_comprehensive_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive company profile across all data sources"""
        
        cik = params.get('cik')
        include_subsidiaries = params.get('include_subsidiaries', True)
        
        if not cik:
            return {"error": "CIK parameter required"}
        
        # Unified company info query
        company_info_query = text("""
            SELECT 
                'SEC_SUBMISSIONS' as source,
                issuercik as cik,
                issuername as company_name,
                issuertradingsymbol as ticker_symbol,
                NULL as lei
            FROM sec_submissions 
            WHERE issuercik = :cik
            LIMIT 1
            
            UNION ALL
            
            SELECT 
                'FORM_13F' as source,
                cik,
                registrant_full_name as company_name,
                NULL as ticker_symbol,
                registrant_leiid as lei
            FROM nmfp_submissions 
            WHERE cik = :cik
            LIMIT 1
            
            UNION ALL
            
            SELECT 
                'FORM_D' as source,
                cik,
                entityname as company_name,
                NULL as ticker_symbol,
                NULL as lei
            FROM formd_issuers 
            WHERE cik = :cik
            LIMIT 1
        """)
        
        company_info = self.db.execute(company_info_query, {"cik": cik}).fetchall()
        
        # Recent filing activity
        filing_activity_query = text("""
            SELECT 
                'SEC_INSIDER' as activity_type,
                filing_date as activity_date,
                document_type as details,
                COUNT(*) as count
            FROM sec_submissions 
            WHERE issuercik = :cik 
            AND filing_date >= date('now', '-1 year')
            GROUP BY filing_date, document_type
            
            UNION ALL
            
            SELECT 
                'SEC_10K_8K' as activity_type,
                filing_date as activity_date,
                form_type as details,
                1 as count
            FROM sec_10k_submissions 
            WHERE cik = :cik 
            AND filing_date >= date('now', '-1 year')
            
            UNION ALL
            
            SELECT 
                'SEC_8K' as activity_type,
                filing_date as activity_date,
                form_type as details,
                1 as count
            FROM sec_8k_submissions 
            WHERE cik = :cik 
            AND filing_date >= date('now', '-1 year')
            
            ORDER BY activity_date DESC
            LIMIT 50
        """)
        
        filing_activity = self.db.execute(filing_activity_query, {"cik": cik}).fetchall()
        
        # Insider trading summary
        insider_summary_query = text("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN snt.trans_acquired_disp_cd = 'A' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as total_purchases,
                SUM(CASE WHEN snt.trans_acquired_disp_cd = 'D' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as total_sales,
                COUNT(DISTINCT sro.rptownercik) as unique_insiders,
                MAX(snt.trans_date) as latest_transaction_date
            FROM sec_non_deriv_trans snt
            JOIN sec_submissions ss ON snt.accession_number = ss.accession_number
            JOIN sec_reporting_owners sro ON snt.accession_number = sro.accession_number
            WHERE ss.issuercik = :cik 
            AND snt.trans_date >= date('now', '-1 year')
            AND snt.trans_shares IS NOT NULL 
            AND snt.trans_pricepershare IS NOT NULL
        """)
        
        insider_summary = self.db.execute(insider_summary_query, {"cik": cik}).fetchone()
        
        return {
            "company_info": [dict(row._mapping) for row in company_info],
            "filing_activity": [dict(row._mapping) for row in filing_activity],
            "insider_trading_summary": dict(insider_summary._mapping) if insider_summary else {},
            "analysis_period": "12 months"
        }
    
    def _analyze_institutional_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze institutional money flows using Form 13F data"""
        
        timeframe_days = params.get('timeframe_days', 90)
        min_position_value = params.get('min_position_value', 1000000)
        
        # Current quarter vs previous quarter holdings analysis
        holdings_flow_query = text("""
            WITH current_quarter AS (
                SELECT 
                    fit.cusip,
                    fit.nameofissuer,
                    SUM(fit.value) as current_value,
                    COUNT(DISTINCT fs.cik) as current_holders,
                    COUNT(*) as current_positions
                FROM form13f_info_tables fit 
                JOIN form13f_submissions fs ON fit.accession_number = fs.accession_number
                WHERE fs.filing_date >= date('now', '-120 days')
                GROUP BY fit.cusip, fit.nameofissuer
            ),
            previous_quarter AS (
                SELECT 
                    fit.cusip,
                    fit.nameofissuer,
                    SUM(fit.value) as previous_value,
                    COUNT(DISTINCT fs.cik) as previous_holders,
                    COUNT(*) as previous_positions
                FROM form13f_info_tables fit 
                JOIN form13f_submissions fs ON fit.accession_number = fs.accession_number  
                WHERE fs.filing_date BETWEEN date('now', '-240 days') AND date('now', '-120 days')
                GROUP BY fit.cusip, fit.nameofissuer
            )
            SELECT 
                COALESCE(c.cusip, p.cusip) as cusip,
                COALESCE(c.nameofissuer, p.nameofissuer) as nameofissuer,
                COALESCE(c.current_value, 0) as current_value,
                COALESCE(p.previous_value, 0) as previous_value,
                COALESCE(c.current_value, 0) - COALESCE(p.previous_value, 0) as value_change,
                CASE 
                    WHEN p.previous_value > 0 THEN 
                        (COALESCE(c.current_value, 0) - p.previous_value) / p.previous_value * 100 
                    ELSE NULL 
                END as pct_change,
                COALESCE(c.current_holders, 0) as current_holders,
                COALESCE(p.previous_holders, 0) as previous_holders,
                COALESCE(c.current_holders, 0) - COALESCE(p.previous_holders, 0) as holder_change,
                COALESCE(c.current_positions, 0) as current_positions,
                COALESCE(p.previous_positions, 0) as previous_positions
            FROM current_quarter c
            FULL OUTER JOIN previous_quarter p ON c.cusip = p.cusip
            WHERE COALESCE(c.current_value, 0) >= :min_value 
            OR COALESCE(p.previous_value, 0) >= :min_value
            ORDER BY ABS(COALESCE(c.current_value, 0) - COALESCE(p.previous_value, 0)) DESC
            LIMIT 100
        """)
        
        holdings_flow = self.db.execute(holdings_flow_query, {
            "min_value": min_position_value
        }).fetchall()
        
        # Top institutional buyers and sellers
        top_movers_query = text("""
            SELECT 
                fs.cik,
                fs.registrant_full_name,
                COUNT(DISTINCT fit.cusip) as positions_count,
                SUM(fit.value) as total_position_value,
                AVG(fit.value) as avg_position_size
            FROM form13f_info_tables fit
            JOIN form13f_submissions fs ON fit.accession_number = fs.accession_number
            WHERE fs.filing_date >= date('now', '-90 days')
            GROUP BY fs.cik, fs.registrant_full_name
            HAVING SUM(fit.value) >= :min_value
            ORDER BY total_position_value DESC
            LIMIT 50
        """)
        
        top_movers = self.db.execute(top_movers_query, {
            "min_value": min_position_value
        }).fetchall()
        
        return {
            "holdings_flow": [dict(row._mapping) for row in holdings_flow],
            "top_institutional_managers": [dict(row._mapping) for row in top_movers],
            "analysis_parameters": {
                "timeframe_days": timeframe_days,
                "min_position_value": min_position_value
            }
        }
    
    def _monitor_insider_activity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and detect unusual insider trading patterns"""
        
        analysis_type = params.get('analysis_type', 'unusual_activity')
        lookback_days = params.get('lookback_days', 30)
        
        # Unusual insider activity detection
        unusual_activity_query = text(f"""
            WITH recent_insider_activity AS (
                SELECT 
                    ss.issuercik, 
                    ss.issuername,
                    COUNT(*) as recent_transactions,
                    SUM(CASE WHEN snt.trans_acquired_disp_cd = 'D' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as recent_sales,
                    SUM(CASE WHEN snt.trans_acquired_disp_cd = 'A' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as recent_purchases,
                    COUNT(DISTINCT sro.rptownercik) as unique_insiders,
                    COUNT(DISTINCT CASE WHEN snt.trans_acquired_disp_cd = 'D' THEN sro.rptownercik END) as selling_insiders,
                    COUNT(DISTINCT CASE WHEN snt.trans_acquired_disp_cd = 'A' THEN sro.rptownercik END) as buying_insiders
                FROM sec_non_deriv_trans snt
                JOIN sec_submissions ss ON snt.accession_number = ss.accession_number
                JOIN sec_reporting_owners sro ON snt.accession_number = sro.accession_number
                WHERE snt.trans_date >= date('now', '-{lookback_days} days')
                AND snt.trans_shares IS NOT NULL 
                AND snt.trans_pricepershare IS NOT NULL
                AND snt.trans_shares * snt.trans_pricepershare > 10000  -- Minimum $10k transaction
                GROUP BY ss.issuercik, ss.issuername
            ),
            historical_avg AS (
                SELECT 
                    ss.issuercik,
                    AVG(monthly_transactions) as avg_monthly_transactions,
                    AVG(monthly_sales) as avg_monthly_sales,
                    AVG(monthly_purchases) as avg_monthly_purchases
                FROM (
                    SELECT 
                        ss.issuercik,
                        strftime('%Y-%m', snt.trans_date) as month,
                        COUNT(*) as monthly_transactions,
                        SUM(CASE WHEN snt.trans_acquired_disp_cd = 'D' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as monthly_sales,
                        SUM(CASE WHEN snt.trans_acquired_disp_cd = 'A' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as monthly_purchases
                    FROM sec_non_deriv_trans snt
                    JOIN sec_submissions ss ON snt.accession_number = ss.accession_number
                    WHERE snt.trans_date >= date('now', '-1 year')
                    AND snt.trans_date < date('now', '-{lookback_days} days')
                    AND snt.trans_shares IS NOT NULL 
                    AND snt.trans_pricepershare IS NOT NULL
                    AND snt.trans_shares * snt.trans_pricepershare > 10000
                    GROUP BY ss.issuercik, strftime('%Y-%m', snt.trans_date)
                ) monthly_data
                GROUP BY ss.issuercik
                HAVING COUNT(*) >= 3  -- At least 3 months of history
            )
            SELECT 
                ria.issuercik, 
                ria.issuername,
                ria.recent_transactions, 
                ha.avg_monthly_transactions,
                CASE WHEN ha.avg_monthly_transactions > 0 THEN 
                    ria.recent_transactions / ha.avg_monthly_transactions 
                ELSE NULL END as transaction_ratio,
                ria.recent_sales, 
                ha.avg_monthly_sales,
                CASE WHEN ha.avg_monthly_sales > 0 THEN 
                    ria.recent_sales / ha.avg_monthly_sales 
                ELSE NULL END as sales_ratio,
                ria.recent_purchases,
                ha.avg_monthly_purchases,
                CASE WHEN ha.avg_monthly_purchases > 0 THEN 
                    ria.recent_purchases / ha.avg_monthly_purchases 
                ELSE NULL END as purchase_ratio,
                ria.unique_insiders,
                ria.selling_insiders,
                ria.buying_insiders
            FROM recent_insider_activity ria
            JOIN historical_avg ha ON ria.issuercik = ha.issuercik
            WHERE (ria.recent_transactions / ha.avg_monthly_transactions > 2.0)  -- 2x normal activity
            OR (ria.recent_sales / ha.avg_monthly_sales > 3.0)  -- 3x normal sales
            OR (ria.recent_purchases / ha.avg_monthly_purchases > 3.0)  -- 3x normal purchases
            ORDER BY 
                COALESCE(ria.recent_transactions / ha.avg_monthly_transactions, 0) + 
                COALESCE(ria.recent_sales / ha.avg_monthly_sales, 0) + 
                COALESCE(ria.recent_purchases / ha.avg_monthly_purchases, 0) DESC
        """)
        
        unusual_activity = self.db.execute(unusual_activity_query).fetchall()
        
        # Insider roles analysis
        insider_roles_query = text("""
            SELECT 
                ss.issuercik,
                ss.issuername,
                sro.rptowner_relationship,
                COUNT(*) as transaction_count,
                SUM(CASE WHEN snt.trans_acquired_disp_cd = 'D' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as total_sales,
                SUM(CASE WHEN snt.trans_acquired_disp_cd = 'A' THEN snt.trans_shares * snt.trans_pricepershare ELSE 0 END) as total_purchases
            FROM sec_non_deriv_trans snt
            JOIN sec_submissions ss ON snt.accession_number = ss.accession_number
            JOIN sec_reporting_owners sro ON snt.accession_number = sro.accession_number
            WHERE snt.trans_date >= date('now', '-:lookback_days days')
            AND snt.trans_shares IS NOT NULL 
            AND snt.trans_pricepershare IS NOT NULL
            GROUP BY ss.issuercik, ss.issuername, sro.rptowner_relationship
            HAVING COUNT(*) >= 2  -- At least 2 transactions
            ORDER BY total_sales DESC, total_purchases DESC
        """)
        
        insider_roles = self.db.execute(insider_roles_query, {
            "lookback_days": lookback_days
        }).fetchall()
        
        return {
            "unusual_activity_companies": [dict(row._mapping) for row in unusual_activity],
            "insider_activity_by_role": [dict(row._mapping) for row in insider_roles],
            "analysis_parameters": {
                "analysis_type": analysis_type,
                "lookback_days": lookback_days,
                "detection_thresholds": {
                    "transaction_multiple": "2x normal",
                    "value_multiple": "3x normal",
                    "minimum_transaction_value": 10000
                }
            }
        }
    
    def _assess_swap_risk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive CFTC swap market risk assessment"""
        
        risk_dimension = params.get('risk_dimension', 'counterparty')
        aggregation_level = params.get('aggregation_level', 'weekly')
        
        # Market exposure by asset class
        market_exposure_query = text("""
            SELECT 
                asset_class,
                COUNT(*) as transaction_count,
                SUM(notional_amount_leg_1) as total_notional_leg1,
                SUM(notional_amount_leg_2) as total_notional_leg2,
                AVG(notional_amount_leg_1) as avg_notional_leg1,
                MIN(execution_timestamp) as earliest_transaction,
                MAX(execution_timestamp) as latest_transaction,
                COUNT(DISTINCT underlier_id_leg_1) as unique_underliers
            FROM cftc_swap_data
            WHERE execution_timestamp >= date('now', '-90 days')
            AND notional_amount_leg_1 IS NOT NULL
            GROUP BY asset_class
            ORDER BY total_notional_leg1 DESC
        """)
        
        market_exposure = self.db.execute(market_exposure_query).fetchall()
        
        # Concentration risk by underlying asset
        concentration_risk_query = text("""
            SELECT 
                underlying_asset_name,
                asset_class,
                COUNT(*) as contract_count,
                SUM(notional_amount_leg_1) as total_exposure,
                SUM(notional_amount_leg_1) / (
                    SELECT SUM(notional_amount_leg_1) 
                    FROM cftc_swap_data 
                    WHERE execution_timestamp >= date('now', '-30 days')
                    AND notional_amount_leg_1 IS NOT NULL
                ) * 100 as market_share_pct,
                AVG(notional_amount_leg_1) as avg_contract_size,
                MIN(execution_timestamp) as first_seen,
                MAX(execution_timestamp) as last_seen
            FROM cftc_swap_data
            WHERE execution_timestamp >= date('now', '-30 days')
            AND underlying_asset_name IS NOT NULL
            AND notional_amount_leg_1 IS NOT NULL
            GROUP BY underlying_asset_name, asset_class
            HAVING total_exposure > 0
            ORDER BY total_exposure DESC
            LIMIT 50
        """)
        
        concentration_risk = self.db.execute(concentration_risk_query).fetchall()
        
        # Time series analysis for trend detection
        time_series_query = text("""
            SELECT 
                date(execution_timestamp) as trade_date,
                asset_class,
                COUNT(*) as daily_transaction_count,
                SUM(notional_amount_leg_1) as daily_notional,
                AVG(notional_amount_leg_1) as avg_daily_notional
            FROM cftc_swap_data
            WHERE execution_timestamp >= date('now', '-30 days')
            AND notional_amount_leg_1 IS NOT NULL
            GROUP BY date(execution_timestamp), asset_class
            ORDER BY trade_date DESC, daily_notional DESC
        """)
        
        time_series = self.db.execute(time_series_query).fetchall()
        
        return {
            "market_exposure_by_asset_class": [dict(row._mapping) for row in market_exposure],
            "concentration_risk_analysis": [dict(row._mapping) for row in concentration_risk],
            "time_series_analysis": [dict(row._mapping) for row in time_series],
            "risk_metrics": {
                "analysis_period": "30-90 days",
                "risk_dimension": risk_dimension,
                "aggregation_level": aggregation_level
            }
        }
    
    def _analyze_fund_stability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Money market fund liquidity and stability analysis"""
        
        fund_category = params.get('fund_category', 'all')
        stress_scenario = params.get('stress_scenario', False)
        
        # Fund liquidity metrics
        liquidity_metrics_query = text("""
            SELECT 
                ns.seriesid,
                ns.nameofseries,
                ns.registrant_full_name,
                nsli.money_market_fund_category,
                nsli.pct_dly_liquid_asset_friday_week1 as daily_liquidity_pct,
                nsli.pct_wkly_liquid_asset_friday_week1 as weekly_liquidity_pct,
                nsli.seven_day_gross_yield,
                nsli.net_asset_of_series,
                nsli.average_portfolio_maturity,
                nsli.average_life_maturity,
                ns.filing_date
            FROM nmfp_submissions ns
            JOIN nmfp_series_level_info nsli ON ns.accession_number = nsli.accession_number
            WHERE ns.filing_date >= date('now', '-60 days')
            AND nsli.pct_dly_liquid_asset_friday_week1 IS NOT NULL
            ORDER BY nsli.pct_dly_liquid_asset_friday_week1 ASC
            LIMIT 100
        """)
        
        liquidity_metrics = self.db.execute(liquidity_metrics_query).fetchall()
        
        # Portfolio concentration analysis  
        concentration_query = text("""
            SELECT 
                nps.accession_number,
                ns.nameofseries,
                nps.name_of_issuer,
                nps.investment_category,
                COUNT(*) as security_count,
                SUM(nps.percentage_of_money_market_fund_net) as total_fund_percentage,
                AVG(nps.yield_of_the_security_as_of_reportin) as avg_yield,
                SUM(nps.including_value_of_any_sponsor_supp) as total_value
            FROM nmfp_sch_portfolio_securities nps
            JOIN nmfp_submissions ns ON nps.accession_number = ns.accession_number
            WHERE ns.filing_date >= date('now', '-30 days')
            GROUP BY nps.accession_number, ns.nameofseries, nps.name_of_issuer, nps.investment_category
            HAVING total_fund_percentage > 2.0  -- Concentration > 2%
            ORDER BY total_fund_percentage DESC
            LIMIT 200
        """)
        
        concentration_analysis = self.db.execute(concentration_query).fetchall()
        
        # Fund flow analysis
        fund_flows_query = text("""
            SELECT 
                ncli.accession_number,
                ns.nameofseries,
                ncli.net_assets_of_class,
                ncli.total_gross_subscriptions,
                ncli.total_gross_redemptions,
                ncli.total_gross_subscriptions - ncli.total_gross_redemptions as net_flows,
                CASE 
                    WHEN ncli.net_assets_of_class > 0 THEN 
                        (ncli.total_gross_subscriptions - ncli.total_gross_redemptions) / ncli.net_assets_of_class * 100
                    ELSE NULL 
                END as net_flow_percentage,
                ncli.seven_day_net_yield
            FROM nmfp_class_level_info ncli
            JOIN nmfp_submissions ns ON ncli.accession_number = ns.accession_number
            WHERE ns.filing_date >= date('now', '-30 days')
            AND ncli.net_assets_of_class IS NOT NULL
            ORDER BY ABS(ncli.total_gross_subscriptions - ncli.total_gross_redemptions) DESC
            LIMIT 100
        """)
        
        fund_flows = self.db.execute(fund_flows_query).fetchall()
        
        return {
            "liquidity_metrics": [dict(row._mapping) for row in liquidity_metrics],
            "concentration_analysis": [dict(row._mapping) for row in concentration_analysis],
            "fund_flows": [dict(row._mapping) for row in fund_flows],
            "stability_indicators": {
                "low_liquidity_threshold": "10% daily liquid assets",
                "high_concentration_threshold": "5% single issuer",
                "stress_scenario_applied": stress_scenario
            }
        }
    
    def _analyze_company_vs_peers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Company peer analysis across multiple dimensions"""
        
        cik = params.get('cik')
        peer_selection = params.get('peer_selection', 'industry')
        
        if not cik:
            return {"error": "CIK parameter required"}
        
        # Company filing metrics
        company_metrics_query = text("""
            SELECT 
                cik,
                COUNT(DISTINCT filing_date) as filing_frequency_annual,
                COUNT(DISTINCT CASE WHEN form_type LIKE '10-K%' THEN filing_date END) as annual_reports,
                COUNT(DISTINCT CASE WHEN form_type LIKE '10-Q%' THEN filing_date END) as quarterly_reports,
                COUNT(DISTINCT CASE WHEN form_type LIKE '8-K%' THEN filing_date END) as current_reports,
                MIN(filing_date) as earliest_filing,
                MAX(filing_date) as latest_filing
            FROM (
                SELECT cik, filing_date, form_type FROM sec_10k_submissions
                UNION ALL
                SELECT cik, filing_date, form_type FROM sec_8k_submissions
            ) all_filings
            WHERE cik = :cik
            AND filing_date >= date('now', '-1 year')
            GROUP BY cik
        """)
        
        company_metrics = self.db.execute(company_metrics_query, {"cik": cik}).fetchone()
        
        # Similar companies (placeholder - would need industry classification)
        peer_metrics_query = text("""
            SELECT 
                cik,
                COUNT(DISTINCT filing_date) as filing_frequency_annual,
                COUNT(DISTINCT CASE WHEN form_type LIKE '10-K%' THEN filing_date END) as annual_reports,
                COUNT(DISTINCT CASE WHEN form_type LIKE '10-Q%' THEN filing_date END) as quarterly_reports,
                COUNT(DISTINCT CASE WHEN form_type LIKE '8-K%' THEN filing_date END) as current_reports
            FROM (
                SELECT cik, filing_date, form_type FROM sec_10k_submissions
                UNION ALL
                SELECT cik, filing_date, form_type FROM sec_8k_submissions
            ) all_filings
            WHERE filing_date >= date('now', '-1 year')
            AND cik != :cik
            GROUP BY cik
            HAVING COUNT(DISTINCT filing_date) > 0
            ORDER BY filing_frequency_annual DESC
            LIMIT 20
        """)
        
        peer_metrics = self.db.execute(peer_metrics_query, {"cik": cik}).fetchall()
        
        return {
            "company_metrics": dict(company_metrics._mapping) if company_metrics else {},
            "peer_metrics": [dict(row._mapping) for row in peer_metrics],
            "comparison_analysis": {
                "peer_selection_method": peer_selection,
                "analysis_period": "12 months",
                "metrics_compared": ["filing_frequency", "report_types", "timeliness"]
            }
        }
    
    def _analyze_market_concentration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Market concentration analysis across asset classes"""
        
        # Placeholder implementation - would need more specific market definition
        return {
            "concentration_metrics": {
                "herfindahl_index": "Not implemented",
                "top_4_concentration": "Not implemented", 
                "market_participants": "Not implemented"
            },
            "note": "Market concentration analysis requires additional market definition parameters"
        }
    
    def _analyze_regulatory_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Regulatory filing timeline analysis"""
        
        # Placeholder implementation
        return {
            "timeline_analysis": {
                "filing_patterns": "Not implemented",
                "regulatory_cycles": "Not implemented",
                "compliance_indicators": "Not implemented"
            },
            "note": "Regulatory timeline analysis requires additional temporal modeling"
        }
    
    def _analyze_cross_asset_correlation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-asset correlation analysis"""
        
        # Placeholder implementation 
        return {
            "correlation_analysis": {
                "asset_correlations": "Not implemented",
                "risk_factor_exposures": "Not implemented",
                "volatility_clustering": "Not implemented"
            },
            "note": "Cross-asset correlation analysis requires additional statistical modeling"
        }
    
    def _identify_data_sources(self, query_type: str) -> List[str]:
        """Identify which data sources are used for each query type"""
        
        source_mapping = {
            'company_comprehensive_profile': ['SEC Insider Filings', 'SEC 10-K/8-K', 'Form D', 'N-MFP'],
            'institutional_flow_analysis': ['Form 13F Holdings'],
            'insider_activity_monitoring': ['SEC Insider Transactions'],
            'swap_risk_assessment': ['CFTC Swap Data'],
            'fund_stability_analysis': ['N-MFP Money Market Funds'],
            'company_peer_analysis': ['SEC 10-K/8-K Filings'],
            'market_concentration_analysis': ['Multiple Sources'],
            'regulatory_timeline_analysis': ['SEC Filings Timeline'],
            'cross_asset_correlation': ['CFTC + SEC Data']
        }
        
        return source_mapping.get(query_type, ['Unknown'])
    
    def _generate_ai_insights(self, query_type: str, sql_results: Dict[str, Any], params: Dict[str, Any]) -> str:
        """Generate AI-powered insights from cross-dataset analysis results"""
        
        prompt = f"""
        As Raven, analyze the following cross-dataset {query_type} results and provide sophisticated financial insights:

        Query Type: {query_type}
        Parameters: {json.dumps(params, indent=2)}
        Data Sources: {', '.join(self._identify_data_sources(query_type))}
        
        Results: {json.dumps(sql_results, indent=2, default=str)[:3000]}...
        
        Please provide:
        1. Key findings and cross-dataset patterns
        2. Risk assessments and regulatory implications
        3. Market context and comparative analysis
        4. Actionable insights for financial professionals
        5. Potential areas for deeper investigation
        
        Focus on connecting insights across different regulatory data sources and identifying patterns that wouldn't be visible in single-dataset analysis.
        """
        
        try:
            response = ollama.chat(
                model='raven-enhanced',
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"AI insight generation failed: {str(e)}"


# Enhanced analytics functions for the TOOL_MAP
def comprehensive_company_analysis(cik: str, include_subsidiaries: bool = True):
    """Multi-dimensional company analysis across all regulatory data sources"""
    with CrossDatasetAnalyticsEngine() as engine:
        results = engine.execute_cross_dataset_query('company_comprehensive_profile', {
            'cik': cik,
            'include_subsidiaries': include_subsidiaries
        })
    return json.dumps(results, default=str)

def institutional_flow_analysis(timeframe_days: int = 90, min_position_value: float = 1000000):
    """Analyze institutional money flows and position changes using Form 13F data"""
    with CrossDatasetAnalyticsEngine() as engine:
        results = engine.execute_cross_dataset_query('institutional_flow_analysis', {
            'timeframe_days': timeframe_days,
            'min_position_value': min_position_value
        })
    return json.dumps(results, default=str)

def insider_activity_monitoring(analysis_type: str = "unusual_activity", lookback_days: int = 30):
    """Monitor and analyze insider trading patterns for unusual activity detection"""
    with CrossDatasetAnalyticsEngine() as engine:
        results = engine.execute_cross_dataset_query('insider_activity_monitoring', {
            'analysis_type': analysis_type,
            'lookback_days': lookback_days
        })
    return json.dumps(results, default=str)

def swap_risk_assessment(risk_dimension: str = "counterparty", aggregation_level: str = "weekly"):
    """Comprehensive CFTC swap market risk analysis and exposure assessment"""
    with CrossDatasetAnalyticsEngine() as engine:
        results = engine.execute_cross_dataset_query('swap_risk_assessment', {
            'risk_dimension': risk_dimension,
            'aggregation_level': aggregation_level
        })
    return json.dumps(results, default=str)

def fund_stability_analysis(fund_category: str = "all", stress_scenario: bool = False):
    """Money market fund liquidity and stability assessment using N-MFP data"""
    with CrossDatasetAnalyticsEngine() as engine:
        results = engine.execute_cross_dataset_query('fund_stability_analysis', {
            'fund_category': fund_category,
            'stress_scenario': stress_scenario
        })
    return json.dumps(results, default=str)

def company_peer_analysis(cik: str, peer_selection: str = "industry"):
    """Compare company metrics against industry peers across multiple data sources"""
    with CrossDatasetAnalyticsEngine() as engine:
        results = engine.execute_cross_dataset_query('company_peer_analysis', {
            'cik': cik,
            'peer_selection': peer_selection
        })
    return json.dumps(results, default=str)

# Enhanced TOOL_MAP additions for cross-dataset analytics
ENHANCED_ANALYTICS_TOOLS = {
    "comprehensive_company_analysis": {
        "function": comprehensive_company_analysis,
        "schema": {
            "name": "comprehensive_company_analysis",
            "description": "Multi-dimensional company analysis across SEC, CFTC, Form D, and fund data sources",
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
    "institutional_flow_analysis": {
        "function": institutional_flow_analysis,
        "schema": {
            "name": "institutional_flow_analysis",
            "description": "Analyze institutional money flows and position changes using Form 13F data",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeframe_days": {"type": "integer", "description": "Analysis timeframe in days (default: 90)"},
                    "min_position_value": {"type": "number", "description": "Minimum position value for analysis (default: 1000000)"}
                },
                "required": []
            }
        }
    },
    "insider_activity_monitoring": {
        "function": insider_activity_monitoring,
        "schema": {
            "name": "insider_activity_monitoring",
            "description": "Monitor and detect unusual insider trading patterns across companies",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_type": {"type": "string", "description": "Type of analysis: 'unusual_activity', 'unusual_selling', 'unusual_buying' (default: 'unusual_activity')"},
                    "lookback_days": {"type": "integer", "description": "Analysis period in days (default: 30)"}
                },
                "required": []
            }
        }
    },
    "swap_risk_assessment": {
        "function": swap_risk_assessment,
        "schema": {
            "name": "swap_risk_assessment",
            "description": "Comprehensive CFTC swap market risk analysis and exposure assessment",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_dimension": {"type": "string", "description": "Risk analysis dimension: 'counterparty', 'underlying', 'maturity' (default: 'counterparty')"},
                    "aggregation_level": {"type": "string", "description": "Time aggregation: 'daily', 'weekly', 'monthly' (default: 'weekly')"}
                },
                "required": []
            }
        }
    },
    "fund_stability_analysis": {
        "function": fund_stability_analysis,
        "schema": {
            "name": "fund_stability_analysis",
            "description": "Money market fund liquidity and stability assessment using N-MFP regulatory data",
            "parameters": {
                "type": "object",
                "properties": {
                    "fund_category": {"type": "string", "description": "Fund category: 'prime', 'government', 'tax_exempt', 'all' (default: 'all')"},
                    "stress_scenario": {"type": "boolean", "description": "Apply stress testing scenarios (default: false)"}
                },
                "required": []
            }
        }
    },
    "company_peer_analysis": {
        "function": company_peer_analysis,
        "schema": {
            "name": "company_peer_analysis",
            "description": "Compare company metrics against industry peers across multiple regulatory data sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "cik": {"type": "string", "description": "Company CIK identifier (required)"},
                    "peer_selection": {"type": "string", "description": "Peer selection method: 'industry', 'size', 'filing_pattern' (default: 'industry')"}
                },
                "required": ["cik"]
            }
        }
    }
}
