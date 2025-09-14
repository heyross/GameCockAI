import requests
import json
import pandas as pd

# URL for the SEC's CIK lookup data
CIK_LOOKUP_URL = "https://www.sec.gov/files/company_tickers.json"

def get_company_map():
    """Downloads and processes the SEC's company ticker to CIK mapping."""
    headers = {'User-Agent': 'Gamecock/1.0'}
    try:
        response = requests.get(CIK_LOOKUP_URL, headers=headers)
        response.raise_for_status()
        # The data is a JSON object where each entry is a dictionary of company info
        # The keys are 'cik_str', 'ticker', and 'title'
        company_data = response.json()
        # Convert to a DataFrame for easier searching
        df = pd.DataFrame.from_records(company_data)
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
    
    search_term = search_term.lower()
    # Search in both ticker and title columns
    results = df[(df['ticker'].str.lower() == search_term) | (df['title'].str.lower().str.contains(search_term, na=False))]
    return results.to_dict('records')

