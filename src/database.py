from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

DATABASE_URL = "sqlite:///./gamecock.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, Float

class CFTCSwap(Base):
    __tablename__ = 'cftc_swap_data'

    id = Column(Integer, primary_key=True, index=True)
    dissemination_id = Column(String, index=True)
    original_dissemination_id = Column(String)
    action = Column(String)
    clearing_indicator = Column(String)
    collateralization_indicator = Column(String)
    end_user_exception_indicator = Column(String)
    off_market_price_indicator = Column(String)
    execution_timestamp = Column(DateTime)
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    # Add more columns as needed based on the actual data
    # For example:
    asset_class = Column(String)
    notional_amount = Column(Float)
    currency = Column(String)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_db_stats():
    """Returns statistics about the database."""
    db = SessionLocal()
    try:
        cftc_count = db.query(CFTCSwap).count()
        # Add counts for other tables as they are created
        return {"cftc_swap_data": cftc_count}
    finally:
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
