import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from src.config import FIGURES_DIR
from src.utils import indian_formatter

class AdvancedAnalytics:
    def __init__(self, datasets):
        self.datasets = datasets
        self.figures_dir = FIGURES_DIR
        os.makedirs(self.figures_dir, exist_ok=True)

    def compute_operational_maturity_index(self):
        """
        Calculates the Operational Maturity Index (OMI) for each state.
        OMI = Total Updates / (Total Enrolments + Total Updates)
        
        Interpretation:
        - High OMI (> 0.7): Maintenance/Mature Phase (Testing demographic/biometric updates dominant)
        - Low OMI (< 0.3): Expansion Phase (New enrolments dominant)
        """
        if 'enrolment' not in self.datasets:
            print("Skipping OMI: Enrolment data missing.")
            return None
            
        print("Calculating Operational Maturity Index (OMI)...")
        
        # Prepare Enrolment
        enrol = self.datasets['enrolment']
        numeric_enrol = enrol.select_dtypes(include=['number']).columns
        # Exclude pincode, YearMonth if present
        cols = [c for c in numeric_enrol if 'pincode' not in c and 'Year' not in c]
        enrol_state = enrol.groupby('state')[cols].sum().reset_index()
        enrol_state['Total_Enrolment'] = enrol_state[cols].sum(axis=1)

        # Prepare Updates (Biometric + Demographic)
        total_updates_state = pd.DataFrame({'state': enrol_state['state'], 'Total_Updates': 0})
        
        for cat in ['biometric', 'demographic']:
            if cat in self.datasets:
                df = self.datasets[cat]
                numeric = df.select_dtypes(include=['number']).columns
                cols_up = [c for c in numeric if 'pincode' not in c and 'Year' not in c]
                grp = df.groupby('state')[cols_up].sum().reset_index()
                grp[f'Total_{cat}'] = grp[cols_up].sum(axis=1)
                
                # Merge to ensure alignment
                total_updates_state = pd.merge(total_updates_state, grp[['state', f'Total_{cat}']], 
                                             on='state', how='outer').fillna(0)
                total_updates_state['Total_Updates'] += total_updates_state[f'Total_{cat}']

        # Merge Enrolment and Updates
        merged = pd.merge(enrol_state[['state', 'Total_Enrolment']], 
                        total_updates_state[['state', 'Total_Updates']], 
                        on='state', how='inner')

        # Calculate OMI
        merged['Total_Volume'] = merged['Total_Enrolment'] + merged['Total_Updates']
        merged['OMI'] = merged['Total_Updates'] / merged['Total_Volume']
        
        # Sort for visualization
        merged = merged.sort_values('OMI', ascending=False)
        
        # Plot
        plt.figure(figsize=(14, 8))
        # Color bar logic
        sc = plt.scatter(merged['OMI'], merged['Total_Volume'], 
                    s=merged['Total_Volume'] / merged['Total_Volume'].max() * 1000, 
                    alpha=0.6, c=merged['OMI'], cmap='RdYlGn')
        
        plt.colorbar(sc, label='Operational Maturity Index (Red=Growth, Green=Mature)')
        
        # Annotate meaningful states (Top 5 Mature, Top 5 Growth, Top 5 Volume)
        annotate_mask = (merged['OMI'].rank(ascending=False) <= 5) | \
                        (merged['OMI'].rank(ascending=True) <= 5) | \
                        (merged['Total_Volume'].rank(ascending=False) <= 5)
                        
        for idx, row in merged[annotate_mask].iterrows():
            plt.text(row['OMI'], row['Total_Volume'], row['state'], fontsize=8)

        plt.title('Operational Maturity vs. Scale: Identifying Growth Frontiers')
        plt.xlabel('Operational Maturity Index (Updates Share)')
        plt.ylabel('Total Transaction Volume')
        plt.gca().yaxis.set_major_formatter(indian_formatter)
        plt.axvline(0.5, linestyle='--', color='gray', alpha=0.5)
        plt.tight_layout()
        
        output_path = os.path.join(self.figures_dir, 'operational_maturity_bubble.png')
        plt.savefig(output_path)
        plt.close()
        
        return merged

    def generate_temporal_heatmap(self):
        """
        Generates a heatmap of Activity Intensity: Day of Week vs Month.
        Helps identify seasonal-weekly interaction effects (e.g. 'Are Mondays in May busier than Mondays in December?')
        """
        if 'enrolment' not in self.datasets:
            return

        print("Generating Temporal Heatmap...")
        df = self.datasets['enrolment'].copy()
        
        # Feature Engineering
        df['Month'] = df['date'].dt.month_name()
        df['DayOfWeek'] = df['date'].dt.day_name()
        
        # Numeric cols for volume
        numeric_cols = [c for c in df.select_dtypes(include=['number']).columns if 'pincode' not in c and 'Year' not in c]
        df['Volume'] = df[numeric_cols].sum(axis=1)

        # Aggregate
        pivot = df.pivot_table(index='DayOfWeek', columns='Month', values='Volume', aggfunc='mean')
        
        # Reorder
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        months_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        # Filter only existing months/days
        existing_months = [m for m in months_order if m in pivot.columns]
        pivot = pivot.reindex(index=days_order, columns=existing_months)

        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot, cmap='YlOrRd', annot=False, fmt='.0f', cbar_kws={'label': 'Avg Daily Volume'})
        plt.title('Temporal Heatmap: Enrolment Intensity (Day vs Month)')
        plt.tight_layout()
        
        output_path = os.path.join(self.figures_dir, 'temporal_heatmap.png')
        plt.savefig(output_path)
        plt.close()
