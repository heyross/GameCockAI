# 🏗️ GameCock Database Relational Analysis & AI Query Framework

## 📊 Current Schema Overview

Based on the comprehensive analysis, the GameCock system contains **64 data models** across 4 major categories:

### Data Categories & Scale
- **SEC Tables (16)**: Insider transactions, 10-K/8-K filings, exchange metrics
- **CFTC Tables (1)**: Swap transaction data
- **Form Tables (13)**: 13F holdings, Form D offerings (**4.39M records** - primary data source)
- **N-Series Tables (34)**: Money market funds (N-MFP), portfolio reports (N-PORT), census data (N-CEN)

## 🔗 Key Relational Structure Analysis

### 1. **Company-Centric Relationships**
The system revolves around companies identified by:
- **CIK** (Central Index Key) - Primary company identifier
- **Ticker Symbol** - Trading symbol
- **LEI** (Legal Entity Identifier) - International identifier

**Core Entity Relationships:**
```
Company (CIK) ──┬── SEC Filings (10-K, 8-K, Insider)
                ├── CFTC Swaps
                ├── Form 13F Holdings
                ├── Form D Offerings
                └── Fund Management (N-Series)
```

### 2. **Time-Series Data Structure**
Most tables follow temporal patterns:
- **Filing Date** - When submitted to regulators
- **Period of Report** - What period data covers
- **Execution/Transaction Date** - When events occurred

### 3. **Hierarchical Relationships**

#### SEC Insider Trading Hierarchy:
```
sec_submissions (filing metadata)
├── sec_reporting_owners (who filed)
├── sec_non_deriv_trans (stock transactions)
├── sec_deriv_trans (derivative transactions)
├── sec_non_deriv_holdings (stock holdings)
├── sec_deriv_holdings (derivative holdings)
└── sec_footnotes (additional details)
```

#### Form 13F Hierarchy:
```
form13f_submissions (quarterly institutional filings)
├── form13f_coverpages (filing details)
├── form13f_info_tables (individual holdings)
├── form13f_other_managers (co-managers)
└── form13f_signatures (authorization)
```

#### N-MFP Fund Hierarchy:
```
nmfp_submissions (money market fund reports)
├── nmfp_series_level_info (fund details)
├── nmfp_class_level_info (share classes)
├── nmfp_sch_portfolio_securities (holdings)
├── nmfp_collateral_issuers (collateral details)
└── nmfp_advisers (fund managers)
```

## 🎯 Proposed Relational Optimization

### 1. **Core Entity Tables** (Master Data)
```sql
-- Unified company registry
CREATE VIEW unified_companies AS
SELECT DISTINCT 
    cik,
    company_name,
    ticker_symbol,
    lei,
    industry_classification
FROM (
    SELECT issuercik as cik, issuername as company_name, issuertradingsymbol as ticker_symbol, NULL as lei, NULL as industry_classification FROM sec_submissions
    UNION
    SELECT cik, registrant_name as company_name, NULL as ticker_symbol, lei, NULL as industry_classification FROM form13f_submissions
    UNION
    SELECT cik, entity_name as company_name, NULL as ticker_symbol, NULL as lei, sic_code as industry_classification FROM formd_issuers
);
```

### 2. **Time-Series Index Strategy**
```sql
-- Optimized indexes for temporal queries
CREATE INDEX idx_temporal_filings ON sec_submissions(filing_date, issuercik);
CREATE INDEX idx_temporal_swaps ON cftc_swap_data(execution_timestamp, asset_class);
CREATE INDEX idx_temporal_trades ON sec_non_deriv_trans(trans_date, accession_number);
CREATE INDEX idx_temporal_holdings ON form13f_info_tables(accession_number, cusip);
```

### 3. **Cross-Dataset Relationship Views**
```sql
-- Company activity timeline
CREATE VIEW company_activity_timeline AS
SELECT 
    cik,
    'SEC_FILING' as activity_type,
    filing_date as activity_date,
    document_type as details
FROM sec_submissions
UNION ALL
SELECT 
    cik,
    'FORM_13F' as activity_type,
    filing_date as activity_date,
    submission_type as details
FROM form13f_submissions
UNION ALL
SELECT 
    cik,
    'FORM_D' as activity_type,
    filing_date as activity_date,
    'OFFERING' as details
FROM formd_submissions
ORDER BY activity_date DESC;
```

## 🤖 AI-Triggerable Query Framework

### 1. **Company Analysis Queries**

#### Company Profile & Activity
```python
def get_company_comprehensive_profile(cik: str, include_subsidiaries: bool = True):
    """Get complete company profile across all data sources"""
    return {
        "query_type": "company_profile",
        "parameters": {"cik": cik, "include_subsidiaries": include_subsidiaries},
        "sql_components": [
            # Basic company info
            "SELECT * FROM unified_companies WHERE cik = ?",
            # Recent filings
            "SELECT * FROM company_activity_timeline WHERE cik = ? ORDER BY activity_date DESC LIMIT 50",
            # Insider trading activity
            "SELECT COUNT(*), SUM(trans_shares * trans_pricepershare) as total_value FROM sec_non_deriv_trans snt JOIN sec_submissions ss ON snt.accession_number = ss.accession_number WHERE ss.issuercik = ? AND snt.trans_date >= date('now', '-1 year')",
            # 13F holdings exposure
            "SELECT COUNT(DISTINCT accession_number) as institutional_holders, SUM(value) as total_institutional_value FROM form13f_info_tables fit WHERE fit.cusip IN (SELECT DISTINCT cusip FROM security_mappings WHERE cik = ?)"
        ]
    }
```

#### Company Peer Analysis
```python
def analyze_company_vs_peers(cik: str, peer_selection: str = "industry"):
    """Compare company metrics against industry peers"""
    return {
        "query_type": "peer_analysis", 
        "parameters": {"cik": cik, "peer_selection": peer_selection},
        "sql_components": [
            # Company metrics
            "SELECT cik, COUNT(DISTINCT filing_date) as filing_frequency, AVG(CASE WHEN form_type = '10-K' THEN 1 ELSE 0 END) as annual_filing_rate FROM sec_10k_submissions WHERE cik = ? GROUP BY cik",
            # Peer metrics (same industry)
            "SELECT AVG(filing_frequency) as peer_avg_filing_freq, AVG(annual_filing_rate) as peer_avg_annual_rate FROM (SELECT cik, COUNT(DISTINCT filing_date) as filing_frequency, AVG(CASE WHEN form_type = '10-K' THEN 1 ELSE 0 END) as annual_filing_rate FROM sec_10k_submissions s10k JOIN unified_companies uc ON s10k.cik = uc.cik WHERE uc.industry_classification = (SELECT industry_classification FROM unified_companies WHERE cik = ?) GROUP BY s10k.cik)"
        ]
    }
```

### 2. **Market Analysis Queries**

#### Institutional Holdings Flow
```python
def analyze_institutional_holdings_flow(timeframe_days: int = 90, min_position_value: float = 1000000):
    """Analyze institutional buying/selling patterns"""
    return {
        "query_type": "institutional_flow",
        "parameters": {"timeframe_days": timeframe_days, "min_position_value": min_position_value},
        "sql_components": [
            # Current quarter vs previous quarter holdings changes
            """
            WITH current_holdings AS (
                SELECT cusip, nameofissuer, SUM(value) as current_value, COUNT(*) as current_holders
                FROM form13f_info_tables fit 
                JOIN form13f_submissions fs ON fit.accession_number = fs.accession_number
                WHERE fs.filing_date >= date('now', '-120 days')
                GROUP BY cusip, nameofissuer
            ),
            previous_holdings AS (
                SELECT cusip, nameofissuer, SUM(value) as previous_value, COUNT(*) as previous_holders
                FROM form13f_info_tables fit 
                JOIN form13f_submissions fs ON fit.accession_number = fs.accession_number  
                WHERE fs.filing_date BETWEEN date('now', '-240 days') AND date('now', '-120 days')
                GROUP BY cusip, nameofissuer
            )
            SELECT 
                c.cusip, c.nameofissuer,
                c.current_value, p.previous_value,
                c.current_value - p.previous_value as value_change,
                (c.current_value - p.previous_value) / p.previous_value * 100 as pct_change,
                c.current_holders, p.previous_holders,
                c.current_holders - p.previous_holders as holder_change
            FROM current_holdings c
            LEFT JOIN previous_holdings p ON c.cusip = p.cusip
            WHERE c.current_value >= ? OR p.previous_value >= ?
            ORDER BY ABS(value_change) DESC
            """
        ]
    }
```

#### Insider Trading Patterns
```python
def analyze_insider_trading_patterns(analysis_type: str = "unusual_activity", lookback_days: int = 30):
    """Detect insider trading patterns and anomalies"""
    return {
        "query_type": "insider_patterns",
        "parameters": {"analysis_type": analysis_type, "lookback_days": lookback_days},
        "sql_components": [
            # Unusual volume by company
            """
            WITH insider_activity AS (
                SELECT 
                    ss.issuercik, ss.issuername,
                    COUNT(*) as recent_transactions,
                    SUM(snt.trans_shares * snt.trans_pricepershare) as recent_value,
                    COUNT(DISTINCT sro.rptownercik) as unique_insiders
                FROM sec_non_deriv_trans snt
                JOIN sec_submissions ss ON snt.accession_number = ss.accession_number
                JOIN sec_reporting_owners sro ON snt.accession_number = sro.accession_number
                WHERE snt.trans_date >= date('now', '-{} days')
                AND snt.trans_acquired_disp_cd = 'D'  -- Dispositions (sales)
                GROUP BY ss.issuercik, ss.issuername
            ),
            historical_avg AS (
                SELECT 
                    ss.issuercik,
                    AVG(monthly_transactions) as avg_monthly_transactions,
                    AVG(monthly_value) as avg_monthly_value
                FROM (
                    SELECT 
                        ss.issuercik,
                        strftime('%Y-%m', snt.trans_date) as month,
                        COUNT(*) as monthly_transactions,
                        SUM(snt.trans_shares * snt.trans_pricepershare) as monthly_value
                    FROM sec_non_deriv_trans snt
                    JOIN sec_submissions ss ON snt.accession_number = ss.accession_number
                    WHERE snt.trans_date >= date('now', '-1 year')
                    AND snt.trans_date < date('now', '-{} days')
                    AND snt.trans_acquired_disp_cd = 'D'
                    GROUP BY ss.issuercik, strftime('%Y-%m', snt.trans_date)
                ) monthly_data
                GROUP BY ss.issuercik
            )
            SELECT 
                ia.issuercik, ia.issuername,
                ia.recent_transactions, ha.avg_monthly_transactions,
                ia.recent_transactions / ha.avg_monthly_transactions as transaction_ratio,
                ia.recent_value, ha.avg_monthly_value,
                ia.recent_value / ha.avg_monthly_value as value_ratio,
                ia.unique_insiders
            FROM insider_activity ia
            JOIN historical_avg ha ON ia.issuercik = ha.issuercik
            WHERE ia.recent_transactions / ha.avg_monthly_transactions > 2.0  -- 2x normal activity
            OR ia.recent_value / ha.avg_monthly_value > 3.0  -- 3x normal value
            ORDER BY transaction_ratio DESC, value_ratio DESC
            """.format(lookback_days, lookback_days)
        ]
    }
```

### 3. **Risk & Compliance Queries**

#### CFTC Swap Exposure Analysis
```python
def analyze_swap_market_exposure(risk_dimension: str = "counterparty", aggregation_level: str = "weekly"):
    """Analyze swap market exposures and concentrations"""
    return {
        "query_type": "swap_exposure",
        "parameters": {"risk_dimension": risk_dimension, "aggregation_level": aggregation_level},
        "sql_components": [
            # Notional exposure by asset class and time
            """
            SELECT 
                asset_class,
                strftime('%Y-%W', execution_timestamp) as week,
                COUNT(*) as transaction_count,
                SUM(notional_amount_leg_1) as total_notional_leg1,
                SUM(notional_amount_leg_2) as total_notional_leg2,
                AVG(notional_amount_leg_1) as avg_notional_leg1,
                COUNT(DISTINCT underlier_id_leg_1) as unique_underlyings
            FROM cftc_swap_data
            WHERE execution_timestamp >= date('now', '-90 days')
            GROUP BY asset_class, strftime('%Y-%W', execution_timestamp)
            ORDER BY week DESC, total_notional_leg1 DESC
            """,
            # Concentration risk by underlying
            """
            SELECT 
                underlying_asset_name,
                asset_class,
                COUNT(*) as contract_count,
                SUM(notional_amount_leg_1) as total_exposure,
                SUM(notional_amount_leg_1) / (SELECT SUM(notional_amount_leg_1) FROM cftc_swap_data WHERE execution_timestamp >= date('now', '-30 days')) * 100 as market_share_pct
            FROM cftc_swap_data
            WHERE execution_timestamp >= date('now', '-30 days')
            AND underlying_asset_name IS NOT NULL
            GROUP BY underlying_asset_name, asset_class
            HAVING total_exposure > 0
            ORDER BY total_exposure DESC
            LIMIT 50
            """
        ]
    }
```

### 4. **Fund Analysis Queries**

#### Money Market Fund Liquidity Analysis
```python
def analyze_fund_liquidity_metrics(fund_category: str = "all", stress_scenario: bool = False):
    """Analyze money market fund liquidity and stability metrics"""
    return {
        "query_type": "fund_liquidity",
        "parameters": {"fund_category": fund_category, "stress_scenario": stress_scenario},
        "sql_components": [
            # Daily/Weekly liquidity ratios
            """
            SELECT 
                ns.seriesid, ns.nameofseries,
                nsli.money_market_fund_category,
                nsli.pct_dly_liquid_asset_friday_week1 as daily_liquidity_pct,
                nsli.pct_wkly_liquid_asset_friday_week1 as weekly_liquidity_pct,
                nsli.seven_day_gross_yield,
                nsli.net_asset_of_series,
                ncli.net_assets_of_class,
                ncli.seven_day_net_yield
            FROM nmfp_submissions ns
            JOIN nmfp_series_level_info nsli ON ns.accession_number = nsli.accession_number
            LEFT JOIN nmfp_class_level_info ncli ON ns.accession_number = ncli.accession_number
            WHERE ns.filing_date >= date('now', '-30 days')
            AND nsli.pct_dly_liquid_asset_friday_week1 IS NOT NULL
            ORDER BY nsli.pct_dly_liquid_asset_friday_week1 ASC  -- Lowest liquidity first
            """,
            # Portfolio concentration analysis
            """
            SELECT 
                nps.accession_number,
                nps.name_of_issuer,
                nps.investment_category,
                COUNT(*) as security_count,
                SUM(nps.percentage_of_money_market_fund_net) as total_fund_percentage,
                AVG(nps.yield_of_the_security_as_of_reportin) as avg_yield,
                SUM(nps.including_value_of_any_sponsor_supp) as total_value
            FROM nmfp_sch_portfolio_securities nps
            JOIN nmfp_submissions ns ON nps.accession_number = ns.accession_number
            WHERE ns.filing_date >= date('now', '-30 days')
            GROUP BY nps.accession_number, nps.name_of_issuer, nps.investment_category
            HAVING total_fund_percentage > 5.0  -- Concentration > 5%
            ORDER BY total_fund_percentage DESC
            """
        ]
    }
```

## 🎛️ Enhanced Analytics Tools Implementation

### New Analytics Functions for AI Integration

```python
# Add to analytics_tools.py

def comprehensive_company_analysis(cik: str, include_subsidiaries: bool = True):
    """Multi-dimensional company analysis across all data sources"""
    with AnalyticsEngine() as engine:
        profile_data = get_company_comprehensive_profile(cik, include_subsidiaries)
        results = engine.execute_analytical_query('company_profile', profile_data['parameters'])
    return json.dumps(results, default=str)

def institutional_flow_analysis(timeframe_days: int = 90, min_position_value: float = 1000000):
    """Analyze institutional money flows and position changes"""
    with AnalyticsEngine() as engine:
        flow_data = analyze_institutional_holdings_flow(timeframe_days, min_position_value)
        results = engine.execute_analytical_query('institutional_flow', flow_data['parameters'])
    return json.dumps(results, default=str)

def insider_activity_monitoring(analysis_type: str = "unusual_activity", lookback_days: int = 30):
    """Monitor and analyze insider trading patterns"""
    with AnalyticsEngine() as engine:
        insider_data = analyze_insider_trading_patterns(analysis_type, lookback_days)
        results = engine.execute_analytical_query('insider_patterns', insider_data['parameters'])
    return json.dumps(results, default=str)

def swap_risk_assessment(risk_dimension: str = "counterparty", aggregation_level: str = "weekly"):
    """Comprehensive CFTC swap market risk analysis"""
    with AnalyticsEngine() as engine:
        swap_data = analyze_swap_market_exposure(risk_dimension, aggregation_level)
        results = engine.execute_analytical_query('swap_exposure', swap_data['parameters'])
    return json.dumps(results, default=str)

def fund_stability_analysis(fund_category: str = "all", stress_scenario: bool = False):
    """Money market fund liquidity and stability assessment"""
    with AnalyticsEngine() as engine:
        fund_data = analyze_fund_liquidity_metrics(fund_category, stress_scenario)
        results = engine.execute_analytical_query('fund_liquidity', fund_data['parameters'])
    return json.dumps(results, default=str)
```

## 🚀 AI Natural Language Query Examples

### Enhanced Natural Language Triggers:

1. **"Show me companies with unusual insider selling in the past 30 days"**
   → Triggers: `insider_activity_monitoring(analysis_type="unusual_selling", lookback_days=30)`

2. **"Which institutional investors have been buying tech stocks this quarter?"**
   → Triggers: `institutional_flow_analysis(timeframe_days=90)` + sector filter

3. **"Analyze swap market concentration risk for credit derivatives"**
   → Triggers: `swap_risk_assessment(risk_dimension="underlying", aggregation_level="daily")` + asset_class filter

4. **"What money market funds have the lowest liquidity ratios?"**
   → Triggers: `fund_stability_analysis(fund_category="prime", stress_scenario=True)`

5. **"Compare Apple's filing activity against tech industry peers"**
   → Triggers: `comprehensive_company_analysis(cik="320193", include_subsidiaries=True)` + peer analysis

## 📊 Performance Optimization Recommendations

### 1. **Materialized Views for Heavy Queries**
```sql
-- Pre-computed company metrics
CREATE MATERIALIZED VIEW company_metrics_monthly AS
SELECT 
    cik, 
    strftime('%Y-%m', filing_date) as month,
    COUNT(*) as filing_count,
    COUNT(DISTINCT document_type) as filing_types
FROM sec_submissions 
GROUP BY cik, strftime('%Y-%m', filing_date);

-- Refresh quarterly
```

### 2. **Partitioning Strategy**
- **Time-based partitioning** for large tables by filing_date/execution_timestamp
- **Hash partitioning** for company-based queries by CIK

### 3. **Caching Layer**
- Cache frequently requested company profiles
- Cache market overview metrics (daily refresh)
- Cache peer group calculations

## 🎯 Next Steps for Implementation

1. **Implement the enhanced analytics functions** in `analytics_tools.py`
2. **Create optimized database views** for cross-dataset queries  
3. **Add the new functions to TOOL_MAP** for AI access
4. **Implement materialized views** for performance
5. **Create data validation** and consistency checks
6. **Add real-time alerting** for unusual patterns

This framework transforms GameCock from a data storage system into an intelligent financial analysis platform capable of answering complex multi-dimensional questions across regulatory filings, market data, and institutional activity.
