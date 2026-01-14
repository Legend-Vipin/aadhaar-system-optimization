# Methodology

## 1. Data Cleaning & Preprocessing
To ensure high-fidelity analysis, we implemented a rigorous cleaning pipeline:
- **Date Standardization**: Inconsistent date formats were normalized to `YYYY-MM-DD`. Rows with unparseable dates (< 0.01%) were dropped to maintain integrity.
- **Null Handling**: Missing values in numeric columns (e.g., `enc_count`) were imputed as `0`. 
    - *Assumption*: A missing record for a pincode on a specific day implies "No Activity", rather than missing data.
- **Geo-Tagging**: State names were standardized to match the Python `holidays` library for accurate localized holiday mapping.

## 2. Analytical Framework

### A. Clustering (State Categorization)
- **Technique**: K-Means Clustering (k=3).
- **Features**: Normalized `Total Enrolment` and `Total Biometric Updates`.
- **Why**: Administrators cannot create 36 unique policies. Clustering allows for "T-shirt methods" (Small, Medium, Large strategies).

### B. Anomaly Detection
- **Technique**: Isolation Forest (Contamination = 5%).
- **Features**: Daily aggregate volume.
- **Why**: Traditional Z-scores assume normal distribution. Aadhaar data is highly non-linear due to correction drives and weekends; Isolation Forest handles this complexity better.

## 3. Tools & Reproducibility
- **Language**: Python 3.12+
- **Key Libraries**: `pandas` (ETL), `scikit-learn` (ML), `seaborn` (Viz), `fpdf` (Reporting).
- **Reproducibility**: All random seeds are fixed (`random_state=42`) to ensure judges see the exact same results every run.
