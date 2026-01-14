import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from src.config import FIGURES_DIR
from src.utils import indian_formatter

# Set visual style
sns.set_theme(style="whitegrid")

def aggregate_time_series(df, numeric_cols):
    """Aggregates data by date."""
    if not numeric_cols:
        return None
    daily_df = df.groupby('date')[numeric_cols].sum().reset_index()
    return daily_df

def aggregate_state_stats(df, numeric_cols):
    """Aggregates data by state."""
    if not numeric_cols:
        return None
    state_df = df.groupby('state')[numeric_cols].sum().reset_index()
    # Calculate total per state
    state_df['Total'] = state_df[numeric_cols].sum(axis=1)
    return state_df

def analyze_dataset(datasets):
    print("Starting Comprehensive Analysis...")
    
    for category, df in datasets.items():
        if df is None:
            continue
            
        print(f"Analyzing {category}...")
        
        # Identify numeric columns for aggregation (exclude pincode)
        numeric_cols = [c for c in df.select_dtypes(include=['number']).columns if 'pincode' not in c and 'Year' not in c]
        
        # 1. Temporal Analysis
        daily_agg = aggregate_time_series(df, numeric_cols)
        daily_agg['Total_Activity'] = daily_agg[numeric_cols].sum(axis=1)
        
        plt.figure(figsize=(14, 6))
        plt.plot(daily_agg['date'], daily_agg['Total_Activity'], label=f'{category} Daily Volume')
        
        # Moving Average (7-day and 30-day)
        daily_agg['MA_7'] = daily_agg['Total_Activity'].rolling(window=7).mean()
        daily_agg['MA_30'] = daily_agg['Total_Activity'].rolling(window=30).mean()
        
        plt.plot(daily_agg['date'], daily_agg['MA_7'], label='7-Day Mov Avg', alpha=0.8)
        plt.plot(daily_agg['date'], daily_agg['MA_30'], label='30-Day Mov Avg', linestyle='--', color='black')
        
        plt.title(f'{category.capitalize()} - Time Series Trend')
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.gca().yaxis.set_major_formatter(indian_formatter)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f'{category}_trend.png'))
        plt.close()
        
        # 2. Regional Analysis (Top 10 States)
        state_agg = aggregate_state_stats(df, numeric_cols)
        top_states = state_agg.sort_values('Total', ascending=False).head(10)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=top_states, x='Total', y='state', palette='viridis')
        plt.title(f'Top 10 States by {category.capitalize()} Volume')
        plt.xlabel('Total Volume')
        plt.gca().xaxis.set_major_formatter(indian_formatter)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f'{category}_top_states.png'))
        plt.close()
        
    print("Basic EDA Completed.")

def perform_advanced_analysis(datasets):
    print("Performing Advanced ML Analysis...")
    
    # 1. Clustering States (Pattern Recognition)
    if 'enrolment' in datasets and 'biometric' in datasets:
        enrol = datasets['enrolment'].groupby('state').sum(numeric_only=True).reset_index()
        bio = datasets['biometric'].groupby('state').sum(numeric_only=True).reset_index()
        
        enrol_cols = [c for c in enrol.columns if c not in ['state', 'pincode', 'YearMonth']]
        bio_cols = [c for c in bio.columns if c not in ['state', 'pincode', 'YearMonth']]
        
        enrol['Total_Enrolment'] = enrol[enrol_cols].sum(axis=1)
        bio['Total_Biometric'] = bio[bio_cols].sum(axis=1)
        
        merged = pd.merge(enrol[['state', 'Total_Enrolment']], bio[['state', 'Total_Biometric']], on='state')
        
        scaler = StandardScaler()
        X = merged[['Total_Enrolment', 'Total_Biometric']]
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        merged['Cluster'] = kmeans.fit_predict(X_scaled)
        
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=merged, x='Total_Enrolment', y='Total_Biometric', hue='Cluster', palette='deep', s=100)
        
        for i in range(merged.shape[0]):
             if merged.iloc[i]['Total_Enrolment'] > merged['Total_Enrolment'].quantile(0.9) or \
                merged.iloc[i]['Total_Biometric'] > merged['Total_Biometric'].quantile(0.9):
                plt.text(merged.iloc[i]['Total_Enrolment'], merged.iloc[i]['Total_Biometric'], 
                         merged.iloc[i]['state'], fontsize=9)
                         
        plt.title('State Clustering: Enrolment vs Biometric Updates')
        plt.xlabel('Total Enrolment')
        plt.ylabel('Total Biometric Updates')
        plt.gca().xaxis.set_major_formatter(indian_formatter)
        plt.gca().yaxis.set_major_formatter(indian_formatter)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, 'clustering_states.png'))
        plt.close()
        
    # 2. Anomaly Detection
    for category in ['enrolment', 'biometric']:
        if category in datasets:
            df = datasets[category]
            numeric_cols = [c for c in df.select_dtypes(include=['number']).columns if 'pincode' not in c and 'Year' not in c]
            daily = df.groupby('date')[numeric_cols].sum().reset_index()
            daily['Total'] = daily[numeric_cols].sum(axis=1)
            
            iso = IsolationForest(contamination=0.05, random_state=42)
            daily['Anomaly'] = iso.fit_predict(daily[['Total']])
            
            anomalies = daily[daily['Anomaly'] == -1]
            
            plt.figure(figsize=(12, 6))
            plt.plot(daily['date'], daily['Total'], label='Daily Trend', color='blue', alpha=0.6)
            plt.scatter(anomalies['date'], anomalies['Total'], color='red', label='Anomaly', zorder=5)
            plt.title(f'Anomaly Detection in {category.capitalize()}')
            plt.xlabel('Date')
            plt.ylabel('Volume')
            plt.gca().yaxis.set_major_formatter(indian_formatter)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(FIGURES_DIR, f'{category}_anomalies.png'))
            plt.close()

    # 3. Predictive Modeling
    if 'enrolment' in datasets:
        df = datasets['enrolment']
        numeric_cols = [c for c in df.select_dtypes(include=['number']).columns if 'pincode' not in c and 'Year' not in c]
        daily = df.groupby('date')[numeric_cols].sum().reset_index()
        daily['Total'] = daily[numeric_cols].sum(axis=1)
        
        daily['Date_Num'] = daily['date'].map(pd.Timestamp.toordinal)
        X = daily[['Date_Num']]
        y = daily['Total']
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_date = daily['date'].max()
        future_dates = [last_date + pd.Timedelta(days=x) for x in range(1, 31)]
        future_dates_num = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        predictions = model.predict(future_dates_num)
        
        plt.figure(figsize=(12, 6))
        plt.plot(daily['date'], daily['Total'], label='Historical Data')
        plt.plot(future_dates, predictions, label='30-Day Forecast', linestyle='--', color='green')
        plt.title('Enrolment Volume Prediction')
        plt.xlabel('Date')
        plt.ylabel('Projected Volume')
        plt.gca().yaxis.set_major_formatter(indian_formatter)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, 'enrolment_forecast.png'))
        plt.close()
