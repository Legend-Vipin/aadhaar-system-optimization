# Aadhaar Data Analytics & ML Project
[![Reproducible](https://img.shields.io/badge/Reproducible-Yes-green)](https://github.com/astral-sh/uv)

## Overview
This project performs an in-depth analysis of anonymised Aadhaar enrolment and update datasets. By leveraging statistical modeling, detecting human-activity patterns, and analyzing holiday impacts, we provide actionable insights into the operational rhythm of the Aadhaar ecosystem.

## Key Insights ("So What?")
1. **Holiday-Driven Contraction**: National holidays see a **~73% drop** in activity.
   - *So What?*: Enrollment centers should implement staggered staffing or automated kiosks during holidays to maintain service levels.
2. **Weekend Reliance**: Operations consistently dip by **37%** on weekends.
   - *So What?*: Shifting operational hours to include weekends could offset weekday congestion.
3. **Regional Dominance**: 5 States drive **>50%** of daily volume.
   - *So What?*: These "Powerhouse" states require dedicated regional server clusters to prevent latency.

## Project Structure
```text
.
├── src/                      # Source Code
│   ├── config.py             # Centralized Configuration (Paths)
│   ├── data_loader.py        # ETL Logic
│   ├── analytics.py          # ML & Clustering Logic
│   ├── main.py               # Main Analysis Orchestrator
│   ├── reporting.py          # PDF Generation Engine
│   ├── utils.py              # Utility Functions
│   └── analysis_date_holiday.py # Holiday Intelligence Module
├── data/                     # Raw Datasets
├── docs/                     # Documentation (Executive Summary)
├── outputs/                  # Analysis Artifacts
│   ├── figures/              # Plots & Charts
│   └── reports/              # Final PDF Reports
└── submission_runner.py      # Master Execution Script
```

## Methodology & Why This Approach
We prioritized **explainable AI** over black-box deep learning because public systems require accountability.
- **Clustering (K-Means)**: Selected to objectively categorize state performance tiers without supervision.
- **Isolation Forest**: Chosen for anomaly detection because it is robust against high-dimensional noise and does not assume a normal distribution.
- **Linear Regression**: Used for short-term forecasting where trend stability is higher than seasonal complexity.

## Known Limitations
- **Anonymised Data**: Analysis is limited to aggregate trends; individual behavioral patterns cannot be inferred.
- **State Granularity**: Comparison is done at the state level; distinct district-level variances (e.g., urban vs rural) are masked.
- **Correlation ≠ Causation**: Observed dips on holidays are correlated, but operational closures vs user behavior cannot be fully disentangled without center status logs.

## How to Run

### Prerequisites
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (Recommended for dependency management)

### Installation
```bash
uv pip install -r requirements.txt
# OR manually:
uv pip install pandas matplotlib seaborn scikit-learn fpdf holidays
```

### Execution
Run the master submission script to generate all analysis and reports:
```bash
python src/main.py
```

Outputs will be generated in the `outputs/` directory:
- **Report**: `outputs/reports/Aadhaar_Analysis_Report.pdf`
- **Plots**: `outputs/figures/*.png`

## Insights
- **Weekday Dominance**: Operations peak mid-week (Wednesday/Thursday) and contract by ~37% on weekends.
- **Holiday Compliance**: National holidays see a ~73% drop in activity, indicating strong operational adherence.
- **Regional Powerhouses**: A specific cluster of 5 states drives over 50% of the daily updates.

---
*Submitted for Aadhaar Data Analytics Hackathon*
