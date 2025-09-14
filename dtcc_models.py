"""
DTCC Data Models for the GameCockAI system.

This module contains SQLAlchemy models for DTCC (Depository Trust & Clearing Corporation) data,
including interest rate swaps, credit default swaps, equity derivatives, and other OTC derivatives.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Numeric, Text, Index, BigInteger, JSON, Table
)
from sqlalchemy.orm import relationship

# Import Base from database to avoid circular imports
from database import Base

class DTCCOrganization(Base):
    """Stores information about organizations involved in DTCC transactions."""
    __tablename__ = 'dtcc_organizations'
    
    id = Column(Integer, primary_key=True, index=True)
    lei = Column(String(20), unique=True, index=True, nullable=True)  # Legal Entity Identifier
    name = Column(String(255), nullable=False)
    duns_number = Column(String(20), index=True, nullable=True)
    entity_type = Column(String(100), nullable=True)
    registration_status = Column(String(50), nullable=True)
    registration_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_dtcc_org_lei', 'lei'),
        Index('idx_dtcc_org_name', 'name'),
        Index('idx_dtcc_org_duns', 'duns_number'),
    )

class DTCCTrade(Base):
    """Base class for DTCC trade data with common fields."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(100), unique=True, nullable=False, index=True)
    execution_timestamp = Column(DateTime, nullable=False, index=True)
    effective_date = Column(DateTime, nullable=False, index=True)
    termination_date = Column(DateTime, nullable=True, index=True)
    notional_amount = Column(Numeric(20, 2), nullable=True)
    notional_currency = Column(String(3), nullable=True)
    trade_status = Column(String(50), nullable=False, default='ACTIVE')
    clearing_status = Column(String(50), nullable=True)
    asset_class = Column(String(50), nullable=False, index=True)
    product_type = Column(String(100), nullable=False, index=True)
    product_subtype = Column(String(100), nullable=True)
    trade_type = Column(String(50), nullable=True)
    block_trade = Column(Boolean, default=False)
    package_trade = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class DTCCInterestRateSwap(DTCCTrade):
    """Stores DTCC interest rate swap data."""
    __tablename__ = 'dtcc_interest_rate_swaps'
    
    # Counterparties
    reporting_party_lei = Column(String(20), nullable=False, index=True)
    other_party_lei = Column(String(20), nullable=False, index=True)
    
    # Fixed leg details
    fixed_rate = Column(Numeric(10, 6), nullable=True)
    fixed_rate_day_count = Column(String(20), nullable=True)
    fixed_payment_freq = Column(String(20), nullable=True)
    fixed_payment_freq_mult = Column(Integer, nullable=True)
    
    # Floating leg details
    floating_index = Column(String(50), nullable=True)  # e.g., LIBOR, SOFR, etc.
    floating_rate_spread = Column(Numeric(10, 6), nullable=True)
    floating_rate_day_count = Column(String(20), nullable=True)
    floating_payment_freq = Column(String(20), nullable=True)
    floating_payment_freq_mult = Column(Integer, nullable=True)
    floating_reset_freq = Column(String(20), nullable=True)
    floating_reset_freq_mult = Column(Integer, nullable=True)
    
    # Additional IRS-specific fields
    day_count_convention = Column(String(20), nullable=True)
    business_day_convention = Column(String(20), nullable=True)
    calendar = Column(String(50), nullable=True)
    
    __table_args__ = (
        Index('idx_dtcc_irs_trade_id', 'trade_id'),
        Index('idx_dtcc_irs_execution', 'execution_timestamp'),
        Index('idx_dtcc_irs_effective', 'effective_date'),
        Index('idx_dtcc_irs_termination', 'termination_date'),
        Index('idx_dtcc_irs_reporting_party', 'reporting_party_lei'),
        Index('idx_dtcc_irs_other_party', 'other_party_lei'),
    )

class DTCCOptionStrategyLeg(Base):
    """Stores individual legs of option strategies."""
    __tablename__ = 'dtcc_option_strategy_legs'
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String(100), ForeignKey('dtcc_option_strategy_trades.trade_id'), nullable=False, index=True)
    leg_number = Column(Integer, nullable=False)
    option_type = Column(String(10), nullable=False)  # CALL, PUT, etc.
    strike_price = Column(Numeric(20, 6), nullable=True)
    strike_currency = Column(String(3), nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    exercise_style = Column(String(20), nullable=True)  # AMERICAN, EUROPEAN, BERMUDAN
    premium = Column(Numeric(20, 2), nullable=True)
    premium_currency = Column(String(3), nullable=True)
    premium_payment_date = Column(DateTime, nullable=True)
    
    # Relationship to the parent strategy trade
    strategy_trade = relationship("DTCCOptionStrategyTrade", back_populates="legs")
    
    __table_args__ = (
        Index('idx_dtcc_opt_strat_leg', 'trade_id', 'leg_number'),
    )

class DTCCOptionTrade(DTCCTrade):
    """Stores DTCC option trade data."""
    __tablename__ = 'dtcc_option_trades'
    
    # Relationship to equity option if this is an equity option
    equity_option = relationship("DTCCEquityOption", back_populates="option_trade", uselist=False)
    
    # Counterparties
    reporting_party_lei = Column(String(20), nullable=False, index=True)
    other_party_lei = Column(String(20), nullable=False, index=True)
    
    # Underlying asset details
    underlying_asset = Column(String(100), nullable=True, index=True)
    underlying_asset_id = Column(String(50), nullable=True, index=True)
    underlying_asset_id_type = Column(String(20), nullable=True)  # ISIN, CUSIP, etc.
    
    # Option details
    option_style = Column(String(20), nullable=True)  # AMERICAN, EUROPEAN, BERMUDAN
    option_type = Column(String(10), nullable=True)  # CALL, PUT, etc.
    strike_price = Column(Numeric(20, 6), nullable=True)
    strike_currency = Column(String(3), nullable=True)
    expiration_date = Column(DateTime, nullable=True, index=True)
    exercise_settlement_type = Column(String(20), nullable=True)  # CASH, PHYSICAL
    
    # Premium details
    premium_amount = Column(Numeric(20, 2), nullable=True)
    premium_currency = Column(String(3), nullable=True)
    premium_payment_date = Column(DateTime, nullable=True)
    
    # Multi-leg strategies
    is_multi_leg = Column(Boolean, default=False)
    strategy_type = Column(String(50), nullable=True)  # VERTICAL_SPREAD, STRADDLE, etc.
    
    # Additional fields
    day_count_convention = Column(String(20), nullable=True)
    business_day_convention = Column(String(20), nullable=True)
    calendar = Column(String(50), nullable=True)
    
    __table_args__ = (
        Index('idx_dtcc_opt_trade_id', 'trade_id'),
        Index('idx_dtcc_opt_underlying', 'underlying_asset'),
        Index('idx_dtcc_opt_expiration', 'expiration_date'),
        Index('idx_dtcc_opt_reporting_party', 'reporting_party_lei'),
        Index('idx_dtcc_opt_other_party', 'other_party_lei'),
    )

class DTCCEquityOption(Base):
    """Stores DTCC equity option data."""
    __tablename__ = 'dtcc_equity_options'
    
    # Primary key and foreign key to the base option trade
    id = Column(Integer, primary_key=True)
    trade_id = Column(String(100), ForeignKey('dtcc_option_trades.trade_id'), nullable=False, unique=True)
    
    # Relationship to the base option trade
    option_trade = relationship("DTCCOptionTrade", back_populates="equity_option")
    
    # Additional equity-specific fields
    security_type = Column(String(50), nullable=True)  # STOCK, ETF, INDEX, etc.
    security_description = Column(String(255), nullable=True)
    
    __table_args__ = (
        Index('idx_dtcc_eq_opt_security_type', 'security_type'),
        Index('idx_dtcc_eq_opt_trade_id', 'trade_id'),
    )

class DTCCOptionExercise(Base):
    """Tracks option exercises and assignments."""
    __tablename__ = 'dtcc_option_exercises'
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String(100), nullable=False, index=True)
    exercise_id = Column(String(100), nullable=False, index=True)
    exercise_date = Column(DateTime, nullable=False, index=True)
    exercise_type = Column(String(20), nullable=False)  # EXERCISE, ASSIGNMENT, EXPIRATION
    quantity = Column(Numeric(20, 2), nullable=False)
    settlement_amount = Column(Numeric(20, 2), nullable=True)
    settlement_currency = Column(String(3), nullable=True)
    settlement_date = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_dtcc_opt_ex_trade_id', 'trade_id'),
        Index('idx_dtcc_opt_ex_exercise_id', 'exercise_id'),
        Index('idx_dtcc_opt_ex_date', 'exercise_date'),
    )

class DTCCOptionPosition(Base):
    """Tracks option positions."""
    __tablename__ = 'dtcc_option_positions'
    
    id = Column(Integer, primary_key=True)
    position_id = Column(String(100), nullable=False, index=True)
    trade_id = Column(String(100), nullable=False, index=True)
    position_date = Column(DateTime, nullable=False, index=True)
    position_status = Column(String(20), nullable=False)  # OPEN, CLOSED, EXERCISED, EXPIRED
    quantity = Column(Numeric(20, 2), nullable=False)
    cost_basis = Column(Numeric(20, 2), nullable=True)
    cost_basis_currency = Column(String(3), nullable=True)
    
    __table_args__ = (
        Index('idx_dtcc_opt_pos_id', 'position_id'),
        Index('idx_dtcc_opt_pos_trade_id', 'trade_id'),
        Index('idx_dtcc_opt_pos_date', 'position_date'),
    )

class DTCCOptionSettlement(Base):
    """Tracks option settlements."""
    __tablename__ = 'dtcc_option_settlements'
    
    id = Column(Integer, primary_key=True)
    settlement_id = Column(String(100), nullable=False, index=True)
    trade_id = Column(String(100), nullable=False, index=True)
    settlement_date = Column(DateTime, nullable=False, index=True)
    settlement_amount = Column(Numeric(20, 2), nullable=False)
    settlement_currency = Column(String(3), nullable=False)
    settlement_type = Column(String(20), nullable=False)  # PREMIUM, EXERCISE, ASSIGNMENT
    
    __table_args__ = (
        Index('idx_dtcc_opt_settle_id', 'settlement_id'),
        Index('idx_dtcc_opt_settle_trade_id', 'trade_id'),
        Index('idx_dtcc_opt_settle_date', 'settlement_date'),
    )

class DTCCOptionTradeLeg(Base):
    """Stores individual legs of option trades."""
    __tablename__ = 'dtcc_option_trade_legs'
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String(100), nullable=False, index=True)
    leg_number = Column(Integer, nullable=False)
    option_type = Column(String(10), nullable=False)  # CALL, PUT, etc.
    strike_price = Column(Numeric(20, 6), nullable=True)
    strike_currency = Column(String(3), nullable=True)
    expiration_date = Column(DateTime, nullable=True, index=True)
    exercise_style = Column(String(20), nullable=True)  # AMERICAN, EUROPEAN, BERMUDAN
    premium = Column(Numeric(20, 2), nullable=True)
    premium_currency = Column(String(3), nullable=True)
    premium_payment_date = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_dtcc_opt_leg_trade_id', 'trade_id', 'leg_number'),
    )


class DTCCOptionStrategyTrade(DTCCTrade):
    """Stores option strategy trades (e.g., spreads, strangles, etc.)."""
    __tablename__ = 'dtcc_option_strategy_trades'
    
    # Relationship to strategy legs
    legs = relationship("DTCCOptionStrategyLeg", back_populates="strategy_trade")
    
    # Counterparties
    reporting_party_lei = Column(String(20), nullable=False, index=True)
    other_party_lei = Column(String(20), nullable=False, index=True)
    
    # Strategy details
    strategy_type = Column(String(50), nullable=True)  # VERTICAL_SPREAD, STRADDLE, etc.
    
    # Premium details
    net_premium_amount = Column(Numeric(20, 2), nullable=True)
    net_premium_currency = Column(String(3), nullable=True)
    premium_payment_date = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_dtcc_opt_strat_trade_id', 'trade_id'),
        Index('idx_dtcc_opt_strat_type', 'strategy_type'),
        Index('idx_dtcc_opt_strat_reporting', 'reporting_party_lei'),
        Index('idx_dtcc_opt_strat_other_party', 'other_party_lei'),
    )
