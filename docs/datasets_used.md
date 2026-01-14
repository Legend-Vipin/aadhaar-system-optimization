# Datasets Used

We strictly utilized the specific anonymized datasets provided by UIDAI for this hackathon. No external demographic or census data was merged, ensuring full compliance with competition terms.

## 1. Aadhaar Enrolment Data
This dataset tracks the volume of new Aadhaar generations.
- **`date`**: Essential for temporal analysis and detecting seasonality/holiday impacts.
- **`state`**: The primary unit of administrative governance; crucial for regional clustering.
- **`pincode`**: Used for aggregation to District/State levels; granularity allows for future hyper-local analysis.
- **`age_0_5` / `age_5_17` / `age_18_greater`**: These demographic buckets allow us to distinguish between "Child Enrolment" (mandatory updates) and "Adult Enrolment" (new entries), which require different operational resources.

## 2. Aadhaar Biometric Update Data
Tracks updates to biometric modalities (Iris, Fingerprint, Photo).
- **`bio_age_5_17`**: Critical for monitoring the mandatory biometric updates required for children, a key Key Performance Indicator (KPI) for the ecosystem.

## 3. Aadhaar Demographic Update Data
Tracks text-based updates (Name, Address, DoB).
- **`demo_age_...`**: metrics used to correlate "Correction Drives" or name-change trends with specific time periods.
