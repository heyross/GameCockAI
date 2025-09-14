import os
from dotenv import load_dotenv

load_dotenv()

# Base directories
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # GameCockAI root
SRC_DIR = os.path.dirname(os.path.abspath(__file__))  # src directory
DATA_DIR = os.path.join(ROOT_DIR, "data")
DOWNLOADS_DIR = os.path.join(ROOT_DIR, "Downloads")

# SEC EDGAR API Configuration
EDGAR_BASE_URL = "https://www.sec.gov/Archives/"
SEC_API_KEY = os.getenv("SEC_API_KEY")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "GameCockAI/1.0 (your-email@example.com)")

# SEC Data Directories (organized under Downloads/SEC/)
SEC_BASE_DIR = os.path.join(DOWNLOADS_DIR, "SEC")
FORMD_SOURCE_DIR = os.path.join(SEC_BASE_DIR, "SecFormD")
NCEN_SOURCE_DIR = os.path.join(SEC_BASE_DIR, "SecNcen")
NPORT_SOURCE_DIR = os.path.join(SEC_BASE_DIR, "SecNport")
THRTNF_SOURCE_DIR = os.path.join(SEC_BASE_DIR, "Sec13F")
NMFP_SOURCE_DIR = os.path.join(SEC_BASE_DIR, "SecNmfp")
SEC_8K_SOURCE_DIR = os.path.join(SEC_BASE_DIR, "processed", "8k", "raw")
SEC_10K_SOURCE_DIR = os.path.join(SEC_BASE_DIR, "processed", "10k", "raw")

# CFTC Data Directories (organized under Downloads/CFTC/)
CFTC_BASE_DIR = os.path.join(DOWNLOADS_DIR, "CFTC")
CREDIT_SOURCE_DIR = os.path.join(CFTC_BASE_DIR, "CREDITS")
EQUITY_SOURCE_DIR = os.path.join(CFTC_BASE_DIR, "EQUITY")
CFTC_EQUITY_SOURCE_DIR = os.path.join(CFTC_BASE_DIR, "CFTC_EQ")
CFTC_CREDIT_SOURCE_DIR = os.path.join(CFTC_BASE_DIR, "CFTC_CR")
CFTC_COMMODITIES_SOURCE_DIR = os.path.join(CFTC_BASE_DIR, "CFTC_CO")
CFTC_FOREX_SOURCE_DIR = os.path.join(DOWNLOADS_DIR, "FOREX")
CFTC_RATES_SOURCE_DIR = os.path.join(CFTC_BASE_DIR, "CFTC_IR")

# Additional Swap Data Directories
CFTC_SWAP_DEALER_DIR = os.path.join(CFTC_BASE_DIR, "CFTC_SWAP_DEALER")
CFTC_SWAP_EXECUTION_DIR = os.path.join(CFTC_BASE_DIR, "CFTC_SWAP_EXECUTION")
CFTC_SWAP_DATA_REPOSITORY_DIR = os.path.join(CFTC_BASE_DIR, "CFTC_SWAP_DATA_REPOSITORY")

# Other Directories
EDGAR_SOURCE_DIR = os.path.join(DOWNLOADS_DIR, "EDGAR")
EXCHANGE_SOURCE_DIR = os.path.join(DOWNLOADS_DIR, "EXCHANGE")
INSIDER_SOURCE_DIR = os.path.join(DOWNLOADS_DIR, "INSIDERS")

# FRED Data Directory
FRED_SOURCE_DIR = os.path.join(DOWNLOADS_DIR, "FRED")

# DTCC Data Directory
DTCC_SOURCE_DIR = os.path.join(DOWNLOADS_DIR, "DTCC")

# Cache directories
CACHE_DIR = os.path.join(ROOT_DIR, "cache")
EMBEDDING_CACHE_DIR = os.path.join(CACHE_DIR, "embeddings")
VECTOR_CACHE_DIR = os.path.join(CACHE_DIR, "vectors")

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

# Legacy paths for backward compatibility (will be deprecated)
# These point to the same locations but maintain old variable names
ROOT_DIR_LEGACY = "./"  # For root directory imports
