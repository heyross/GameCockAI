import os
from dotenv import load_dotenv

load_dotenv()

# Base directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

# SEC EDGAR API Configuration
EDGAR_BASE_URL = "https://www.sec.gov/Archives/"
SEC_API_KEY = os.getenv("SEC_API_KEY")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "GameCockAI/1.0 (your-email@example.com)")

# Data source directories
FORMD_SOURCE_DIR = os.path.join(ROOT_DIR, "SecFormD")
NCEN_SOURCE_DIR = os.path.join(ROOT_DIR, "SecNcen")
NPORT_SOURCE_DIR = os.path.join(ROOT_DIR, "SecNport")
THRTNF_SOURCE_DIR = os.path.join(ROOT_DIR, "Sec13F")
NMFP_SOURCE_DIR = os.path.join(ROOT_DIR, "SecNmfp")
CREDIT_SOURCE_DIR = os.path.join(ROOT_DIR, "CREDITS")
EQUITY_SOURCE_DIR = os.path.join(ROOT_DIR, "EQUITY")
CFTC_EQUITY_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_EQ")
CFTC_CREDIT_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_CR")
CFTC_COMMODITIES_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_CO")
CFTC_FOREX_SOURCE_DIR = os.path.join(ROOT_DIR, "FOREX")
CFTC_RATES_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_IR")
EDGAR_SOURCE_DIR = os.path.join(ROOT_DIR, "EDGAR")
EXCHANGE_SOURCE_DIR = os.path.join(ROOT_DIR, "EXCHANGE")
INSIDER_SOURCE_DIR = os.path.join(ROOT_DIR, "INSIDERS")
SEC_8K_SOURCE_DIR = os.path.join(DATA_DIR, 'sec', '8k', 'raw') 

