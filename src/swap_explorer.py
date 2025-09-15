"""
Comprehensive Swap Explorer & Single Party Risk Analyzer

This module provides the core functionality for aggregating and analyzing ALL swap data sources
to identify single party risk triggers and obligations across multiple filings.

Features:
- Multi-Source Data Aggregation (CFTC, DTCC, SEC, ISDA, CCP)
- Single Party Risk Consolidation
- Risk Trigger Detection Engine
- Obligation Tracking System
- Cross-Filing Correlation Analysis
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AssetClass(Enum):
    """Asset class classifications for swaps"""
    INTEREST_RATE = "interest_rate"
    CREDIT = "credit"
    EQUITY = "equity"
    FOREX = "forex"
    COMMODITY = "commodity"

@dataclass
class EntityIdentifier:
    """Entity identification across different data sources"""
    lei: Optional[str] = None
    cik: Optional[str] = None
    cusip: Optional[str] = None
    ticker: Optional[str] = None
    name: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    parent_entity: Optional[str] = None
    subsidiary_entities: List[str] = field(default_factory=list)

@dataclass
class SwapExposure:
    """Individual swap exposure record"""
    entity_id: str
    counterparty_id: str
    asset_class: AssetClass
    notional_amount: float
    market_value: float
    maturity_date: datetime
    trade_date: datetime
    data_source: str
    filing_reference: Optional[str] = None
    risk_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class RiskTrigger:
    """Risk trigger event"""
    entity_id: str
    trigger_type: str
    severity: RiskLevel
    description: str
    trigger_date: datetime
    impact_amount: Optional[float] = None
    mitigation_actions: List[str] = field(default_factory=list)

@dataclass
class Obligation:
    """Swap-related obligation"""
    entity_id: str
    obligation_type: str  # payment, collateral, settlement, regulatory
    amount: float
    due_date: datetime
    counterparty_id: Optional[str] = None
    description: str = ""
    status: str = "pending"  # pending, completed, overdue

class SwapExplorer:
    """
    Comprehensive Swap Explorer & Single Party Risk Analyzer
    
    Aggregates swap data from multiple sources and provides risk analysis
    """
    
    def __init__(self, db_path: str = "gamecock.db"):
        """Initialize the Swap Explorer"""
        self.db_path = db_path
        self.entity_registry: Dict[str, EntityIdentifier] = {}
        self.swap_exposures: List[SwapExposure] = []
        self.risk_triggers: List[RiskTrigger] = []
        self.obligations: List[Obligation] = []
        
        # Initialize database connection
        self._init_database()
        
        logger.info("Swap Explorer initialized successfully")
    
    def _init_database(self):
        """Initialize database tables for swap explorer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create entity registry table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_registry (
                    entity_id TEXT PRIMARY KEY,
                    lei TEXT,
                    cik TEXT,
                    cusip TEXT,
                    ticker TEXT,
                    name TEXT,
                    aliases TEXT,
                    parent_entity TEXT,
                    subsidiary_entities TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create swap exposures table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS swap_exposures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT,
                    counterparty_id TEXT,
                    asset_class TEXT,
                    notional_amount REAL,
                    market_value REAL,
                    maturity_date TIMESTAMP,
                    trade_date TIMESTAMP,
                    data_source TEXT,
                    filing_reference TEXT,
                    risk_metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entity_id) REFERENCES entity_registry (entity_id)
                )
            """)
            
            # Create risk triggers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT,
                    trigger_type TEXT,
                    severity TEXT,
                    description TEXT,
                    trigger_date TIMESTAMP,
                    impact_amount REAL,
                    mitigation_actions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entity_id) REFERENCES entity_registry (entity_id)
                )
            """)
            
            # Create obligations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS obligations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT,
                    obligation_type TEXT,
                    amount REAL,
                    due_date TIMESTAMP,
                    counterparty_id TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entity_id) REFERENCES entity_registry (entity_id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def register_entity(self, entity_id: str, identifier: EntityIdentifier) -> bool:
        """
        Register an entity with its identifiers
        
        Args:
            entity_id: Unique entity identifier
            identifier: EntityIdentifier object with all identifiers
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO entity_registry 
                (entity_id, lei, cik, cusip, ticker, name, aliases, parent_entity, subsidiary_entities, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity_id,
                identifier.lei,
                identifier.cik,
                identifier.cusip,
                identifier.ticker,
                identifier.name,
                json.dumps(identifier.aliases),
                identifier.parent_entity,
                json.dumps(identifier.subsidiary_entities),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            self.entity_registry[entity_id] = identifier
            logger.info(f"Entity {entity_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering entity {entity_id}: {e}")
            return False
    
    def add_swap_exposure(self, exposure: SwapExposure) -> bool:
        """
        Add a swap exposure to the system
        
        Args:
            exposure: SwapExposure object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO swap_exposures 
                (entity_id, counterparty_id, asset_class, notional_amount, market_value, 
                 maturity_date, trade_date, data_source, filing_reference, risk_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                exposure.entity_id,
                exposure.counterparty_id,
                exposure.asset_class.value,
                exposure.notional_amount,
                exposure.market_value,
                exposure.maturity_date,
                exposure.trade_date,
                exposure.data_source,
                exposure.filing_reference,
                json.dumps(exposure.risk_metrics)
            ))
            
            conn.commit()
            conn.close()
            
            self.swap_exposures.append(exposure)
            logger.info(f"Swap exposure added for entity {exposure.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding swap exposure: {e}")
            return False
    
    def get_entity_exposure_summary(self, entity_id: str) -> Dict[str, Any]:
        """
        Get comprehensive exposure summary for an entity
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Dict containing exposure summary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get total exposure by asset class
            exposure_query = """
                SELECT asset_class, 
                       SUM(notional_amount) as total_notional,
                       SUM(market_value) as total_market_value,
                       COUNT(*) as position_count
                FROM swap_exposures 
                WHERE entity_id = ?
                GROUP BY asset_class
            """
            
            exposure_df = pd.read_sql_query(exposure_query, conn, params=(entity_id,))
            
            # Get counterparty exposure
            counterparty_query = """
                SELECT counterparty_id,
                       SUM(notional_amount) as total_notional,
                       SUM(market_value) as total_market_value,
                       COUNT(*) as position_count
                FROM swap_exposures 
                WHERE entity_id = ?
                GROUP BY counterparty_id
                ORDER BY total_notional DESC
            """
            
            counterparty_df = pd.read_sql_query(counterparty_query, conn, params=(entity_id,))
            
            # Get risk triggers
            triggers_query = """
                SELECT trigger_type, severity, description, trigger_date, impact_amount
                FROM risk_triggers 
                WHERE entity_id = ?
                ORDER BY trigger_date DESC
            """
            
            triggers_df = pd.read_sql_query(triggers_query, conn, params=(entity_id,))
            
            # Get obligations
            obligations_query = """
                SELECT obligation_type, amount, due_date, status
                FROM obligations 
                WHERE entity_id = ?
                ORDER BY due_date
            """
            
            obligations_df = pd.read_sql_query(obligations_query, conn, params=(entity_id,))
            
            conn.close()
            
            # Calculate summary metrics
            total_notional = exposure_df['total_notional'].sum() if not exposure_df.empty else 0
            total_market_value = exposure_df['total_market_value'].sum() if not exposure_df.empty else 0
            total_positions = exposure_df['position_count'].sum() if not exposure_df.empty else 0
            counterparty_count = len(counterparty_df)
            
            # Calculate upcoming obligations
            if not obligations_df.empty:
                # Ensure due_date is datetime type
                obligations_df['due_date'] = pd.to_datetime(obligations_df['due_date'])
                upcoming_obligations = obligations_df[
                    (obligations_df['due_date'] <= datetime.now() + timedelta(days=30)) &
                    (obligations_df['status'] == 'pending')
                ]
            else:
                upcoming_obligations = pd.DataFrame()
            
            upcoming_amount = upcoming_obligations['amount'].sum() if not upcoming_obligations.empty else 0
            
            summary = {
                'entity_id': entity_id,
                'total_notional_exposure': total_notional,
                'total_market_value': total_market_value,
                'total_positions': total_positions,
                'counterparty_count': counterparty_count,
                'exposure_by_asset_class': exposure_df.to_dict('records') if not exposure_df.empty else [],
                'top_counterparties': counterparty_df.head(10).to_dict('records') if not counterparty_df.empty else [],
                'active_risk_triggers': triggers_df.to_dict('records') if not triggers_df.empty else [],
                'upcoming_obligations_30d': upcoming_amount,
                'total_obligations': obligations_df['amount'].sum() if not obligations_df.empty else 0,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Generated exposure summary for entity {entity_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating exposure summary for {entity_id}: {e}")
            return {}
    
    def detect_risk_triggers(self, entity_id: str) -> List[RiskTrigger]:
        """
        Detect risk triggers for an entity
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            List of RiskTrigger objects
        """
        triggers = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get entity exposures
            exposure_query = """
                SELECT * FROM swap_exposures WHERE entity_id = ?
            """
            exposures_df = pd.read_sql_query(exposure_query, conn, params=(entity_id,))
            
            if exposures_df.empty:
                conn.close()
                return triggers
            
            # Detect concentration risk
            counterparty_exposure = exposures_df.groupby('counterparty_id')['notional_amount'].sum()
            total_exposure = counterparty_exposure.sum()
            
            for counterparty, exposure in counterparty_exposure.items():
                concentration_ratio = exposure / total_exposure
                if concentration_ratio > 0.2:  # 20% concentration threshold
                    triggers.append(RiskTrigger(
                        entity_id=entity_id,
                        trigger_type="concentration_risk",
                        severity=RiskLevel.HIGH if concentration_ratio > 0.3 else RiskLevel.MEDIUM,
                        description=f"High concentration risk with {counterparty}: {concentration_ratio:.1%} of total exposure",
                        trigger_date=datetime.now(),
                        impact_amount=exposure
                    ))
            
            # Detect maturity concentration
            exposures_df['maturity_date'] = pd.to_datetime(exposures_df['maturity_date'])
            current_date = datetime.now()
            near_term_exposures = exposures_df[
                exposures_df['maturity_date'] <= current_date + timedelta(days=365)
            ]
            
            if not near_term_exposures.empty:
                near_term_amount = near_term_exposures['notional_amount'].sum()
                near_term_ratio = near_term_amount / total_exposure
                
                if near_term_ratio > 0.4:  # 40% maturing within 1 year
                    triggers.append(RiskTrigger(
                        entity_id=entity_id,
                        trigger_type="maturity_concentration",
                        severity=RiskLevel.MEDIUM,
                        description=f"High near-term maturity concentration: {near_term_ratio:.1%} of exposure matures within 1 year",
                        trigger_date=datetime.now(),
                        impact_amount=near_term_amount
                    ))
            
            # Detect negative market value positions
            negative_positions = exposures_df[exposures_df['market_value'] < 0]
            if not negative_positions.empty:
                total_negative = abs(negative_positions['market_value'].sum())
                triggers.append(RiskTrigger(
                    entity_id=entity_id,
                    trigger_type="negative_market_value",
                    severity=RiskLevel.HIGH,
                    description=f"Negative market value positions totaling ${total_negative:,.0f}",
                    trigger_date=datetime.now(),
                    impact_amount=total_negative
                ))
            
            conn.close()
            
            # Store triggers in database
            for trigger in triggers:
                self._store_risk_trigger(trigger)
            
            logger.info(f"Detected {len(triggers)} risk triggers for entity {entity_id}")
            return triggers
            
        except Exception as e:
            logger.error(f"Error detecting risk triggers for {entity_id}: {e}")
            return []
    
    def _store_risk_trigger(self, trigger: RiskTrigger) -> bool:
        """Store risk trigger in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO risk_triggers 
                (entity_id, trigger_type, severity, description, trigger_date, impact_amount, mitigation_actions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                trigger.entity_id,
                trigger.trigger_type,
                trigger.severity.value,
                trigger.description,
                trigger.trigger_date,
                trigger.impact_amount,
                json.dumps(trigger.mitigation_actions)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error storing risk trigger: {e}")
            return False
    
    def add_obligation(self, obligation: Obligation) -> bool:
        """
        Add an obligation to the system
        
        Args:
            obligation: Obligation object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO obligations 
                (entity_id, obligation_type, amount, due_date, counterparty_id, description, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                obligation.entity_id,
                obligation.obligation_type,
                obligation.amount,
                obligation.due_date,
                obligation.counterparty_id,
                obligation.description,
                obligation.status
            ))
            
            conn.commit()
            conn.close()
            
            self.obligations.append(obligation)
            logger.info(f"Obligation added for entity {obligation.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding obligation: {e}")
            return False
    
    def generate_risk_report(self, entity_id: str) -> str:
        """
        Generate comprehensive risk report for an entity
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Formatted risk report string
        """
        try:
            summary = self.get_entity_exposure_summary(entity_id)
            triggers = self.detect_risk_triggers(entity_id)
            
            if not summary:
                return f"No data found for entity {entity_id}"
            
            report = f"""
=== COMPREHENSIVE SWAP RISK ANALYSIS REPORT ===
Entity: {entity_id}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXPOSURE SUMMARY:
- Total Notional Exposure: ${summary['total_notional_exposure']:,.0f}
- Total Market Value: ${summary['total_market_value']:,.0f}
- Total Positions: {summary['total_positions']}
- Counterparties: {summary['counterparty_count']}

ASSET CLASS BREAKDOWN:
"""
            
            for asset_class in summary['exposure_by_asset_class']:
                report += f"- {asset_class['asset_class']}: ${asset_class['total_notional']:,.0f} notional, {asset_class['position_count']} positions\n"
            
            report += f"""
TOP COUNTERPARTIES:
"""
            for i, counterparty in enumerate(summary['top_counterparties'][:5], 1):
                report += f"{i}. {counterparty['counterparty_id']}: ${counterparty['total_notional']:,.0f} notional\n"
            
            report += f"""
OBLIGATIONS:
- Upcoming (30 days): ${summary['upcoming_obligations_30d']:,.0f}
- Total Outstanding: ${summary['total_obligations']:,.0f}

RISK TRIGGERS ({len(triggers)} detected):
"""
            
            for trigger in triggers:
                report += f"- {trigger.severity.value.upper()}: {trigger.description}\n"
                if trigger.impact_amount:
                    report += f"  Impact: ${trigger.impact_amount:,.0f}\n"
            
            if not triggers:
                report += "- No significant risk triggers detected\n"
            
            report += "\n=== END REPORT ===\n"
            
            logger.info(f"Generated risk report for entity {entity_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating risk report for {entity_id}: {e}")
            return f"Error generating report: {e}"


def create_sample_data():
    """Create sample data for testing"""
    explorer = SwapExplorer()
    
    # Register sample entities
    explorer.register_entity("ABC_CORP", EntityIdentifier(
        lei="ABC123456789",
        cik="0001234567",
        ticker="ABC",
        name="ABC Corporation",
        aliases=["ABC Corp", "ABC Inc"]
    ))
    
    explorer.register_entity("XYZ_BANK", EntityIdentifier(
        lei="XYZ987654321",
        cik="0007654321",
        ticker="XYZ",
        name="XYZ Bank",
        aliases=["XYZ Bank Corp", "XYZ Financial"]
    ))
    
    # Add sample swap exposures
    explorer.add_swap_exposure(SwapExposure(
        entity_id="ABC_CORP",
        counterparty_id="XYZ_BANK",
        asset_class=AssetClass.INTEREST_RATE,
        notional_amount=100000000,  # $100M
        market_value=2500000,  # $2.5M
        maturity_date=datetime.now() + timedelta(days=365),
        trade_date=datetime.now() - timedelta(days=30),
        data_source="CFTC",
        risk_metrics={"duration": 2.5, "dv01": 250000}
    ))
    
    explorer.add_swap_exposure(SwapExposure(
        entity_id="ABC_CORP",
        counterparty_id="XYZ_BANK",
        asset_class=AssetClass.CREDIT,
        notional_amount=50000000,  # $50M
        market_value=-1000000,  # -$1M
        maturity_date=datetime.now() + timedelta(days=730),
        trade_date=datetime.now() - timedelta(days=60),
        data_source="DTCC",
        risk_metrics={"spread_duration": 3.2, "credit_dv01": 160000}
    ))
    
    # Add sample obligations
    explorer.add_obligation(Obligation(
        entity_id="ABC_CORP",
        obligation_type="payment",
        amount=500000,  # $500K
        due_date=datetime.now() + timedelta(days=15),
        counterparty_id="XYZ_BANK",
        description="Quarterly interest payment"
    ))
    
    explorer.add_obligation(Obligation(
        entity_id="ABC_CORP",
        obligation_type="collateral",
        amount=2000000,  # $2M
        due_date=datetime.now() + timedelta(days=7),
        counterparty_id="XYZ_BANK",
        description="Initial margin posting"
    ))
    
    return explorer


if __name__ == "__main__":
    # Create sample data and generate report
    explorer = create_sample_data()
    
    # Generate risk report
    report = explorer.generate_risk_report("ABC_CORP")
    print(report)
