# GameCock AI Database Schema Documentation

## Overview
The GameCock AI database is a comprehensive SQLite-based system containing 64+ tables with 4.39 million records across multiple regulatory data sources. The schema is designed to support advanced financial analysis, entity resolution, and cross-dataset correlation. **Note**: Entity resolution now primarily uses the SEC API for real-time company data, with the database serving as a fallback for additional entity information.

## Database Statistics
- **Total Tables**: 64+
- **Total Records**: 4.39 million
- **Primary Data Sources**: SEC, CFTC, FRED, DTCC, Form filings
- **Database Engine**: SQLite with SQLAlchemy ORM
- **Storage Location**: `gamecock.db`

## Schema Categories

### 1. SEC Regulatory Filings (16 tables)
#### Insider Trading Tables
- `sec_submissions` - Main submission metadata
- `sec_reporting_owners` - Reporting owner information
- `sec_non_deriv_trans` - Non-derivative transactions
- `sec_non_deriv_holdings` - Non-derivative holdings
- `sec_deriv_trans` - Derivative transactions
- `sec_deriv_holdings` - Derivative holdings
- `sec_footnotes` - Filing footnotes
- `sec_owner_signatures` - Owner signatures

#### 10-K/10-Q Filings
- `sec_10k_submissions` - 10-K/10-Q filing metadata
- `sec_10k_documents` - Extracted document sections
- `sec_10k_financials` - Financial statement data
- `sec_10k_exhibits` - Exhibit information
- `sec_10k_metadata` - Additional metadata

#### 8-K Filings
- `sec_8k_submissions` - 8-K filing metadata
- `sec_8k_items` - Individual 8-K items

#### Exchange Metrics
- `sec_exchange_metrics` - Exchange trading metrics

### 2. Form 13F Holdings (6 tables)
- `form13f_submissions` - 13F submission metadata
- `form13f_coverpages` - Cover page information
- `form13f_other_managers` - Other manager information
- `form13f_signatures` - Signature information
- `form13f_summary_pages` - Summary page data
- `form13f_info_tables` - Holdings information

### 3. N-Series Fund Data (34 tables)
#### N-CEN Tables (5 tables)
- `ncen_submissions` - N-CEN submission metadata
- `ncen_registrants` - Registrant information
- `ncen_fund_reported_info` - Fund information
- `ncen_advisers` - Adviser information

#### N-PORT Tables (3 tables)
- `nport_submissions` - N-PORT submission metadata
- `nport_general_info` - General fund information
- `nport_holdings` - Portfolio holdings
- `nport_derivatives` - Derivative positions

#### N-MFP Tables (26 tables)
- `nmfp_submissions` - N-MFP submission metadata
- `nmfp_funds` - Fund information
- `nmfp_series_level_info` - Series-level information
- `nmfp_master_feeder_funds` - Master-feeder relationships
- `nmfp_advisers` - Adviser information
- `nmfp_administrators` - Administrator information
- `nmfp_transfer_agents` - Transfer agent information
- `nmfp_series_shadow_price_l` - Shadow pricing
- `nmfp_class_level_info` - Class-level information
- `nmfp_net_asset_value_per_share_l` - NAV per share
- `nmfp_sch_portfolio_securities` - Portfolio securities
- `nmfp_collateral_issuers` - Collateral issuer information
- `nmfp_nrsro` - NRSRO ratings
- `nmfp_demand_features` - Demand features
- `nmfp_guarantors` - Guarantor information
- `nmfp_enhancement_providers` - Enhancement providers
- `nmfp_liquid_assets_details` - Liquid assets
- `nmfp_seven_day_gross_yields` - Seven-day gross yields
- `nmfp_dly_net_asset_value_per_shars` - Daily NAV
- `nmfp_liquidity_fee_reporting_per` - Liquidity fees
- `nmfp_dly_net_asset_value_per_sharc` - Daily NAV per class
- `nmfp_dly_shareholder_flow_reports` - Shareholder flows
- `nmfp_seven_day_net_yields` - Seven-day net yields
- `nmfp_beneficial_record_owner_cat` - Beneficial ownership
- `nmfp_cancelled_shares_per_bus_day` - Cancelled shares
- `nmfp_disposition_of_portfolio_securities` - Security dispositions

### 4. Form D Filings (5 tables)
- `formd_submissions` - Form D submission metadata
- `formd_issuers` - Issuer information
- `formd_offerings` - Offering details
- `formd_recipients` - Recipient information
- `formd_related_persons` - Related person information
- `formd_signatures` - Signature information

### 5. CFTC Swap Data (5 tables)
- `cftc_derivatives_dealers` - Swap dealers and major swap participants
- `cftc_derivatives_clearing_orgs` - Derivatives clearing organizations
- `cftc_swap_execution_facilities` - Swap execution facilities
- `cftc_swap_data_repositories` - Swap data repositories
- `cftc_daily_swap_reports` - Daily swap report data
- `cftc_swap_data` - Comprehensive swap transaction data

## Key Table Relationships

### Entity Resolution
```
Companies (CIK) ←→ SEC Filings (issuercik)
Companies (CIK) ←→ Form 13F (cik)
Companies (CIK) ←→ N-Series (cik)
Companies (CIK) ←→ Form D (cik)
```

### Cross-Reference Relationships
```
SEC Submissions (accession_number) ←→ SEC Transactions
Form 13F Submissions (accession_number) ←→ Form 13F Holdings
N-PORT Submissions (accession_number) ←→ N-PORT Holdings
CFTC Swaps (dissemination_id) ←→ CFTC Daily Reports
```

### Temporal Relationships
```
Filing Date ←→ Period of Report
Transaction Date ←→ Execution Date
Effective Date ←→ Maturity Date
```

## Data Types and Constraints

### Primary Keys
- Most tables use `accession_number` as primary key
- Some tables use composite keys (accession_number + sequence)
- Auto-incrementing IDs for some tables

### Foreign Key Relationships
- `issuercik` references company identifiers
- `accession_number` links related filing data
- `cik` fields link to company information

### Indexing Strategy
- Primary keys are automatically indexed
- Frequently queried columns have explicit indexes
- Composite indexes for multi-column queries
- Temporal indexes for date-based queries

## Data Quality and Validation

### Data Validation Rules
- CIK format validation (10-digit zero-padded)
- Date format consistency
- Currency code validation
- Numeric range validation

### Data Cleaning Processes
- HTML tag removal from SEC filings
- Whitespace normalization
- Duplicate detection and removal
- Missing value handling

## Performance Optimizations

### Indexing Strategy
```sql
-- Primary indexes
CREATE INDEX idx_sec_submissions_cik ON sec_submissions(issuercik);
CREATE INDEX idx_sec_submissions_date ON sec_submissions(filing_date);
CREATE INDEX idx_cftc_swap_date ON cftc_swap_data(report_date);
CREATE INDEX idx_cftc_swap_asset_class ON cftc_swap_data(asset_class);

-- Composite indexes
CREATE INDEX idx_sec_10k_cik_date ON sec_10k_submissions(cik, filing_date);
CREATE INDEX idx_form13f_cik_period ON form13f_submissions(cik, period_of_report);
```

### Query Optimization
- Strategic use of WHERE clauses
- LIMIT clauses for large result sets
- Efficient JOIN operations
- Subquery optimization

## Data Volume by Category

### Current Data Distribution
- **Form Tables**: 4,393,254 records (Primary data source)
- **SEC Tables**: Ready for data (0 records currently)
- **CFTC Tables**: Ready for data (0 records currently)
- **N-Series Tables**: Ready for data (0 records currently)

### Growth Projections
- SEC filings: ~50,000 new records per year
- CFTC data: ~1,000,000 new records per year
- Form 13F: ~20,000 new records per year
- N-Series: ~100,000 new records per year

## Backup and Recovery

### Backup Strategy
- Daily automated backups
- Point-in-time recovery capability
- Cross-platform backup compatibility
- Compressed backup storage

### Recovery Procedures
- Full database restoration
- Selective table restoration
- Data migration procedures
- Schema version management

## Security Considerations

### Data Protection
- Encrypted storage for sensitive data
- Access control mechanisms
- Audit logging for data changes
- Secure backup procedures

### Compliance
- SEC data handling compliance
- CFTC reporting requirements
- Data retention policies
- Privacy protection measures

## Integration Points

### External APIs
- SEC EDGAR API integration
- CFTC data repository access
- FRED economic data
- DTCC derivative data

### Internal Systems
- Vector database synchronization
- RAG system integration
- Analytics tool access
- Reporting system feeds

## Maintenance Procedures

### Regular Maintenance
- Database optimization
- Index rebuilding
- Statistics updates
- Vacuum operations

### Monitoring
- Query performance monitoring
- Storage usage tracking
- Error rate monitoring
- Data quality metrics

---

*This database schema documentation provides a comprehensive overview of the GameCock AI database structure, relationships, and management procedures. For detailed table specifications, refer to the database.py source code.*
