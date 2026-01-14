import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DATA_DIRS
from src.data_loader import load_data, clean_data
from src.analytics import analyze_dataset, perform_advanced_analysis
from src.analysis_date_holiday import analyze_date_intelligence
from src.analysis_daywise_week import analyze_daywise
from src.advanced_analytics import AdvancedAnalytics
from src.reporting_extended import generate_enhanced_report

def main():
    print("--- 🚀 Starting Aadhaar Hackathon Competition Submission Run ---")
    datasets = {}
    
    # 1. Load & Clean
    for category, path in DATA_DIRS.items():
        df = load_data(category, path)
        if df is not None:
            datasets[category] = clean_data(df, category)

    # 2. Standard Analytics (Base Requirements)
    # This generates the standard figures used in Section 4
    analyze_dataset(datasets)
    perform_advanced_analysis(datasets)
    analyze_date_intelligence(datasets)
    analyze_daywise(datasets)

    # 3. Advanced Analytics (Competitive Edge)
    # This generates the OMI bubble chart and Heatmap for Section 5
    adv = AdvancedAnalytics(datasets)
    adv.compute_operational_maturity_index()
    adv.generate_temporal_heatmap()

    # 4. Generate Final PDF
    # Combines everything into the submisson document
    generate_enhanced_report()
    
    print("--- ✅ Submission Run Completed Successfully ---")

if __name__ == "__main__":
    main()
