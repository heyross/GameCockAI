import glob
import logging
import os
import pandas as pd
from zipfile import ZipFile
from database import SessionLocal, CFTCSwap

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_zip_files(source_dir, target_companies, search_term=None):
    """Processes all zip files in a directory, optionally filtering by a search term."""
    master_df = pd.DataFrame()
    zip_files = sorted(glob.glob(os.path.join(source_dir, '*.zip')))

    for zip_file in zip_files:
        try:
            with ZipFile(zip_file, 'r') as zip_ref:
                for csv_filename in zip_ref.namelist():
                    if not csv_filename.endswith('.csv'):
                        continue

                    with zip_ref.open(csv_filename) as csv_file:
                        df = pd.read_csv(csv_file, low_memory=False)

                        # Filter by target companies if a list is provided and a CIK column exists
                        if target_companies:
                            target_ciks = {str(c['cik_str']) for c in target_companies}
                            cik_col = next((col for col in df.columns if 'cik' in col.lower()), None)

                            if cik_col:
                                df[cik_col] = df[cik_col].astype(str).str.zfill(10)
                                df = df[df[cik_col].isin(target_ciks)]
                                # If filtering results in an empty DataFrame, skip to the next file
                                if df.empty:
                                    continue
                            else:
                                # If no CIK column, process the whole file but warn the user
                                logging.warning(f"No CIK column in {csv_filename}, processing all data.")

                        if search_term:
                            mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
                            df = df[mask]
                        
                        if not df.empty:
                            master_df = pd.concat([master_df, df], ignore_index=True)

        except Exception as e:
            logging.error(f"Error processing {zip_file}: {e}")

    return master_df

def sanitize_column_names(df):
    """Converts DataFrame column names to a database-friendly format."""
    sanitized_columns = {}
    for col in df.columns:
        new_col = col.lower().replace(' ', '_').replace('-', '_').replace('/', '_')
        # Remove any trailing characters that are not alphanumeric
        new_col = ''.join(e for e in new_col if e.isalnum() or e == '_')
        sanitized_columns[col] = new_col
    df.rename(columns=sanitized_columns, inplace=True)
    return df

def load_cftc_data_to_db(df):
    """Cleans and loads a DataFrame into the CFTC Swap data table."""
    db = SessionLocal()

    # Sanitize column names to match the database schema
    df = sanitize_column_names(df)

    # Get model columns from the CFTCSwap table
    model_columns = {c.name for c in CFTCSwap.__table__.columns}

    # Define all potential date and numeric columns based on the new schema
    potential_date_cols = [
        'event_timestamp', 'execution_timestamp', 'effective_date', 'expiration_date',
        'maturity_date_of_the_underlier', 'effective_date_of_the_notional_amount_leg_1',
        'effective_date_of_the_notional_amount_leg_2', 'end_date_of_the_notional_amount_leg_1',
        'end_date_of_the_notional_amount_leg_2', 'first_exercise_date'
    ]
    potential_numeric_cols = [
        'notional_amount_leg_1', 'notional_amount_leg_2', 'notional_quantity_leg_1',
        'notional_quantity_leg_2', 'total_notional_quantity_leg_1', 'total_notional_quantity_leg_2',
        'quantity_frequency_multiplier_leg_1', 'quantity_frequency_multiplier_leg_2',
        'notional_amount_in_effect_on_associated_effective_date_leg_1',
        'notional_amount_in_effect_on_associated_effective_date_leg_2', 'call_amount_leg_1',
        'call_amount_leg_2', 'put_amount_leg_1', 'put_amount_leg_2', 'exchange_rate',
        'fixed_rate_leg_1', 'fixed_rate_leg_2', 'option_premium_amount', 'price',
        'spread_leg_1', 'spread_leg_2', 'strike_price',
        'floating_rate_reset_frequency_period_multiplier_leg_1',
        'floating_rate_reset_frequency_period_multiplier_leg_2', 'other_payment_amount',
        'fixed_rate_payment_frequency_period_multiplier_leg_1',
        'floating_rate_payment_frequency_period_multiplier_leg_1',
        'fixed_rate_payment_frequency_period_multiplier_leg_2',
        'floating_rate_payment_frequency_period_multiplier_leg_2', 'index_factor',
        'package_transaction_price', 'package_transaction_spread'
    ]

    # Convert data types for existing columns
    for col in potential_date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    for col in potential_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where essential conversions failed (optional, but good practice)
    # df.dropna(subset=existing_date_cols + existing_numeric_cols, inplace=True)

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
