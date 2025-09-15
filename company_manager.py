import requests
import json
import pandas as pd
from config import SEC_USER_AGENT

# URL for the SEC's CIK lookup data
CIK_LOOKUP_URL = "https://www.sec.gov/files/company_tickers.json"

def get_company_map():
    """Downloads and processes the SEC's company ticker to CIK mapping."""
    headers = {'User-Agent': SEC_USER_AGENT}
    try:
        response = requests.get(CIK_LOOKUP_URL, headers=headers)
        response.raise_for_status()
        # The data is a JSON object where each entry is a dictionary of company info
        # The keys are 'cik_str', 'ticker', and 'title'
        company_data = response.json()
        # The data is a dictionary of dictionaries, so we take the values
        # The data is a dictionary of dictionaries; we need the values.
        df = pd.DataFrame.from_records(list(company_data.values()))
        df['cik_str'] = df['cik_str'].astype(str).str.zfill(10) # Pad CIKs to 10 digits
        return df
    except requests.RequestException as e:
        print(f"Error downloading company map: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from company map.")
        return None

def find_company(df, search_term):
    """Searches the company map DataFrame for a given ticker or company name."""
    if df is None:
        return []
    
    # Handle None or empty search terms
    if search_term is None or not search_term:
        return []
    
    # Strip whitespace and convert to lowercase
    search_term_clean = str(search_term).strip().lower()
    if not search_term_clean:
        return []
    
    # Search in ticker, title, and CIK columns
    results = df[
        (df['ticker'].str.lower() == search_term_clean) | 
        (df['title'].str.lower().str.contains(search_term_clean, na=False)) | 
        (df['cik_str'] == search_term_clean.zfill(10))
    ]
    return results.to_dict('records')

