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

# CFTC Data Directories
CREDIT_SOURCE_DIR = os.path.join(ROOT_DIR, "CREDITS")
EQUITY_SOURCE_DIR = os.path.join(ROOT_DIR, "EQUITY")
CFTC_EQUITY_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_EQ")
CFTC_CREDIT_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_CR")
CFTC_COMMODITIES_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_CO")
CFTC_FOREX_SOURCE_DIR = os.path.join(ROOT_DIR, "FOREX")
CFTC_RATES_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_IR")

# Additional Swap Data Directories
CFTC_SWAP_DEALER_DIR = os.path.join(ROOT_DIR, "CFTC_SWAP_DEALER")
CFTC_SWAP_EXECUTION_DIR = os.path.join(ROOT_DIR, "CFTC_SWAP_EXECUTION")
CFTC_SWAP_DATA_REPOSITORY_DIR = os.path.join(ROOT_DIR, "CFTC_SWAP_DATA_REPOSITORY")

# Other Directories
EDGAR_SOURCE_DIR = os.path.join(ROOT_DIR, "EDGAR")
EXCHANGE_SOURCE_DIR = os.path.join(ROOT_DIR, "EXCHANGE")
INSIDER_SOURCE_DIR = os.path.join(ROOT_DIR, "INSIDERS")
SEC_8K_SOURCE_DIR = os.path.join(DATA_DIR, 'sec', '8k', 'raw')

# CFTC API Base URLs
CFTC_BASE_URL = "https://www.cftc.gov/api/v2/"

# Swap Data Repository (SDR) Data
CFTC_SWAP_DATA_URL = f"{CFTC_BASE_URL}datatables/sdr/transactions"

# Swap Dealer Registration Data
CFTC_SWAP_DEALER_URL = "https://sirt.cftc.gov/sirt/sirt.aspx?Topic=SwapDealersandMajorSwapParticipants"

# Swap Execution Facilities
CFTC_SWAP_EXECUTION_URL = "https://www.cftc.gov/IndustryOversight/TradingOrganizations/SEF/sef_listing"

# Swap Data Repositories
CFTC_SWAP_DATA_REPOSITORY_URL = "https://www.cftc.gov/IndustryOversight/DataRepositories/index.htm"

