import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np
from src.config import FIGURES_DIR, REPORTS_DIR
from src.utils import setup_logger, indian_formatter
from src.analysis_date_holiday import STATE_CODE_MAP

logger = setup_logger("DayWiseAnalysis")

def maximize_constrast_palette():
    """Returns a color palette suitable for heatmaps with outliers."""
    return sns.diverging_palette(220, 20, as_cmap=True)

def ensure_day_order(df, day_col='day_name'):
    """Ensures Monday-Sunday ordering for visualizations."""
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df[day_col] = pd.Categorical(df[day_col], categories=days_order, ordered=True)
    return df

def generate_server_load_insights(state_day_matrix, category):
    """
    Generates operational insights focusing on Server Load and Capacity Planning.
    Calculates Peak-to-Mean Ratio (PMR) to identify bursty states.
    """
    logger.info(f"Generating Server Load Insights for {category}...")
    
    insights = []
    insights.append(f"### {category.capitalize()} - Server Load Optimization Insights\n")
    
    # 1. Peak Day Identification (Global)
    global_day_sum = state_day_matrix.sum(axis=0)
    peak_day = global_day_sum.idxmax()
    min_day = global_day_sum.idxmin()
    peak_vol = global_day_sum.max()
    min_vol = global_day_sum.min()
    
    load_imbalance = (peak_vol - min_vol) / peak_vol * 100
    
    insights.append(f"**Global Load Imbalance**: The system processes **{load_imbalance:.1f}%** less traffic on {min_day} compared to {peak_day}.")
    insights.append(f"- **Recommendation**: Shift batch processing jobs (e.g., deduplication, mis-match reports) to **{min_day}s** to utilize idle compute capacity.\n")

    # 2. State-Wise Bursty Load Analysis (PMR)
    # PMR = Peak Daily Volume / Average Daily Volume
    # High PMR (> 2.0) means the state slams the server on one day and is quiet on others.
    pmr_scores = {}
    for state in state_day_matrix.index:
        row = state_day_matrix.loc[state]
        if row.mean() > 0:
            pmr = row.max() / row.mean()
            pmr_scores[state] = pmr
            
    # Top 5 Bursty States
    bursty_states = sorted(pmr_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
    insights.append(f"#### Top 5 'Bursty' States (High Peak-to-Mean Ratio)")
    insights.append("These states generate sudden spikes in server load, risking timeouts.")
    insights.append(f"#### Top 5 'Bursty' States (High Peak-to-Mean Ratio)")
    insights.append("These states generate sudden spikes in server load, risking timeouts.")
    
    for state, score in bursty_states:
        rec = "Queue Throttling" if score > 2.5 else "Standard Balancing"
        insights.append(f"- **{state}**: {score:.2f}x PMR ({rec})")
        
    insights.append("\n_Note: A PMR of 2.0x means peak load is double the average load._\n")
    
    return "\n".join(insights)

def plot_full_state_heatmap(df, category):
    """
    Generates a heatmap of Volume for All States x Days.
    """
    output_path = os.path.join(FIGURES_DIR, 'daywise')
    os.makedirs(output_path, exist_ok=True)
    
    # pivot: index=state, col=day
    pivot = df.pivot_table(index='state', columns='day_name', values='Total', aggfunc='sum', fill_value=0)
    
    # Sort states by total volume so the chart is readable (High volume at top)
    pivot['Total_Row'] = pivot.sum(axis=1)
    pivot = pivot.sort_values('Total_Row', ascending=False)
    pivot = pivot.drop(columns=['Total_Row'])
    
    # Dynamic Height: 0.4 inches per state. Min 10, Max 50.
    n_states = len(pivot)
    height = max(10, n_states * 0.45)
    
    plt.figure(figsize=(12, height))
    
    # Use Log scale for color if disparity is huge? 
    # Let's stick to robust scaler or just standard heatmap but with robust=True equivalent?
    # Actually, standard heatmap is fine, but let's use a clear map.
    sns.heatmap(pivot, cmap='YlGnBu', annot=True, fmt='.0f', linewidths=.5, cbar_kws={'label': 'Volume'})
    
    plt.title(f'State-Wise {category.capitalize()} Load Heatmap (Monday-Sunday)', fontsize=16)
    plt.ylabel('State / UT')
    plt.xlabel('Day of Week')
    plt.tight_layout()
    
    save_file = os.path.join(output_path, f'{category}_state_heatmap_FULL.png')
    plt.savefig(save_file)
    plt.close()
    logger.info(f"Saved full heatmap to {save_file}")
    
    return pivot

def analyze_daywise(datasets):
    logger.info("Starting Day-Wise Analysis...")
    
    report_content = []
    
    for category, df in datasets.items():
        if df is None: 
            continue
            
        logger.info(f"Processing day-wise stats for {category}...")
        
        # Ensure date validity
        df = df[df['date'].notna()].copy()
        
        # --- DATA CLEANING: Filter Invalid States (Cities appearing as States) ---
        # The user reported cities/districts appearing in the 'state' column.
        # We strict filter using the official STATE_CODE_MAP keys.
        
        initial_count = len(df)
        valid_states = set(STATE_CODE_MAP.keys())
        
        # Normalize: title case to match map keys if needed, but assuming data is close
        df = df[df['state'].isin(valid_states)]
        
        dropped_count = initial_count - len(df)
        if dropped_count > 0:
            logger.warning(f"dropped {dropped_count} rows from {category} due to invalid state names (likely cities/districts).")
            
        if df.empty:
            logger.warning(f"Skipping {category} - No valid state data remaining after filtering.")
            continue
            
        # Add day features
        df['day_name'] = df['date'].dt.day_name()
        
        # Ensure order
        df = ensure_day_order(df)
        
        # Numeric columns
        numeric_cols = [c for c in df.select_dtypes(include=['number']).columns if 'pincode' not in c and 'Year' not in c]
        
        # Aggregate logic
        # We need sum per state per day.
        # Note: If we just sum, we get total volume over ALL TIME for that day name.
        # This is correct for "Generic Monday Load" analysis.
        
        agg = df.groupby(['state', 'day_name'])[numeric_cols].sum().reset_index()
        agg['Total'] = agg[numeric_cols].sum(axis=1)
        
        # 1. Generate Heatmap (All States) & Get Matrix for Insights
        state_day_matrix = plot_full_state_heatmap(agg, category)
        
        # 2. Generate Server Load Insights
        insights = generate_server_load_insights(state_day_matrix, category)
        report_content.append(insights)
        
        # 3. Aggregate Daily Global Trend (Monday-Sunday)
        global_day = agg.groupby('day_name')['Total'].sum().reset_index()
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=global_day, x='day_name', y='Total', palette='viridis')
        plt.title(f'Global {category.capitalize()} Volume by Day of Week')
        plt.ylabel('Total Volume')
        plt.xlabel('Day')
        plt.gca().yaxis.set_major_formatter(indian_formatter)
        plt.tight_layout()
        
        save_path = os.path.join(FIGURES_DIR, 'daywise', f'{category}_global_day_trend.png')
        plt.savefig(save_path)
        plt.close()
        
    # Write Report
    report_path = os.path.join(REPORTS_DIR, 'daywise_insights.md')
    with open(report_path, 'w') as f:
        f.write("\n".join(report_content))
        
    logger.info(f"Analysis Complete. Report written to {report_path}")
