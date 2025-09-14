from datetime import datetime
from sqlalchemy import create_engine, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import pandas as pd

# Create the declarative base first to avoid circular imports
Base = declarative_base()

DATABASE_URL = "sqlite:///./gamecock.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, JSON, BigInteger

class SecSubmission(Base):
    __tablename__ = 'sec_submissions'
    accession_number = Column(String(25), primary_key=True)
    filing_date = Column(DateTime, nullable=False)
    period_of_report = Column(DateTime, nullable=False)
    date_of_orig_sub = Column(DateTime)
    no_securities_owned = Column(String(1))
    not_subject_sec16 = Column(String(1))
    form3_holding_reported = Column(String(1))
    form4_trans_reported = Column(String(1))
    document_type = Column(String(20), nullable=False)
    issuercik = Column(String(10), nullable=False)
    issuername = Column(String(150), nullable=False)
    issuertradingsymbol = Column(String(10), nullable=False)
    remarks = Column(String(2000))

class SecReportingOwner(Base):
    __tablename__ = 'sec_reporting_owners'
    accession_number = Column(String(25), primary_key=True)
    rptownercik = Column(String(10), primary_key=True)
    rptownername = Column(String(150), nullable=False)
    rptowner_relationship = Column(String(100), nullable=False)
    rptowner_title = Column(String(150))
    rptowner_txt = Column(String(50))
    rptowner_street1 = Column(String(150), nullable=False)
    rptowner_street2 = Column(String(150))
    rptowner_city = Column(String(150), nullable=False)
    rptowner_state = Column(String(2), nullable=False)
    rptowner_zipcode = Column(String(10), nullable=False)
    rptowner_state_desc = Column(String(150))
    file_number = Column(String(30))

class SecNonDerivTrans(Base):
    __tablename__ = 'sec_non_deriv_trans'
    accession_number = Column(String(25), primary_key=True)
    nonderiv_trans_sk = Column(Integer, primary_key=True)
    security_title = Column(String(60), nullable=False)
    security_title_fn = Column(String(150))
    trans_date = Column(DateTime, nullable=False)
    trans_date_fn = Column(String(150))
    deemed_execution_date = Column(DateTime)
    deemed_execution_date_fn = Column(String(150))
    trans_form_type = Column(String(1))
    trans_code = Column(String(1))
    equity_swap_involved = Column(String(1))
    equity_swap_trans_cd_fn = Column(String(150))
    trans_timeliness = Column(String(1))
    trans_timeliness_fn = Column(String(150))
    trans_shares = Column(Float)
    trans_shares_fn = Column(String(150))
    trans_pricepershare = Column(Float)
    trans_pricepershare_fn = Column(String(150))
    trans_acquired_disp_cd = Column(String(1), nullable=False)
    trans_acquired_disp_cd_fn = Column(String(150))
    shrs_ownd_folwng_trans = Column(Float)
    shrs_ownd_folwng_trans_fn = Column(String(150))
    valu_ownd_folwng_trans = Column(Float)
    valu_ownd_folwng_trans_fn = Column(String(150))
    direct_indirect_ownership = Column(String(5), nullable=False)
    direct_indirect_ownership_fn = Column(String(150))
    nature_of_ownership = Column(String(100))
    nature_of_ownership_fn = Column(String(150))

class SecNonDerivHolding(Base):
    __tablename__ = 'sec_non_deriv_holdings'
    accession_number = Column(String(25), primary_key=True)
    nonderiv_holding_sk = Column(Integer, primary_key=True)
    security_title = Column(String(60), nullable=False)
    security_title_fn = Column(String(150))
    trans_form_type = Column(String(1))
    trans_form_type_fn = Column(String(150))
    shrs_ownd_folwng_trans = Column(Float)
    shrs_ownd_folwng_trans_fn = Column(String(150))
    valu_ownd_folwng_trans = Column(Float)
    valu_ownd_folwng_trans_fn = Column(String(150))
    direct_indirect_ownership = Column(String(5), nullable=False)
    direct_indirect_ownership_fn = Column(String(150))
    nature_of_ownership = Column(String(100))
    nature_of_ownership_fn = Column(String(150))

class SecDerivTrans(Base):
    __tablename__ = 'sec_deriv_trans'
    accession_number = Column(String(25), primary_key=True)
    deriv_trans_sk = Column(Integer, primary_key=True)
    security_title = Column(String(60), nullable=False)
    security_title_fn = Column(String(150))
    conv_exercise_price = Column(Float)
    conv_exercise_price_fn = Column(String(150))
    trans_date = Column(DateTime, nullable=False)
    trans_date_fn = Column(String(150))
    deemed_execution_date = Column(DateTime)
    deemed_execution_date_fn = Column(String(150))
    trans_form_type = Column(String(1))
    trans_code = Column(String(1))
    equity_swap_involved = Column(String(1))
    equity_swap_trans_cd_fn = Column(String(150))
    trans_timeliness = Column(String(1))
    trans_timeliness_fn = Column(String(150))
    trans_shares = Column(Float)
    trans_shares_fn = Column(String(150))
    trans_total_value = Column(Float)
    trans_total_value_fn = Column(String(150))
    trans_pricepershare = Column(Float)
    trans_pricepershare_fn = Column(String(150))
    trans_acquired_disp_cd = Column(String(1), nullable=False)
    trans_acquired_disp_cd_fn = Column(String(150))
    excercise_date = Column(DateTime)
    excercise_date_fn = Column(String(150))
    expiration_date = Column(DateTime)
    expiration_date_fn = Column(String(150))
    undlyng_sec_title = Column(String(50), nullable=False)
    undlyng_sec_title_fn = Column(String(150))
    undlyng_sec_shares = Column(Float, nullable=False)
    undlyng_sec_shares_fn = Column(String(150))
    undlyng_sec_value = Column(Float)
    undlyng_sec_value_fn = Column(String(150))
    shrs_ownd_folwng_trans = Column(Float)
    shrs_ownd_folwng_trans_fn = Column(String(150))
    valu_ownd_folwng_trans = Column(Float)
    valu_ownd_folwng_trans_fn = Column(String(150))
    direct_indirect_ownership = Column(String(5), nullable=False)
    direct_indirect_ownership_fn = Column(String(150))
    nature_of_ownership = Column(String(100))
    nature_of_ownership_fn = Column(String(150))

class SecDerivHolding(Base):
    __tablename__ = 'sec_deriv_holdings'
    accession_number = Column(String(25), primary_key=True)
    deriv_holding_sk = Column(Integer, primary_key=True)
    security_title = Column(String(60), nullable=False)
    security_title_fn = Column(String(150))
    conv_exercise_price = Column(Float)
    conv_exercise_price_fn = Column(String(150))
    trans_form_type = Column(String(1))
    trans_form_type_fn = Column(String(150))
    exercise_date = Column(DateTime)
    exercise_date_fn = Column(String(150))
    expiration_date = Column(DateTime)
    expiration_date_fn = Column(String(150))
    undlyng_sec_title = Column(String(20), nullable=False)
    undlyng_sec_title_fn = Column(String(150))
    undlyng_sec_shares = Column(Float)
    undlyng_sec_shares_fn = Column(String(150))
    undlyng_sec_value = Column(Float)
    undlyng_sec_value_fn = Column(String(150))
    shrs_ownd_folwng_trans = Column(Float)
    shrs_ownd_folwng_trans_fn = Column(String(150))
    valu_ownd_folwng_trans = Column(Float)
    valu_ownd_folwng_trans_fn = Column(String(150))
    direct_indirect_ownership = Column(String(5), nullable=False)
    direct_indirect_ownership_fn = Column(String(150))
    nature_of_ownership = Column(String(100))
    nature_of_ownership_fn = Column(String(150))

class SecFootnote(Base):
    __tablename__ = 'sec_footnotes'
    accession_number = Column(String(25), primary_key=True)
    footnote_id = Column(String(10), primary_key=True)
    footnote_txt = Column(String(2000), nullable=False)

class SecOwnerSignature(Base):
    __tablename__ = 'sec_owner_signatures'
    accession_number = Column(String(25), primary_key=True)
    ownersignaturename = Column(String(255), primary_key=True)
    ownersignaturedate = Column(DateTime, nullable=False)



class Form13FSubmission(Base):
    __tablename__ = 'form13f_submissions'
    accession_number = Column(String(25), primary_key=True)
    filing_date = Column(DateTime, nullable=False)
    submission_type = Column(String(10), nullable=False)
    cik = Column(String(10), nullable=False)
    period_of_report = Column(DateTime, nullable=False)

class Form13FCoverPage(Base):
    __tablename__ = 'form13f_coverpages'
    accession_number = Column(String(25), primary_key=True)
    report_calendar_or_quarter = Column(DateTime, nullable=False)
    is_amendment = Column(String(1))
    amendment_no = Column(Integer, nullable=True)
    amendment_type = Column(String(20))
    conf_denied_expired = Column(String(1))
    date_denied_expired = Column(DateTime)
    date_reported = Column(DateTime)
    reason_for_non_confidentiality = Column(String(40))
    filing_manager_name = Column(String(150), nullable=False)
    filing_manager_street1 = Column(String(40))
    filing_manager_street2 = Column(String(40))
    filing_manager_city = Column(String(30))
    filing_manager_state_or_country = Column(String(2))
    filing_manager_zipcode = Column(String(10))
    report_type = Column(String(30), nullable=False)
    form13f_file_number = Column(String(17))
    provide_info_for_instruction5 = Column(String(1), nullable=False)
    additional_information = Column(String(4000))

class Form13FOtherManager(Base):
    __tablename__ = 'form13f_other_managers'
    other_manager_sk = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String(25), nullable=False)
    cik = Column(String(10))
    form13f_file_number = Column(String(17))
    name = Column(String(150), nullable=True)

class Form13FSignature(Base):
    __tablename__ = 'form13f_signatures'
    accession_number = Column(String(25), primary_key=True)
    name = Column(String(150), nullable=True)
    title = Column(String(60))
    phone = Column(String(20))
    signature = Column(String(150), nullable=False)
    city = Column(String(30), nullable=True)
    state_or_country = Column(String(2), nullable=True)
    signature_date = Column(DateTime, nullable=False)

class Form13FSummaryPage(Base):
    __tablename__ = 'form13f_summary_pages'
    accession_number = Column(String(25), primary_key=True)
    other_included_managers_count = Column(Integer, nullable=True)
    table_entry_total = Column(Integer, nullable=True)
    table_value_total = Column(Integer, nullable=True)
    is_confidential_omitted = Column(String(1))

class Form13FOtherManager2(Base):
    __tablename__ = 'form13f_other_managers2'
    other_manager2_sk = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String(25), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    cik = Column(String(10))
    form13f_file_number = Column(String(17))
    name = Column(String(150), nullable=True)

class Form13FInfoTable(Base):
    __tablename__ = 'form13f_info_tables'
    accession_number = Column(String(25), primary_key=True)
    infotable_sk = Column(Integer, primary_key=True)
    nameofissuer = Column(String(200), nullable=True)
    titleofclass = Column(String(150), nullable=True)
    cusip = Column(String(9), nullable=False)
    value = Column(Integer, nullable=True)
    sshprnamt = Column(Integer, nullable=True)
    sshprnamttype = Column(String(10), nullable=False)
    putcall = Column(String(10))
    investmentdiscretion = Column(String(10), nullable=False)
    othermanager = Column(String(100))
    voting_auth_sole = Column(Integer, nullable=True)
    voting_auth_shared = Column(Integer, nullable=True)
    voting_auth_none = Column(Integer, nullable=True)

class SecExchangeMetrics(Base):
    __tablename__ = 'sec_exchange_metrics'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    security = Column(String(100))
    mcap_rank = Column(Integer)
    turn_rank = Column(Integer)
    volatility_rank = Column(Integer)
    price_rank = Column(Integer)
    cancels = Column(Integer)
    trades = Column(Integer)
    lit_trades = Column(Integer)
    odd_lots = Column(Integer)
    hidden = Column(Integer)
    trades_for_hidden = Column(Integer)
    order_vol = Column(Float)
    trade_vol = Column(Float)
    lit_vol = Column(Float)
    odd_lot_vol = Column(Float)
    hidden_vol = Column(Float)
    trade_vol_for_hidden = Column(Float)

# N-CEN Tables
class NCENSubmission(Base):
    __tablename__ = 'ncen_submissions'
    accession_number = Column(String(25), primary_key=True)
    submission_type = Column(String(20), nullable=True)
    cik = Column(String(10), nullable=True)
    filing_date = Column(DateTime, nullable=False)
    report_ending_period = Column(DateTime, nullable=True)
    is_report_period_lt_12month = Column(Boolean)
    file_num = Column(String(20))
    registrant_signed_name = Column(String(150))
    date_signed = Column(DateTime)
    signature = Column(String(150))
    title = Column(String(100))
    is_legal_proceedings = Column(Boolean)
    is_provision_financial_support = Column(Boolean)
    is_ipa_report_internal_control = Column(Boolean)
    is_change_acc_principles = Column(Boolean)
    is_info_required_eo = Column(Boolean)
    is_other_info_required = Column(Boolean)
    is_material_amendments = Column(Boolean)
    is_inst_defining_rights = Column(Boolean)
    is_new_or_amended_inv_adv_cont = Column(Boolean)
    is_info_item405 = Column(Boolean)
    is_code_of_ethics = Column(Boolean)

class NCENRegistrant(Base):
    __tablename__ = 'ncen_registrants'
    ncen_registrant_sk = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String(25), nullable=False)
    registrant_name = Column(String(200), nullable=False)
    file_num = Column(String(20))
    cik = Column(String(10))
    lei = Column(String(20))
    address1 = Column(String(100))
    address2 = Column(String(100))
    city = Column(String(50))
    state = Column(String(2))
    country = Column(String(50))
    zip = Column(String(10))
    phone = Column(String(20))
    is_first_filing = Column(Boolean)
    is_last_filing = Column(Boolean)
    is_family_investment_company = Column(Boolean)
    family_investment_company_name = Column(String(200))
    investment_company_type = Column(String(50))
    total_series = Column(Integer)

class NCENFundReportedInfo(Base):
    __tablename__ = 'ncen_fund_reported_info'
    ncen_fund_sk = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(String(50), nullable=False)
    accession_number = Column(String(25), nullable=False)
    fund_name = Column(String(200), nullable=False)
    series_id = Column(String(50))
    lei = Column(String(20))
    is_first_filing = Column(Boolean)
    authorized_shares_cnt = Column(BigInteger)
    added_new_shares_cnt = Column(BigInteger)
    terminated_shares_cnt = Column(BigInteger)
    is_etf = Column(Boolean)
    is_etmf = Column(Boolean)
    is_index = Column(Boolean)
    is_multi_inverse_index = Column(Boolean)
    is_interval = Column(Boolean)
    is_fund_of_fund = Column(Boolean)
    is_master_feeder = Column(Boolean)
    is_money_market = Column(Boolean)
    is_target_date = Column(Boolean)
    is_underlying_fund = Column(Boolean)
    return_b4_fees_and_expenses = Column(Float)
    return_aftr_fees_and_expenses = Column(Float)
    monthly_avg_net_assets = Column(BigInteger)
    daily_avg_net_assets = Column(BigInteger)
    management_fee = Column(Float)
    net_operating_expenses = Column(Float)
    market_price_per_share = Column(Float)
    nav_per_share = Column(Float)

class NCENAdviser(Base):
    __tablename__ = 'ncen_advisers'
    ncen_adviser_sk = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(String(50), nullable=False)
    source = Column(String(20))
    adviser_type = Column(String(50))
    adviser_name = Column(String(200), nullable=False)
    file_num = Column(String(20))
    crd_num = Column(String(20))
    adviser_lei = Column(String(20))
    state = Column(String(2))
    country = Column(String(50))
    is_affiliated = Column(Boolean)
    is_advisor_hired = Column(Boolean)
    advisor_start_date = Column(DateTime)
    advisor_terminated_date = Column(DateTime)

# N-PORT Tables
class NPORTSubmission(Base):
    __tablename__ = 'nport_submissions'
    accession_number = Column(String(25), primary_key=True)
    submission_type = Column(String(20), nullable=True)
    cik = Column(String(10), nullable=True)
    filing_date = Column(DateTime, nullable=False)
    report_date = Column(DateTime, nullable=True)
    registrant_name = Column(String(200), nullable=True)
    file_number = Column(String(20))
    lei = Column(String(20))
    series_id = Column(String(50))
    series_name = Column(String(200))
    class_id = Column(String(50))
    class_name = Column(String(200))
    total_assets = Column(BigInteger)
    total_liabilities = Column(BigInteger)
    net_assets = Column(BigInteger)
    assets_attributable_to_miscellaneous_securities = Column(BigInteger)
    investments_owned_at_value = Column(BigInteger)

class NPORTGeneralInfo(Base):
    __tablename__ = 'nport_general_info'
    nport_general_sk = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String(25), nullable=False)
    registrant_name = Column(String(200))
    file_number = Column(String(20))
    lei = Column(String(20))
    address1 = Column(String(100))
    address2 = Column(String(100))
    city = Column(String(50))
    state_or_country = Column(String(50))
    zip = Column(String(10))
    phone = Column(String(20))
    is_final_filing = Column(Boolean)
    total_assets = Column(BigInteger)
    total_liabilities = Column(BigInteger)
    net_assets = Column(BigInteger)
    miscellaneous_securities_owned = Column(BigInteger)
    investments_owned_at_value = Column(BigInteger)
    uninvested_cash = Column(BigInteger)

class NPORTHolding(Base):
    __tablename__ = 'nport_holdings'
    nport_holding_sk = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String(25), nullable=False)
    holding_id = Column(String(50))
    issuer_name = Column(String(200))
    title_of_issue = Column(String(200))
    cusip = Column(String(9))
    isin = Column(String(12))
    balance_held = Column(BigInteger)
    units_principal_amount = Column(String(20))
    currency_code = Column(String(3))
    value_usd = Column(BigInteger)
    percentage_of_net_assets = Column(Float)
    payoff_profile = Column(String(50))
    asset_category = Column(String(50))
    issuer_category = Column(String(50))
    investment_country = Column(String(2))
    is_restricted_security = Column(Boolean)
    fair_value_level = Column(String(10))
    liquidity_classification = Column(String(50))

class NPORTDerivative(Base):
    __tablename__ = 'nport_derivatives'
    nport_derivative_sk = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String(25), nullable=False)
    derivative_id = Column(String(50))
    counterparty_name = Column(String(200))
    derivative_category = Column(String(50))
    underlying_name = Column(String(200))
    underlying_cusip = Column(String(9))
    underlying_isin = Column(String(12))
    notional_amount = Column(BigInteger)
    currency_code = Column(String(3))
    unrealized_appreciation = Column(BigInteger)
    unrealized_depreciation = Column(BigInteger)
    maturity_date = Column(DateTime)
    expiration_date = Column(DateTime)
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)

# CFTC Swap Data Tables

class CFTCDerivativesDealer(Base):
    """CFTC Swap Dealers and Major Swap Participants"""
    __tablename__ = 'cftc_derivatives_dealers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    legal_name = Column(String(255), nullable=False)
    dftc_swap_dealer_id = Column(String(50), unique=True, nullable=False)
    dftc_major_swap_participant_id = Column(String(50))
    dco_swap_dealer_id = Column(String(50))
    dco_major_swap_participant_id = Column(String(50))
    dcm_swap_dealer_id = Column(String(50))
    dcm_major_swap_participant_id = Column(String(50))
    swap_dealer_status = Column(String(50))
    major_swap_participant_status = Column(String(50))
    registration_status = Column(String(50))
    registration_date = Column(DateTime)
    registration_effective_date = Column(DateTime)
    registration_withdrawal_date = Column(DateTime)
    registration_withdrawal_effective_date = Column(DateTime)
    registration_withdrawal_reason = Column(String(255))
    registration_withdrawal_other_reason = Column(String(255))
    registration_withdrawal_comments = Column(Text)
    registration_withdrawal_filing_date = Column(DateTime)
    registration_withdrawal_effective_date_filing_date = Column(DateTime)
    registration_withdrawal_comments_filing_date = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cftc_derivatives_dealer_legal_name', 'legal_name'),
        Index('idx_cftc_derivatives_dealer_dftc_id', 'dftc_swap_dealer_id'),
        Index('idx_cftc_derivatives_dealer_registration_status', 'registration_status'),
    )

class CFTCDerivativesClearingOrganization(Base):
    """CFTC Derivatives Clearing Organizations"""
    __tablename__ = 'cftc_derivatives_clearing_orgs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    legal_name = Column(String(255), nullable=False)
    dco_id = Column(String(50), unique=True, nullable=False)
    dco_registration_status = Column(String(50))
    dco_registration_date = Column(DateTime)
    dco_registration_effective_date = Column(DateTime)
    dco_registration_withdrawal_date = Column(DateTime)
    dco_registration_withdrawal_effective_date = Column(DateTime)
    dco_registration_withdrawal_reason = Column(String(255))
    dco_registration_withdrawal_other_reason = Column(String(255))
    dco_registration_withdrawal_comments = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cftc_dco_legal_name', 'legal_name'),
        Index('idx_cftc_dco_id', 'dco_id'),
        Index('idx_cftc_dco_registration_status', 'dco_registration_status'),
    )

class CFTCSwapExecutionFacility(Base):
    """CFTC Swap Execution Facilities"""
    __tablename__ = 'cftc_swap_execution_facilities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    legal_name = Column(String(255), nullable=False)
    sef_id = Column(String(50), unique=True, nullable=False)
    sef_registration_status = Column(String(50))
    sef_registration_date = Column(DateTime)
    sef_registration_effective_date = Column(DateTime)
    sef_registration_withdrawal_date = Column(DateTime)
    sef_registration_withdrawal_effective_date = Column(DateTime)
    sef_registration_withdrawal_reason = Column(String(255))
    sef_registration_withdrawal_other_reason = Column(String(255))
    sef_registration_withdrawal_comments = Column(Text)
    sef_website = Column(String(255))
    sef_contact_name = Column(String(100))
    sef_contact_title = Column(String(100))
    sef_contact_phone = Column(String(20))
    sef_contact_email = Column(String(100))
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cftc_sef_legal_name', 'legal_name'),
        Index('idx_cftc_sef_id', 'sef_id'),
        Index('idx_cftc_sef_registration_status', 'sef_registration_status'),
    )

class CFTCSwapDataRepository(Base):
    """CFTC Swap Data Repositories"""
    __tablename__ = 'cftc_swap_data_repositories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    legal_name = Column(String(255), nullable=False)
    sdr_id = Column(String(50), unique=True, nullable=False)
    sdr_registration_status = Column(String(50))
    sdr_registration_date = Column(DateTime)
    sdr_registration_effective_date = Column(DateTime)
    sdr_registration_withdrawal_date = Column(DateTime)
    sdr_registration_withdrawal_effective_date = Column(DateTime)
    sdr_registration_withdrawal_reason = Column(String(255))
    sdr_registration_withdrawal_other_reason = Column(String(255))
    sdr_registration_withdrawal_comments = Column(Text)
    sdr_website = Column(String(255))
    sdr_contact_name = Column(String(100))
    sdr_contact_title = Column(String(100))
    sdr_contact_phone = Column(String(20))
    sdr_contact_email = Column(String(100))
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cftc_sdr_legal_name', 'legal_name'),
        Index('idx_cftc_sdr_id', 'sdr_id'),
        Index('idx_cftc_sdr_registration_status', 'sdr_registration_status'),
    )

class CFTCDailySwapReport(Base):
    """CFTC Daily Swap Report Data"""
    __tablename__ = 'cftc_daily_swap_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(DateTime, nullable=False, index=True)
    asset_class = Column(String(50), nullable=False, index=True)
    product_type = Column(String(100), nullable=False, index=True)
    product_subtype = Column(String(100))
    notional_amount = Column(BigInteger)
    trade_count = Column(Integer)
    counterparty_type = Column(String(50))
    clearing_status = Column(String(50))
    execution_type = Column(String(50))
    block_trade = Column(Boolean)
    block_trade_eligible = Column(Boolean)
    compression_trade = Column(Boolean)
    package_trade = Column(Boolean)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cftc_dsr_date_asset_class', 'report_date', 'asset_class'),
        Index('idx_cftc_dsr_product_type', 'product_type'),
        Index('idx_cftc_dsr_clearing_status', 'clearing_status'),
    )

# N-MFP Tables
class NMFPSubmission(Base):
    __tablename__ = 'nmfp_submissions'
    accession_number = Column(String(25), primary_key=True)
    filing_date = Column(DateTime, nullable=False)
    submission_type = Column(String(20), nullable=False)
    cik = Column(String(10))
    report_date = Column(DateTime, nullable=False)
    registrant_full_name = Column(String(150))
    filer_cik = Column(String(10), nullable=False)
    registrant_leiid = Column(String(20))
    series_name = Column(String(150))
    nameofseries = Column(String(150))
    leiofseries = Column(String(20))
    seriesid = Column(String(10), nullable=False)
    total_share_classes_in_series = Column(Integer, nullable=False)
    final_filing_flag = Column(String(1), nullable=False)
    fund_liquidating_flag = Column(String(1))
    fund_mrg_or_acqrd_by_othr_flag = Column(String(1))
    fund_acqrd_or_mrgd_wth_anthr_flag = Column(String(1))
    registrant = Column(String(150))
    signature_date = Column(DateTime)
    signature = Column(String(150))
    nameofsigning_officer = Column(String(150))
    titleofsigning_officer = Column(String(150))

class NMFPFund(Base):
    __tablename__ = 'nmfp_funds'
    accession_number = Column(String(25), primary_key=True)
    cik = Column(String(10))
    file_number = Column(String(17), primary_key=True)
    seriesid = Column(String(10), primary_key=True)
    fund_type = Column(String(18), primary_key=True)

class NMFPSeriesLevelInfo(Base):
    __tablename__ = 'nmfp_series_level_info'
    accession_number = Column(String(25), primary_key=True)
    securities_act_file_number = Column(String(17))
    ind_pub_acct_name = Column(String(30))
    ind_pub_acct_city = Column(String(17))
    ind_pub_acct_state_country = Column(String(2))
    feeder_fund_flag = Column(String(1), nullable=False)
    master_fund_flag = Column(String(1), nullable=False)
    series_fund_insu_cmpny_sep_accnt_fla = Column(String(1))
    money_market_fund_category = Column(String(300), nullable=False)
    fund_exempt_retail_flag = Column(String(1))
    fund_retail_money_market_flag = Column(String(1))
    gov_money_mrkt_fund_flag = Column(String(1))
    average_portfolio_maturity = Column(Integer, nullable=False)
    average_life_maturity = Column(Integer, nullable=False)
    tot_dly_liquid_asset_friday_week1 = Column(Float)
    tot_dly_liquid_asset_friday_week2 = Column(Float)
    tot_dly_liquid_asset_friday_week3 = Column(Float)
    tot_dly_liquid_asset_friday_week4 = Column(Float)
    tot_dly_liquid_asset_friday_week5 = Column(Float)
    tot_wly_liquid_asset_friday_week1 = Column(Float)
    tot_wly_liquid_asset_friday_week2 = Column(Float)
    tot_wly_liquid_asset_friday_week3 = Column(Float)
    tot_wly_liquid_asset_friday_week4 = Column(Float)
    tot_wly_liquid_asset_friday_week5 = Column(Float)
    pct_dly_liquid_asset_friday_week1 = Column(Float)
    pct_dly_liquid_asset_friday_week2 = Column(Float)
    pct_dly_liquid_asset_friday_week3 = Column(Float)
    pct_dly_liquid_asset_friday_week4 = Column(Float)
    pct_dly_liquid_asset_friday_week5 = Column(Float)
    pct_wkly_liquid_asset_friday_week1 = Column(Float)
    pct_wkly_liquid_asset_friday_week2 = Column(Float)
    pct_wkly_liquid_asset_friday_week3 = Column(Float)
    pct_wkly_liquid_asset_friday_week4 = Column(Float)
    pct_wkly_liquid_asset_friday_week5 = Column(Float)
    cash = Column(Float)
    total_value_portfolio_securities = Column(Float)
    amortized_cost_portfolio_securiti = Column(Float)
    total_value_other_assets = Column(Float, nullable=False)
    total_value_liabilities = Column(Float, nullable=False)
    net_asset_of_series = Column(Float, nullable=False)
    number_of_shares_outstanding = Column(Float)
    seeks_stable_price_per_share = Column(String(1))
    stable_price_per_share = Column(Float)
    seven_day_gross_yield = Column(Float, nullable=False)
    net_asset_value_friday_week1 = Column(Float)
    net_asset_value_friday_week2 = Column(Float)
    net_asset_value_friday_week3 = Column(Float)
    net_asset_value_friday_week4 = Column(Float)
    net_asset_value_friday_week5 = Column(Float)
    cash_mgmt_vehicle_affliated_fund_f = Column(String(1))
    liquidity_fee_fund_apply_flag = Column(String(1))

class NMFPMasterFeederFund(Base):
    __tablename__ = 'nmfp_master_feeder_funds'
    accession_number = Column(String(25), primary_key=True)
    cik = Column(String(10))
    name = Column(String(150))
    file_number = Column(String(17))
    seriesid = Column(String(10), primary_key=True)
    fund_type = Column(String(6), primary_key=True)

class NMFPAdviser(Base):
    __tablename__ = 'nmfp_advisers'
    accession_number = Column(String(25), primary_key=True)
    adviser_name = Column(String(150))
    adviser_file_number = Column(String(17), primary_key=True)
    adviser_type = Column(String(10), primary_key=True)

class NMFPAdministrator(Base):
    __tablename__ = 'nmfp_administrators'
    accession_number = Column(String(25), primary_key=True)
    administrator_name = Column(String(150), primary_key=True)

class NMFPTransferAgent(Base):
    __tablename__ = 'nmfp_transfer_agents'
    accession_number = Column(String(25), primary_key=True)
    name = Column(String(150))
    cik = Column(String(10))
    file_number = Column(String(17), primary_key=True)

class NMFPSeriesShadowPriceL(Base):
    __tablename__ = 'nmfp_series_shadow_price_l'
    accession_number = Column(String(25), primary_key=True)
    net_value_per_share_including_capit = Column(Float, nullable=False)
    net_value_per_share_incap_calc_date = Column(DateTime, nullable=False)
    net_value_per_share_excluding_capit = Column(Float, nullable=False)
    net_value_per_share_excap_calc_date = Column(DateTime, nullable=False)

class NMFPClassLevelInfo(Base):
    __tablename__ = 'nmfp_class_level_info'
    accession_number = Column(String(25), primary_key=True)
    class_name = Column(String(150))
    class_full_name = Column(String(150))
    classesid = Column(String(10), primary_key=True)
    min_initial_investment = Column(Float, nullable=False)
    net_assets_of_class = Column(Float, nullable=False)
    number_of_shares_outstanding = Column(Float)
    net_asset_per_share_friday_week1 = Column(Float)
    net_asset_per_share_friday_week2 = Column(Float)
    net_asset_per_share_friday_week3 = Column(Float)
    net_asset_per_share_friday_week4 = Column(Float)
    net_asset_per_share_friday_week5 = Column(Float)
    gross_subscription_friday_week1 = Column(Float)
    gross_redemption_friday_week1 = Column(Float)
    gross_subscription_friday_week2 = Column(Float)
    gross_redemption_friday_week2 = Column(Float)
    gross_subscription_friday_week3 = Column(Float)
    gross_redemption_friday_week3 = Column(Float)
    gross_subscription_friday_week4 = Column(Float)
    gross_redemption_friday_week4 = Column(Float)
    gross_subscription_friday_week5 = Column(Float)
    gross_redemption_friday_week5 = Column(Float)
    tot_form_nthwly_gross_subscription = Column(Float)
    total_gross_subscriptions = Column(Float)
    tot_form_nthwly_gross_redemption = Column(Float)
    total_gross_redemptions = Column(Float)
    net_asset_value_per_share_l = Column(Float)
    net_shareholder_flow_activity_fo_l = Column(Float)
    seven_day_net_yield = Column(Float)
    person_pay_for_fund_flag = Column(String(1))
    name_of_person_desc_expense_pay = Column(String(400))
    name_of_person_desc_expense_pay_amount = Column(Float)
    pct_shareholder_comp_non_financial = Column(Float)
    pct_shareholder_comp_pension_plan = Column(Float)
    pct_shareholder_comp_non_profit = Column(Float)
    pct_shareholder_comp_municipal = Column(Float)
    pct_shareholder_comp_reg_investme = Column(Float)
    pct_shareholder_comp_private_fund = Column(Float)
    pct_shareholder_comp_depository_i = Column(Float)
    pct_shareholder_comp_sovereign_fu = Column(Float)
    pct_shareholder_comp_broker_deale = Column(Float)
    pct_shareholder_comp_insurance = Column(Float)
    pct_shareholder_comp_other = Column(Float)
    other_investor_type_description = Column(String(250))
    share_cancellation_report_period = Column(String(1))

class NMFPNetAssetValuePerShareL(Base):
    __tablename__ = 'nmfp_net_asset_value_per_share_l'
    accession_number = Column(String(25), primary_key=True)
    classesid = Column(String(10), primary_key=True)
    value = Column(Float, nullable=False)
    date_as_of_which_value_was_calculate = Column(DateTime, nullable=False)
    type = Column(String(2), primary_key=True)

class NMFPSchPortfolioSecurities(Base):
    __tablename__ = 'nmfp_sch_portfolio_securities'
    accession_number = Column(String(25), primary_key=True)
    security_id = Column(Integer, primary_key=True)
    name_of_issuer = Column(String(150), nullable=False)
    title_of_issuer = Column(String(200), nullable=False)
    coupon = Column(String(25))
    cusip_number = Column(String(9))
    lei = Column(String(20))
    isin = Column(String(12))
    cik = Column(String(10))
    rssdid = Column(Integer)
    other_unique_id = Column(String(20))
    investment_category = Column(String(200))
    brief_description = Column(String(250))
    fund_acqstn_undrlyng_security_flag = Column(String(1))
    repurchase_agreement_open_flag = Column(String(1))
    repurchase_agreement_cleared_fla = Column(String(1))
    name_of_ccp = Column(String(150))
    repurchase_agreement_triparty_fl = Column(String(1))
    security_eligibility_flag = Column(String(1))
    investment_maturity_date_wam = Column(DateTime, nullable=False)
    investment_maturity_date_wal = Column(DateTime)
    final_legal_investment_maturity_da = Column(DateTime)
    security_demand_feature_flag = Column(String(1), nullable=False)
    security_guarantee_flag = Column(String(1), nullable=False)
    security_enhancements_flag = Column(String(1), nullable=False)
    yield_of_the_security_as_of_reportin = Column(Float)
    including_value_of_any_sponsor_supp = Column(Float, nullable=False)
    excluding_value_of_any_sponsor_supp = Column(Float, nullable=False)
    percentage_of_money_market_fund_net = Column(Float, nullable=False)
    security_categorized_at_level3_fla = Column(String(1))
    daily_liquid_asset_security_flag = Column(String(1))
    weekly_liquid_asset_security_flag = Column(String(1))
    illiquid_security_flag = Column(String(1))
    explanatory_notes = Column(String(250))
    rating_l = Column(String(250))
    investment_owned_balance_princi_l = Column(Float)
    available_for_sale_securities_am_l = Column(Float)

class NMFPCollateralIssuers(Base):
    __tablename__ = 'nmfp_collateral_issuers'
    accession_number = Column(String(25), primary_key=True)
    security_id = Column(Integer, primary_key=True)
    name_of_collateral_issuer = Column(String(150), primary_key=True)
    lei = Column(String(20))
    cusip_member = Column(String(9))
    collateral_maturity_date = Column(String(10), primary_key=True)
    t_from = Column(String(10))
    t_to = Column(String(10))
    coupon_or_yield = Column(String(25))
    coupon = Column(String(25))
    yield_ = Column(String(25))
    principal_amount_to_the_nearest_cen = Column(Float)
    value_of_collateral_to_the_nearest_c = Column(Float, primary_key=True)
    ctgry_investments_rprsnts_collate = Column(String(100))
    other_instrument_brief_desc = Column(String(250))

class NMFPNrsro(Base):
    __tablename__ = 'nmfp_nrsro'
    accession_number = Column(String(25), primary_key=True)
    security_id = Column(Integer, primary_key=True)
    identity = Column(String(150), primary_key=True)
    type = Column(String(15), primary_key=True)
    name_of_nrsro = Column(String(150), primary_key=True)
    rating = Column(String(20), primary_key=True)

class NMFPDemandFeature(Base):
    __tablename__ = 'nmfp_demand_features'
    accession_number = Column(String(25), primary_key=True)
    security_id = Column(Integer, primary_key=True)
    identity_of_demand_feature_issuer = Column(String(150), primary_key=True)
    amount_provided_by_demand_feature_i = Column(Float)
    remaining_period_demand_feature = Column(Float)
    demand_feature_conditional_flag = Column(String(1))

class NMFPGuarantor(Base):
    __tablename__ = 'nmfp_guarantors'
    accession_number = Column(String(25), primary_key=True)
    security_id = Column(Integer, primary_key=True)
    identity_of_the_guarantor = Column(String(150), primary_key=True)
    amount_provided_by_guarantor = Column(Float)

class NMFPEnhancementProvider(Base):
    __tablename__ = 'nmfp_enhancement_providers'
    accession_number = Column(String(25), primary_key=True)
    security_id = Column(Integer, primary_key=True)
    identity_of_enhancement_provider = Column(String(150), primary_key=True)
    type_of_enhancement = Column(String(150), primary_key=True)
    amount_provided_by_enhancement = Column(Float)

class NMFPLiquidAssetsDetails(Base):
    __tablename__ = 'nmfp_liquid_assets_details'
    accession_number = Column(String(25), primary_key=True)
    tot_value_daily_liquid_assets = Column(Float)
    tot_value_weekly_liquid_assets = Column(Float)
    pct_daily_liquid_assets = Column(Float)
    pct_weekly_liquid_assets = Column(Float)
    tot_liquid_assets_near_pct_date = Column(DateTime, primary_key=True)

class NMFPSevenDayGrossYield(Base):
    __tablename__ = 'nmfp_seven_day_gross_yields'
    accession_number = Column(String(25), primary_key=True)
    seven_day_gross_yield_value = Column(Float)
    seven_day_gross_yield_date = Column(DateTime, primary_key=True)

class NMFPDlyNetAssetValuePerShars(Base):
    __tablename__ = 'nmfp_dly_net_asset_value_per_shars'
    accession_number = Column(String(25), primary_key=True)
    dly_net_asset_value_per_share_ser = Column(Float)
    dly_net_asset_val_per_share_dates = Column(DateTime, primary_key=True)

class NMFPLiquidityFeeReportingPer(Base):
    __tablename__ = 'nmfp_liquidity_fee_reporting_per'
    accession_number = Column(String(25), primary_key=True)
    liquidity_fee_apply_date = Column(DateTime, primary_key=True)
    liquidity_fee_type_for_reptng_peri = Column(String(250))
    liquidity_fee_amt_apply_to_redempt = Column(Float)
    liquidity_fee_pct_shares_redeemed = Column(Float)

class NMFPDlyNetAssetValuePerSharc(Base):
    __tablename__ = 'nmfp_dly_net_asset_value_per_sharc'
    accession_number = Column(String(25), primary_key=True)
    classesid = Column(String(10), primary_key=True)
    dly_net_asset_value_per_share_class = Column(Float)
    dly_net_asset_value_per_share_datec = Column(DateTime, primary_key=True)

class NMFPDlyShareholderFlowReport(Base):
    __tablename__ = 'nmfp_dly_shareholder_flow_reports'
    accession_number = Column(String(25), primary_key=True)
    classesid = Column(String(10))
    daily_gross_subscriptions = Column(Float)
    daily_gross_redemptions = Column(Float)
    daily_shareholder_flow_date = Column(DateTime, primary_key=True)

class NMFPSevenDayNetYield(Base):
    __tablename__ = 'nmfp_seven_day_net_yields'
    accession_number = Column(String(25), primary_key=True)
    classesid = Column(String(10), primary_key=True)
    seven_day_net_yield_value = Column(Float)
    seven_day_net_yield_date = Column(DateTime, primary_key=True)

class NMFPBeneficialRecordOwnerCat(Base):
    __tablename__ = 'nmfp_beneficial_record_owner_cat'
    id = Column(Integer, primary_key=True) # No primary key defined, using auto-incrementing id
    accession_number = Column(String(25), nullable=False)
    classesid = Column(String(10))
    beneficial_record_owner_cate_type = Column(String(200))
    other_investor_category = Column(String(250))
    pct_outstanding_shares_record = Column(Float)
    pct_outstanding_shares_beneficia = Column(Float)

class NMFPCancelledSharesPerBusDay(Base):
    __tablename__ = 'nmfp_cancelled_shares_per_bus_day'
    accession_number = Column(String(25), primary_key=True)
    classesid = Column(String(10), primary_key=True)
    cancelled_share_dollar_value = Column(Float)
    cancelled_share_number = Column(Float)
    cancelled_share_date = Column(DateTime, primary_key=True)

class NMFPDispositionOfPortfolioSecurities(Base):
    __tablename__ = 'nmfp_disposition_of_portfolio_securities'
    accession_number = Column(String(25), primary_key=True)
    security_description = Column(String(150))
    ticker_symbol = Column(String(10))
    cusip = Column(String(9))
    value = Column(Float)
    shares = Column(Float)
    type_of_security = Column(String(50))

class Sec10KSubmission(Base):
    """Stores metadata about 10-K and 10-Q filings."""
    __tablename__ = 'sec_10k_submissions'
    
    accession_number = Column(String(25), primary_key=True)
    cik = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    form_type = Column(String(10), nullable=False)  # 10-K, 10-Q, etc.
    filing_date = Column(DateTime, nullable=False, index=True)
    period_of_report = Column(DateTime, nullable=False)
    acceptance_datetime = Column(DateTime)
    file_number = Column(String(20))
    sec_act = Column(String(50))
    film_number = Column(String(50))
    is_xbrl = Column(Boolean, default=False)
    is_inline_xbrl = Column(Boolean, default=False)
    primary_document = Column(String(255))
    size = Column(Integer)  # Size in bytes
    url = Column(String(500))

class Sec10KDocument(Base):
    """Stores sections of 10-K/10-Q documents."""
    __tablename__ = 'sec_10k_documents'
    
    id = Column(Integer, primary_key=True)
    accession_number = Column(String(25), nullable=False, index=True)
    section = Column(String(50), nullable=False)  # e.g., 'business', 'risk_factors', 'mdna'
    sequence = Column(Integer, nullable=False)  # Order of sections
    content = Column(Text)
    word_count = Column(Integer)
    
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )

class Sec10KFinancials(Base):
    """Stores financial statement data from 10-K/10-Q filings."""
    __tablename__ = 'sec_10k_financials'
    
    id = Column(Integer, primary_key=True)
    accession_number = Column(String(25), nullable=False, index=True)
    statement_type = Column(String(20), nullable=False)  # 'income', 'balance', 'cash_flow'
    period_end = Column(DateTime, nullable=False)
    period_length = Column(String(10))  # 'Q1', 'Q2', 'Q3', 'FY'
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float)
    metric_unit = Column(String(20))  # 'USD', 'shares', etc.
    is_restated = Column(Boolean, default=False)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class Sec10KExhibits(Base):
    """Stores information about exhibits in 10-K/10-Q filings."""
    __tablename__ = 'sec_10k_exhibits'
    
    id = Column(Integer, primary_key=True)
    accession_number = Column(String(25), nullable=False, index=True)
    exhibit_number = Column(String(10), nullable=False)
    exhibit_description = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)  # Size in bytes
    url = Column(String(500))
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class Sec10KMetadata(Base):
    """Stores additional metadata and extracted information from 10-K/10-Q filings."""
    __tablename__ = 'sec_10k_metadata'
    
    accession_number = Column(String(25), primary_key=True)
    fiscal_year = Column(Integer)
    fiscal_period = Column(String(10))  # Q1, Q2, Q3, Q4, FY
    entity_common_stock_shares_outstanding = Column(BigInteger)
    entity_public_float = Column(Float)
    entity_well_known_seasoned_issuer = Column(Boolean)
    entity_voluntary_filers = Column(Boolean)
    entity_small_business = Column(Boolean)
    entity_emerging_growth_company = Column(Boolean)
    entity_exchange_act_report = Column(Boolean)
    entity_shell_company = Column(Boolean)
    filing_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    entity_central_index_key = Column(String(10))
    entity_irs_number = Column(String(20))
    entity_incorporation_state = Column(String(2))
    entity_tax_identification_number = Column(String(20))
    entity_phone_number = Column(String(20))
    entity_former_name = Column(String(255))
    entity_former_conformed_name = Column(String(255))
    entity_date_of_name_change = Column(DateTime)
    entity_fiscal_year_end = Column(String(5))  # MM-DD
    entity_website = Column(String(255))
    entity_business_address = Column(JSON)  # JSON with address fields
    entity_mailing_address = Column(JSON)   # JSON with address fields
    entity_former_business_name = Column(String(255))
    entity_former_conformed_name = Column(String(255))
    entity_former_name_change_date = Column(DateTime)
    entity_registrant_name = Column(String(255))
    entity_edgar_company_conformed_name = Column(String(255))
    entity_standard_industrial_classification = Column(String(10))
    entity_irs_employer_identification_number = Column(String(20))

class Sec8KSubmission(Base):
    """Stores metadata about 8-K filings."""
    __tablename__ = 'sec_8k_submissions'
    
    accession_number = Column(String(25), primary_key=True)
    cik = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    form_type = Column(String(10), nullable=False)  # 8-K, 8-K/A
    filing_date = Column(DateTime, nullable=False, index=True)
    period_of_report = Column(DateTime, nullable=True, default=None)
    acceptance_datetime = Column(DateTime)
    file_number = Column(String(20))
    film_number = Column(String(50))
    items = Column(String(255)) # Comma-separated list of items
    size = Column(Integer)  # Size in bytes
    url = Column(String(500))

class Sec8KItem(Base):
    """Stores individual items from an 8-K filing."""
    __tablename__ = 'sec_8k_items'
    
    id = Column(Integer, primary_key=True)
    accession_number = Column(String(25), nullable=False, index=True)
    item_number = Column(String(20), nullable=False) # e.g., '1.01', '5.02'
    item_title = Column(String(255))
    content = Column(Text)
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    # Audit information
    auditor_name = Column(String(255))
    auditor_location = Column(String(100))
    auditor_cik = Column(String(10))
    auditor_former_name = Column(String(255))
    auditor_independence = Column(Boolean)
    
    # Document metadata
    document_type = Column(String(20))  # 10-K, 10-K/A, 10-Q, 10-Q/A, etc.
    document_period_end_date = Column(DateTime)
    document_fiscal_year_focus = Column(Integer)
    document_fiscal_period_focus = Column(String(10))  # Q1, Q2, Q3, FY
    current_fiscal_year_end_date = Column(String(10))  # YYYY-MM-DD
    amendment_flag = Column(Boolean, default=False)
    amendment_description = Column(Text)
    document_quarterly_report = Column(Boolean)
    document_transition_report = Column(Boolean)
    document_annual_report = Column(Boolean)
    shell_company_report = Column(Boolean)
    interactive_data_flag = Column(Boolean)
    
    # Filing information
    filer_category = Column(String(50))
    filer_status = Column(String(50))
    filer_well_known_seasoned_issuer = Column(Boolean)
    filer_voluntary_filer = Column(Boolean)
    filer_small_reporting_company = Column(Boolean)
    filer_emerging_growth_company = Column(Boolean)
    filer_public_float = Column(Float)
    filer_aggregate_market_value = Column(Float)
    filer_common_equity_outstanding = Column(BigInteger)
    
    # Business information
    business_primary_sic_code = Column(String(10))
    business_address = Column(JSON)  # JSON with address fields
    business_phone = Column(String(20))
    business_mailing_address = Column(JSON)  # JSON with address fields
    
    # Additional metadata
    filing_metadata = Column(JSON)  # For any additional metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    non_us_sovereign_supranat_debt_amt = Column(Float)
    certificate_deposit_amt = Column(Float)
    non_negotiable_time_deposit_amt = Column(Float)
    variable_rate_demand_note_amt = Column(Float)
    other_municipal_security_amt = Column(Float)
    asset_backed_commercial_paper_amt = Column(Float)
    other_asset_backed_securities_amt = Column(Float)
    us_treasury_repurchase_agreem_amt = Column(Float)
    us_govt_agency_repurchase_agreamt = Column(Float)
    other_repurchase_agreement_amt = Column(Float)
    insurance_company_fund_agreem_amt = Column(Float)
    investment_company_amt = Column(Float)
    financial_company_commercial_amt = Column(Float)
    non_financial_comp_commercial_amt = Column(Float)
    tender_option_bond_amt = Column(Float)
    other_instrument_amt = Column(Float)
    other_instrument_brief_descripti = Column(String(250))

class CFTCSwap(Base):
    __tablename__ = 'cftc_swap_data'

    id = Column(Integer, primary_key=True, index=True)
    dissemination_id = Column(String, index=True)
    original_dissemination_id = Column(String)
    action_type = Column(String)
    event_type = Column(String)
    event_timestamp = Column(DateTime)
    amendment_indicator = Column(String)
    asset_class = Column(String)
    product_name = Column(String)
    cleared = Column(String)
    mandatory_clearing_indicator = Column(String)
    execution_timestamp = Column(DateTime)
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    maturity_date_of_the_underlier = Column(DateTime)
    non_standardized_term_indicator = Column(String)
    platform_identifier = Column(String)
    prime_brokerage_transaction_indicator = Column(String)
    block_trade_election_indicator = Column(String)
    large_notional_off_facility_swap_election_indicator = Column(String)
    notional_amount_leg_1 = Column(Float)
    notional_amount_leg_2 = Column(Float)
    notional_currency_leg_1 = Column(String)
    notional_currency_leg_2 = Column(String)
    notional_quantity_leg_1 = Column(Float)
    notional_quantity_leg_2 = Column(Float)
    total_notional_quantity_leg_1 = Column(Float)
    total_notional_quantity_leg_2 = Column(Float)
    quantity_frequency_multiplier_leg_1 = Column(Float)
    quantity_frequency_multiplier_leg_2 = Column(Float)
    quantity_unit_of_measure_leg_1 = Column(String)
    quantity_unit_of_measure_leg_2 = Column(String)
    quantity_frequency_leg_1 = Column(String)
    quantity_frequency_leg_2 = Column(String)
    notional_amount_in_effect_on_associated_effective_date_leg_1 = Column(Float)
    notional_amount_in_effect_on_associated_effective_date_leg_2 = Column(Float)
    effective_date_of_the_notional_amount_leg_1 = Column(DateTime)
    effective_date_of_the_notional_amount_leg_2 = Column(DateTime)
    end_date_of_the_notional_amount_leg_1 = Column(DateTime)
    end_date_of_the_notional_amount_leg_2 = Column(DateTime)
    call_amount_leg_1 = Column(Float)
    call_amount_leg_2 = Column(Float)
    call_currency_leg_1 = Column(String)
    call_currency_leg_2 = Column(String)
    put_amount_leg_1 = Column(Float)
    put_amount_leg_2 = Column(Float)
    put_currency_leg_1 = Column(String)
    put_currency_leg_2 = Column(String)
    exchange_rate = Column(Float)
    exchange_rate_basis = Column(String)
    first_exercise_date = Column(DateTime)
    fixed_rate_leg_1 = Column(Float)
    fixed_rate_leg_2 = Column(Float)
    option_premium_amount = Column(Float)
    option_premium_currency = Column(String)
    price = Column(Float)
    price_unit_of_measure = Column(String)
    spread_leg_1 = Column(Float)
    spread_leg_2 = Column(Float)
    spread_currency_leg_1 = Column(String)
    spread_currency_leg_2 = Column(String)
    strike_price = Column(Float)
    strike_price_currency_currency_pair = Column(String)
    post_priced_swap_indicator = Column(String)
    price_currency = Column(String)
    price_notation = Column(String)
    spread_notation_leg_1 = Column(String)
    spread_notation_leg_2 = Column(String)
    strike_price_notation = Column(String)
    fixed_rate_day_count_convention_leg_1 = Column(String)
    fixed_rate_day_count_convention_leg_2 = Column(String)
    floating_rate_day_count_convention_leg_1 = Column(String)
    floating_rate_day_count_convention_leg_2 = Column(String)
    floating_rate_reset_frequency_period_leg_1 = Column(String)
    floating_rate_reset_frequency_period_leg_2 = Column(String)
    floating_rate_reset_frequency_period_multiplier_leg_1 = Column(Float)
    floating_rate_reset_frequency_period_multiplier_leg_2 = Column(Float)
    other_payment_amount = Column(Float)
    fixed_rate_payment_frequency_period_leg_1 = Column(String)
    floating_rate_payment_frequency_period_leg_1 = Column(String)
    fixed_rate_payment_frequency_period_leg_2 = Column(String)
    floating_rate_payment_frequency_period_leg_2 = Column(String)
    fixed_rate_payment_frequency_period_multiplier_leg_1 = Column(Float)
    floating_rate_payment_frequency_period_multiplier_leg_1 = Column(Float)
    fixed_rate_payment_frequency_period_multiplier_leg_2 = Column(Float)
    floating_rate_payment_frequency_period_multiplier_leg_2 = Column(Float)
    other_payment_type = Column(String)
    other_payment_currency = Column(String)
    settlement_currency_leg_1 = Column(String)
    settlement_currency_leg_2 = Column(String)
    settlement_location_leg_1 = Column(String)
    settlement_location_leg_2 = Column(String)
    collateralisation_category = Column(String)
    custom_basket_indicator = Column(String)
    index_factor = Column(Float)
    underlier_id_leg_1 = Column(String)
    underlier_id_leg_2 = Column(String)
    underlier_id_source_leg_1 = Column(String)
    underlying_asset_name = Column(String)
    underlying_asset_subtype_or_underlying_contract_subtype_leg_1 = Column(String)
    underlying_asset_subtype_or_underlying_contract_subtype_leg_2 = Column(String)
    embedded_option_type = Column(String)
    option_type = Column(String)
    option_style = Column(String)
    package_indicator = Column(String)
    package_transaction_price = Column(Float)
    package_transaction_price_currency = Column(String)
    package_transaction_price_notation = Column(String)
    package_transaction_spread = Column(Float)
    package_transaction_spread_currency = Column(String)
    package_transaction_spread_notation = Column(String)
    physical_delivery_location_leg_1 = Column(String)
    delivery_type = Column(String)

# Form D Tables
class FormDSubmission(Base):
    __tablename__ = 'formd_submissions'
    accessionnumber = Column(String(25), primary_key=True)
    file_num = Column(String(20), nullable=True)
    filing_date = Column(String(20), nullable=True)  # Store as string, convert during processing
    sic_code = Column(String(10), nullable=True)
    schemaversion = Column(String(10), nullable=True)
    submissiontype = Column(String(20), nullable=True)
    testorlive = Column(String(10), nullable=True)
    over100personsflag = Column(String(10), nullable=True)
    over100issuerflag = Column(String(10), nullable=True)

class FormDIssuer(Base):
    __tablename__ = 'formd_issuers'
    formd_issuer_sk = Column(Integer, primary_key=True, autoincrement=True)
    accessionnumber = Column(String(25), nullable=False)
    is_primaryissuer_flag = Column(String(10), nullable=True)
    issuer_seq_key = Column(Integer, nullable=True)
    cik = Column(String(10), nullable=True)
    entityname = Column(String(200), nullable=True)
    street1 = Column(String(100), nullable=True)
    street2 = Column(String(100), nullable=True)
    city = Column(String(50), nullable=True)
    stateorcountry = Column(String(10), nullable=True)
    stateorcountrydescription = Column(String(50), nullable=True)
    zipcode = Column(String(15), nullable=True)
    issuerphonenumber = Column(String(20), nullable=True)
    jurisdictionofinc = Column(String(10), nullable=True)
    issuer_previousname_1 = Column(String(200), nullable=True)
    issuer_previousname_2 = Column(String(200), nullable=True)
    issuer_previousname_3 = Column(String(200), nullable=True)
    edgar_previousname_1 = Column(String(200), nullable=True)
    edgar_previousname_2 = Column(String(200), nullable=True)
    edgar_previousname_3 = Column(String(200), nullable=True)
    entitytype = Column(String(50), nullable=True)
    entitytypeotherdesc = Column(String(100), nullable=True)
    yearofinc_timespan_choice = Column(String(20), nullable=True)
    yearofinc_value_entered = Column(String(10), nullable=True)

class FormDOffering(Base):
    __tablename__ = 'formd_offerings'
    formd_offering_sk = Column(Integer, primary_key=True, autoincrement=True)
    accessionnumber = Column(String(25), nullable=False)
    industrygrouptype = Column(String(50), nullable=True)
    investmentfundtype = Column(String(50), nullable=True)
    is40act = Column(String(10), nullable=True)
    revenuerange = Column(String(50), nullable=True)
    aggregatenetassetvaluerange = Column(String(50), nullable=True)
    federalexemptions_items_list = Column(String(200), nullable=True)
    isamendment = Column(String(10), nullable=True)
    previousaccessionnumber = Column(String(25), nullable=True)
    sale_date = Column(String(20), nullable=True)
    yettooccur = Column(String(10), nullable=True)
    morethanoneyear = Column(String(10), nullable=True)
    isequitytype = Column(String(10), nullable=True)
    isdebttype = Column(String(10), nullable=True)
    isoptiontoacquiretype = Column(String(10), nullable=True)
    issecuritytobeacquiredtype = Column(String(10), nullable=True)
    ispooledinvestmentfundtype = Column(String(10), nullable=True)
    istenantincommontype = Column(String(10), nullable=True)
    ismineralpropertytype = Column(String(10), nullable=True)
    isothertype = Column(String(10), nullable=True)
    descriptionofothertype = Column(String(200), nullable=True)
    isbusinesscombinationtrans = Column(String(10), nullable=True)
    buscombclarificationofresp = Column(String(200), nullable=True)
    minimuminvestmentaccepted = Column(String(20), nullable=True)
    over100recipientflag = Column(String(10), nullable=True)
    totalofferingamount = Column(String(20), nullable=True)
    totalamountsold = Column(String(20), nullable=True)
    totalremaining = Column(String(20), nullable=True)
    salesamtclarificationofresp = Column(String(200), nullable=True)
    hasnonaccreditedinvestors = Column(String(10), nullable=True)
    numbernonaccreditedinvestors = Column(String(10), nullable=True)
    totalnumberalreadyinvested = Column(String(10), nullable=True)
    salescomm_dollaramount = Column(String(20), nullable=True)
    salescomm_isestimate = Column(String(10), nullable=True)
    findersfee_dollaramount = Column(String(20), nullable=True)
    findersfee_isestimate = Column(String(10), nullable=True)
    finderfeeclarificationofresp = Column(String(200), nullable=True)
    grossproceedsused_dollaramount = Column(String(20), nullable=True)
    grossproceedsused_isestimate = Column(String(10), nullable=True)
    grossproceedsused_clarofresp = Column(String(200), nullable=True)
    authorizedrepresentative = Column(String(200), nullable=True)

class FormDRecipient(Base):
    __tablename__ = 'formd_recipients'
    formd_recipient_sk = Column(Integer, primary_key=True, autoincrement=True)
    accessionnumber = Column(String(25), nullable=False)
    recipient_seq_key = Column(Integer, nullable=True)
    recipientname = Column(String(200), nullable=True)
    recipientcrdnumber = Column(String(20), nullable=True)
    associatedbdname = Column(String(200), nullable=True)
    associatedbdcrdnumber = Column(String(20), nullable=True)
    street1 = Column(String(100), nullable=True)
    street2 = Column(String(100), nullable=True)
    city = Column(String(50), nullable=True)
    stateorcountry = Column(String(10), nullable=True)
    stateorcountrydescription = Column(String(50), nullable=True)
    zipcode = Column(String(15), nullable=True)
    states_or_value_list = Column(String(200), nullable=True)
    descriptions_list = Column(String(500), nullable=True)
    foreignsolicitation = Column(String(10), nullable=True)

class FormDRelatedPerson(Base):
    __tablename__ = 'formd_related_persons'
    formd_related_person_sk = Column(Integer, primary_key=True, autoincrement=True)
    accessionnumber = Column(String(25), nullable=False)
    relatedperson_seq_key = Column(Integer, nullable=True)
    firstname = Column(String(50), nullable=True)
    middlename = Column(String(50), nullable=True)
    lastname = Column(String(50), nullable=True)
    street1 = Column(String(100), nullable=True)
    street2 = Column(String(100), nullable=True)
    city = Column(String(50), nullable=True)
    stateorcountry = Column(String(10), nullable=True)
    stateorcountrydescription = Column(String(50), nullable=True)
    zipcode = Column(String(15), nullable=True)
    relationship_1 = Column(String(50), nullable=True)
    relationship_2 = Column(String(50), nullable=True)
    relationship_3 = Column(String(50), nullable=True)
    relationshipclarification = Column(String(200), nullable=True)

class FormDSignature(Base):
    __tablename__ = 'formd_signatures'
    formd_signature_sk = Column(Integer, primary_key=True, autoincrement=True)
    accessionnumber = Column(String(25), nullable=False)
    signature_seq_key = Column(Integer, nullable=True)
    issuername = Column(String(200), nullable=True)
    signaturename = Column(String(100), nullable=True)
    nameofsigner = Column(String(100), nullable=True)
    signaturetitle = Column(String(100), nullable=True)
    signaturedate = Column(String(20), nullable=True)  # Store as string, convert during processing

def create_db_and_tables():
    """Create database tables if they don't exist. Safe to run multiple times."""
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False

def get_db_stats(db_session=None):
    """Returns a dictionary with table names and their row counts."""
    from sqlalchemy import inspect

    db = db_session if db_session else SessionLocal()
    try:
        inspector = inspect(db.bind)
        stats = {}
        # Create a mapping from table names to model classes
        table_to_model = {cls.class_.__tablename__: cls for cls in Base.registry.mappers}

        for table_name in inspector.get_table_names():
            model_class = table_to_model.get(table_name)
            if model_class:
                count = db.query(model_class.class_).count()
                stats[table_name] = count
        return stats
    finally:
        if not db_session:
            db.close()

def export_db_to_csv(output_path):
    """Exports the CFTC Swap data to a CSV file."""
    db = SessionLocal()
    try:
        query = db.query(CFTCSwap)
        df = pd.read_sql(query.statement, db.bind)
        df.to_csv(output_path, index=False)
        print(f"Database exported to {output_path}")
    finally:
        db.close()

def reset_database():
    """Drops all tables and recreates them."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database has been reset.")
