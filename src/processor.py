import glob
import logging
import os
import pandas as pd
from zipfile import ZipFile
# Import from the REAL database module with all tables (GameCockAI/database.py)
try:
    from database import SessionLocal, CFTCSwap
except ImportError:
    # Fallback for when running from root directory
    from GameCockAI.database import SessionLocal, CFTCSwap

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_zip_files(source_dir, target_companies, search_term=None):
    """Processes all zip files in a directory, optionally filtering by a search term."""
    master_df = pd.DataFrame()
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))

    for zip_file in zip_files:
        try:
            with ZipFile(zip_file, 'r') as zip_ref:
                for csv_filename in zip_ref.namelist():
                    if csv_filename.endswith('.csv'):
                        with zip_ref.open(csv_filename) as csv_file:
                            df = pd.read_csv(csv_file, low_memory=False)

                            # Filter by target companies if a list is provided
                            if target_companies:
                                target_ciks = {str(c['cik_str']) for c in target_companies}
                                # Find a CIK column in the dataframe (case-insensitive)
                                cik_col = next((col for col in df.columns if 'cik' in col.lower()), None)
                                
                                if cik_col:
                                    # Ensure the CIK column is string type for comparison
                                    df[cik_col] = df[cik_col].astype(str).str.zfill(10)
                                    df = df[df[cik_col].isin(target_ciks)]
                                else:
                                    # If no CIK column, the data might not be company-specific. Process all of it.
                                    logging.warning(f"No CIK column found in {csv_filename}, processing all data.")

                            if search_term:
                                # Simple search across all columns
                                mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
                                df = df[mask]
                            master_df = pd.concat([master_df, df], ignore_index=True)
        except Exception as e:
            logging.error(f"Error processing {zip_file}: {e}")

    return master_df

def load_cftc_data_to_db(df):
    """Cleans and loads a DataFrame into the CFTC Swap data table."""
    db = SessionLocal()

    # Get model columns
    model_columns = {c.name for c in CFTCSwap.__table__.columns}

    # Define potential date and numeric columns
    potential_date_cols = ['execution_timestamp', 'effective_date', 'expiration_date']
    potential_numeric_cols = ['notional_amount']

    # Find which of these columns actually exist in the DataFrame
    existing_date_cols = [col for col in potential_date_cols if col in df.columns]
    existing_numeric_cols = [col for col in potential_numeric_cols if col in df.columns]

    # Clean and convert data types for existing columns
    for col in existing_date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    for col in existing_numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where essential date/numeric conversions failed
    cols_to_check = existing_date_cols + existing_numeric_cols
    if cols_to_check:
        df.dropna(subset=cols_to_check, inplace=True)

    records_to_add = []
    for _, row in df.iterrows():
        # Filter row data to only include columns that exist in the model
        record_data = {k: v for k, v in row.to_dict().items() if k in model_columns}
        records_to_add.append(CFTCSwap(**record_data))

    try:
        db.bulk_save_objects(records_to_add)
        db.commit()
        logging.info(f"Successfully loaded {len(records_to_add)} records into the database.")
    except Exception as e:
        logging.error(f"Error loading data to database: {e}")
        db.rollback()
    finally:
        db.close()
