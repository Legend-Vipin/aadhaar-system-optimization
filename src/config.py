import os
from pathlib import Path

# Base dir is the parent of the directory containing this config file (src) -> root
BASE_DIR = Path(__file__).resolve().parent.parent

# Define data directories
DATA_DIRS = {
    'biometric': os.path.join(BASE_DIR, 'data', 'api_data_aadhar_biometric'),
    'demographic': os.path.join(BASE_DIR, 'data', 'api_data_aadhar_demographic'),
    'enrolment': os.path.join(BASE_DIR, 'data', 'api_data_aadhar_enrolment')
}

# Output directories
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
FIGURES_DIR = os.path.join(OUTPUTS_DIR, 'figures')
REPORTS_DIR = os.path.join(OUTPUTS_DIR, 'reports')
TABLES_DIR = os.path.join(OUTPUTS_DIR, 'tables')

for d in [FIGURES_DIR, REPORTS_DIR, TABLES_DIR]:
    os.makedirs(d, exist_ok=True)

# Deprecated but kept for compatibility with existing code until fully refactored
PLOT_DIR = FIGURES_DIR
