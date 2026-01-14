import pandas as pd
import glob
import os
from src.utils import setup_logger

logger = setup_logger()

def load_data(category, path):
    logger.info(f"Loading {category} data from {path}...")
    all_files = glob.glob(os.path.join(path, "*.csv"))
    
    if not all_files:
        logger.warning(f"No files found for {category}")
        return None
        
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            # Basic schema validation
            if 'state' not in df.columns:
                logger.warning(f"Skipping {filename}: Missing 'state' column")
                continue
            df_list.append(df)
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        logger.info(f"Loaded {len(combined_df)} rows for {category}")
        return combined_df
    else:
        return None

def clean_data(df, category):
    logger.info(f"Cleaning {category} data...")
    # Convert date
    try:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    except Exception as e:
        logger.warning(f"Date conversion error in {category}: {e}")
        # Fallback for mixed formats if any
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Drop rows with invalid dates
    df = df.dropna(subset=['date']).copy()

    # Fill NaNs in numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Sort by date
    df = df.sort_values(by='date')
    
    # Add some basic derived features
    df['YearMonth'] = df['date'].dt.to_period('M')
    
    return df
