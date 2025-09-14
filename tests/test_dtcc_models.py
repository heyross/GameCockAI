"""
Tests for DTCC data models.
"""
import unittest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path to allow imports from the main package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the models we want to test
from dtcc_models import (
    DTCCOrganization,
    DTCCInterestRateSwap,
    DTCCOptionTrade,
    DTCCEquityOption,
    DTCCOptionExercise,
    DTCCOptionPosition,
    DTCCOptionSettlement
)
from database import Base

class TestDTCCModels(unittest.TestCase):
    """Test cases for DTCC data models."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and session."""
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        
        # Create all tables
        Base.metadata.create_all(cls.engine)
    
    def setUp(self):
        """Start a new transaction for each test."""
        self.session = self.Session()
        self.session.begin_nested()
    
    def tearDown(self):
        """Roll back the transaction after each test."""
        self.session.rollback()
        self.session.close()
    
    def test_create_organization(self):
        """Test creating a DTCC organization."""
        # Use a unique LEI for this test
        lei = f"TESTORG{datetime.now(timezone.utc).timestamp()}"[:20]
        
        org = DTCCOrganization(
            lei=lei,
            name="Test Organization Inc.",
            duns_number="123456789",
            entity_type="CORPORATION",
            registration_status="ACTIVE"
        )
        self.session.add(org)
        self.session.commit()
        
        # Verify the organization was created
        result = self.session.query(DTCCOrganization).filter_by(lei=lei).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Test Organization Inc.")
    
    def test_create_interest_rate_swap(self):
        """Test creating an interest rate swap."""
        # Create organizations first with unique LEIs
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        org1 = DTCCOrganization(lei=f"BANKA{timestamp[:15]}", name="Bank A")
        org2 = DTCCOrganization(lei=f"BANKB{timestamp[:15]}", name="Bank B")
        self.session.add_all([org1, org2])
        self.session.commit()
        
        # Create the swap
        effective_date = datetime.now(timezone.utc)
        termination_date = effective_date + timedelta(days=365)
        
        swap = DTCCInterestRateSwap(
            trade_id="SWAP123456789",
            execution_timestamp=datetime.now(timezone.utc),
            effective_date=effective_date,
            termination_date=termination_date,
            notional_amount=1000000.00,
            notional_currency="USD",
            trade_status="ACTIVE",
            clearing_status="CLEARED",
            asset_class="RATES",
            product_type="SWAP",
            reporting_party_lei=org1.lei,
            other_party_lei=org2.lei,
            fixed_rate=2.50,
            floating_index="SOFR"
        )
        
        self.session.add(swap)
        self.session.commit()
        
        # Verify the swap was created
        result = self.session.query(DTCCInterestRateSwap).filter_by(trade_id="SWAP123456789").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.notional_amount, 1000000.00)
        self.assertEqual(result.other_party_lei, org2.lei)
    
    def test_create_equity_option(self):
        """Test creating an equity option."""
        # Create organizations with unique LEIs
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        org1 = DTCCOrganization(lei=f"HFUND{timestamp[:15]}", name="Hedge Fund A")
        org2 = DTCCOrganization(lei=f"MKTMR{timestamp[:15]}", name="Market Maker B")
        self.session.add_all([org1, org2])
        
        # Create the base option trade
        expiration = datetime.now(timezone.utc) + timedelta(days=30)
        
        option_trade = DTCCOptionTrade(
            trade_id="OPT987654321",
            execution_timestamp=datetime.now(timezone.utc),
            effective_date=datetime.now(timezone.utc),
            trade_status="ACTIVE",
            clearing_status="CLEARED",
            asset_class="EQUITY",
            product_type="OPTION",
            reporting_party_lei=org1.lei,
            other_party_lei=org2.lei,
            underlying_asset="AAPL",
            option_type="CALL",
            strike_price=150.00,
            strike_currency="USD",
            expiration_date=expiration,
            premium_amount=5.50,
            premium_currency="USD"
        )
        
        # Create the equity option
        equity_option = DTCCEquityOption(
            trade_id="OPT987654321",
            security_type="STOCK",
            security_description="Apple Inc. Common Stock"
        )
        
        # Set up the relationship
        option_trade.equity_option = equity_option
        
        self.session.add(option_trade)
        self.session.commit()
        
        # Verify the option was created
        result = self.session.query(DTCCEquityOption).filter_by(trade_id="OPT987654321").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.security_type, "STOCK")
        self.assertEqual(result.option_trade.underlying_asset, "AAPL")
        self.assertEqual(result.option_trade.strike_price, 150.00)
    
    def test_option_exercise(self):
        """Test creating an option exercise record."""
        # First create an option with unique organization LEIs
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        org1 = DTCCOrganization(lei=f"HFUND{timestamp[:10]}A", name="Hedge Fund A")
        org2 = DTCCOrganization(lei=f"MKTMR{timestamp[5:15]}B", name="Market Maker B")
        self.session.add_all([org1, org2])
        self.session.commit()  # Explicitly commit the organizations first
        
        now = datetime.now(timezone.utc)
        
        option = DTCCOptionTrade(
            trade_id=f"OPT{timestamp[-9:]}",
            execution_timestamp=now,
            effective_date=now,
            trade_status="EXERCISED",
            asset_class="EQUITY",
            product_type="OPTION",
            reporting_party_lei=org1.lei,
            other_party_lei=org2.lei,
            underlying_asset="MSFT",
            option_type="CALL",
            strike_price=300.00,
            strike_currency="USD",
            expiration_date=now + timedelta(days=10)
        )
        
        exercise = DTCCOptionExercise(
            trade_id=option.trade_id,
            exercise_id=f"EX{timestamp[-9:]}",
            exercise_date=now,
            exercise_type="EXERCISE",
            quantity=100,
            settlement_amount=30000.00,
            settlement_currency="USD",
            settlement_date=now + timedelta(days=2)
        )
        
        self.session.add_all([option, exercise])
        self.session.commit()
        
        # Verify the exercise was created and linked to the trade
        result = self.session.query(DTCCOptionExercise).filter_by(exercise_id=exercise.exercise_id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.trade_id, option.trade_id)
        self.assertEqual(result.settlement_amount, 30000.00)

if __name__ == "__main__":
    unittest.main()
