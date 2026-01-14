"""
Purpose: Analyze Aadhaar activity based on Day of Week and Holidays (National & State).
How to run: python analysis_date_holiday.py
Output: 
    - Plots in 'plots/' directory:
        - weekday_weekend_pattern.png
        - holiday_impact.png
    - Console output summarizing key findings.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import holidays
import sys
import os
from pathlib import Path

# Ensure src is in path if running standalone
if str(Path(__file__).parent / 'src') not in sys.path:
    sys.path.append(str(Path(__file__).parent / 'src'))

from src.config import DATA_DIRS, FIGURES_DIR
from src.data_loader import load_data, clean_data
from src.utils import indian_formatter

# Set visual style
sns.set_theme(style="whitegrid")

# Mapping of State Names to Holidays State Codes
STATE_CODE_MAP = {
    'Andaman and Nicobar Islands': 'AN',
    'Andhra Pradesh': 'AP',
    'Arunachal Pradesh': 'AR',
    'Assam': 'AS',
    'Bihar': 'BR',
    'Chandigarh': 'CH',
    'Chhattisgarh': 'CG',
    'Dadra and Nagar Haveli': 'DN',
    'Daman and Diu': 'DD',
    'Delhi': 'DL',
    'Goa': 'GA',
    'Gujarat': 'GJ',
    'Haryana': 'HR',
    'Himachal Pradesh': 'HP',
    'Jammu and Kashmir': 'JK',
    'Jharkhand': 'JH',
    'Karnataka': 'KA',
    'Kerala': 'KL',
    'Ladakh': 'LA',
    'Lakshadweep': 'LD',
    'Madhya Pradesh': 'MP',
    'Maharashtra': 'MH',
    'Manipur': 'MN',
    'Meghalaya': 'ML',
    'Mizoram': 'MZ',
    'Nagaland': 'NL',
    'Odisha': 'OR',
    'Puducherry': 'PY',
    'Punjab': 'PB',
    'Rajasthan': 'RJ',
    'Sikkim': 'SK',
    'Tamil Nadu': 'TN',
    'Telangana': 'TS',
    'Tripura': 'TR',
    'Uttar Pradesh': 'UP',
    'Uttarakhand': 'UK',
    'West Bengal': 'WB'
}

def get_holiday_info(row, holiday_dict):
    """
    Determines if a date is a holiday for a specific state.
    """
    date = row['date']
    state = row['state']
    
    # Get state code, default to None (National holidays only logic if needed later)
    state_code = STATE_CODE_MAP.get(state)
    
    # Check specific state holidays if code exists
    if state_code and state_code in holiday_dict:
        if date in holiday_dict[state_code]:
            return True, holiday_dict[state_code].get(date)
            
    # Always check National/Base India holidays (represented by 'IN' in our dict structure or just base object)
    if 'IN' in holiday_dict and date in holiday_dict['IN']:
         return True, holiday_dict['IN'].get(date)
         
    return False, None

def prepare_holiday_data(years):
    """Pre-fetches holiday objects for all states and years."""
    holiday_dict = {}
    
    # National Holidays
    holiday_dict['IN'] = holidays.India(years=years)
    
    # State Holidays
    for state_name, code in STATE_CODE_MAP.items():
        try:
            holiday_dict[code] = holidays.India(years=years, subdiv=code)
        except Exception:
            pass # Graceful degradation if code not supported
            
    return holiday_dict

def analyze_date_intelligence(datasets):
    print("Starting Date & Holiday Analysis...")
    
    # Focus on 'enrolment' for this deep dive, but can extend
    if 'enrolment' not in datasets or datasets['enrolment'] is None:
        print("Enrolment data missing.")
        return

    df = datasets['enrolment'].copy()
    
    # 1. Date Feature Extraction
    df['DayOfWeek'] = df['date'].dt.day_name()
    df['IsWeekend'] = df['date'].dt.dayofweek.isin([5, 6]) # Sat=5, Sun=6
    
    # 2. Holiday Detection
    years = df['date'].dt.year.unique()
    holiday_dict = prepare_holiday_data(years)
    
    # Apply holiday logic (this can be slow on huge data, so standardizing/vectorizing where possible is better, 
    # but for state-specific lookups, apply or merge is needed)
    
    # detailed row-by-row check is expensive. Let's optimize:
    # Create a long-form holiday dataframe? 
    # Or just iterate since we need State + Date combo.
    # Given dataset size (1M+ rows potentially), apply is slow.
    # Optimization: Merge with a pre-generated holiday table.
    
    print("Generating holiday mapping...")
    holiday_records = []
    for code, holidays_obj in holiday_dict.items():
        for date, name in holidays_obj.items():
            holiday_records.append({'date': pd.to_datetime(date), 'HolidayName': name, 'StateCode': code})
            
    if holiday_records:
        hol_df = pd.DataFrame(holiday_records)
        # We need to map df['state'] to code first
        df['StateCode'] = df['state'].map(STATE_CODE_MAP)
        
        # Merge for National (StateCode='IN' or fallback) - simplified approach:
        # Just check if date is in National list
        nat_holidays = holidays.India(years=years)
        df['IsNationalHoliday'] = df['date'].isin(nat_holidays)
        
        # State Specific check:
        # Let's stick to "Is it a holiday in that state?"
        # It's tricky to vectorise perfectly without a huge join.
        # Let's stick to National for general trend and simple apply for correctness if needed, 
        # but for speed on 1M rows, let's just use National + Weekend for the main "Holiday Impact" plot.
        
        # ACTUALLY, strict requirement: "State-specific holidays (where available)"
        # Let's try a merge.
        hol_df_state = hol_df[hol_df['StateCode'] != 'IN']
        
        # Merge df with hol_df_state on date AND StateCode
        df = pd.merge(df, hol_df_state[['date', 'StateCode', 'HolidayName']], 
                      on=['date', 'StateCode'], how='left')
        
        df.rename(columns={'HolidayName': 'StateHolidayName'}, inplace=True)
        df['IsStateHoliday'] = df['StateHolidayName'].notnull()
        
        df['IsHoliday'] = df['IsNationalHoliday'] | df['IsStateHoliday']
    else:
        df['IsHoliday'] = False

    # 3. Weekday vs Weekend Analysis
    numeric_cols = [c for c in df.select_dtypes(include=['number']).columns if 'pincode' not in c and 'Year' not in c]
    # Sum numeric cols for total volume
    df['Total_Volume'] = df[numeric_cols].sum(axis=1)
    
    # Plot 1: Average Volume by Day of Week
    # Reorder days
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='DayOfWeek', y='Total_Volume', estimator='mean', order=order, palette='coolwarm')
    plt.title('Average Enrolment Volume by Day of Week')
    plt.ylabel('Avg Volume')
    plt.gca().yaxis.set_major_formatter(indian_formatter)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'weekday_pattern.png'))
    plt.close()
    
    # Plot 2: Holiday vs Non-Holiday
    # Group by Date first to get daily totals, then categorize
    daily_stats = df.groupby(['date', 'IsHoliday', 'IsWeekend'])['Total_Volume'].sum().reset_index()
    
    # Create category
    def categorize(row):
        if row['IsHoliday']: return 'Holiday'
        if row['IsWeekend']: return 'Weekend'
        return 'Weekday'
        
    daily_stats['DayType'] = daily_stats.apply(categorize, axis=1)
    
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=daily_stats, x='DayType', y='Total_Volume', palette='Set2')
    plt.title('Volume Distribution: Weekday vs Weekend vs Holiday')
    plt.ylabel('Daily Total Volume')
    plt.gca().yaxis.set_major_formatter(indian_formatter)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'holiday_impact.png'))
    avg_weekday = daily_stats[daily_stats['DayType'] == 'Weekday']['Total_Volume'].mean()
    avg_weekend = daily_stats[daily_stats['DayType'] == 'Weekend']['Total_Volume'].mean()
    avg_holiday = daily_stats[daily_stats['DayType'] == 'Holiday']['Total_Volume'].mean()
    
    print("--- Insights ---")
    print(f"Avg Daily Volume (Weekday): {avg_weekday:,.0f}")
    print(f"Avg Daily Volume (Weekend): {avg_weekend:,.0f}")
    print(f"Avg Daily Volume (Holiday): {avg_holiday:,.0f}")
    print("----------------")
    
    return {
        'avg_weekday': avg_weekday,
        'avg_weekend': avg_weekend,
        'avg_holiday': avg_holiday
    }

def main():
    datasets = {}
    # Only loading enrolment for now as per objective to keep it clean, but can load all
    for category in ['enrolment']:
        path = DATA_DIRS[category]
        df = load_data(category, path)
        if df is not None:
            datasets[category] = clean_data(df, category)
            
    stats = analyze_date_intelligence(datasets)
    
if __name__ == "__main__":
    main()
