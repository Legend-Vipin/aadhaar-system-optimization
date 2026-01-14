import os
import sys
from pathlib import Path
from src.reporting import PDFReport, clean_markdown, REPORTS_DIR, FIGURES_DIR

# Extend the existing PDFReport class to add specific competition sections
class EnhancedPDFReport(PDFReport):
    def add_advanced_insights_section(self):
        self.add_page()
        self.chapter_title("5. Advanced Insights: Operational Maturity & Seasonality")
        self.chapter_body_text(
            "Beyond basic trends, we analyzed the 'Operational Maturity' of each state to distinguish between "
            "Growth Markets (high new enrolments) and Sustainment Markets (high updates). "
            "This distinction is crucial for resource allocation: Growth markets need more enrolment kits, "
            "while Sustainment markets need efficient update workflows."
        )

        # OMI Plot
        self.add_plot(
            os.path.join(FIGURES_DIR, 'operational_maturity_bubble.png'), 
            "Operational Maturity Index (Values > 0.5 indicate update-heavy loads)", 
            h=90
        )
        self.chapter_body_text(
            "The cluster analysis reveals distinct operational phases. States in Green are 'Maure', "
            "focusing on maintenance. States in Red are 'Expanding', driving new Aadhaar adoption."
        )

        # Heatmap
        self.add_plot(
            os.path.join(FIGURES_DIR, 'temporal_heatmap.png'), 
            "Seasonal-Weekly Activity Heatmap", 
            h=80
        )
        self.chapter_body_text(
            "The heatmap exposes the interaction between seasonality and weekly cycles. "
            "Resource planning must account for these compound peak periods."
        )

    def add_daywise_insights_section(self):
        self.add_page()
        self.chapter_title("6. Day-Wise Server Load & Burstiness Analysis")
        
        # Add generated text insights
        daywise_report = os.path.join(REPORTS_DIR, 'daywise_insights.md')
        
        if os.path.exists(daywise_report):
            from src.reporting import add_markdown_section
            # We use the add_markdown_section utility to parse headers properly
            add_markdown_section(self, daywise_report)
        else:
            self.chapter_body_text("Day-wise insights report not found.")

        # Add Full Heatmap
        self.add_plot(
            os.path.join(FIGURES_DIR, 'daywise/enrolment_state_heatmap_FULL.png'),
            "State-Wise Weekly Load Heatmap",
            h=110
        )

    def add_impact_section(self):
        self.add_page()
        self.chapter_title("7. Impact & Strategic Recommendations")
        
        docs_dir = Path(__file__).resolve().parent.parent / 'docs'
        impact_file = docs_dir / 'impact_strategy.md'
        
        if impact_file.exists():
            from src.reporting import add_markdown_section
            add_markdown_section(self, impact_file)
        else:
            self.chapter_body_text("Impact strategy document missing.")

def generate_enhanced_report():
    print("Generating Competition Submission PDF...")
    pdf = EnhancedPDFReport()
    
    docs_dir = Path(__file__).resolve().parent.parent / 'docs'
    src_dir = Path(__file__).resolve().parent.parent / 'src'

    # --- Reusing Existing Sections (1-4) ---
    from src.reporting import add_markdown_section
    
    # 1. Problem
    add_markdown_section(pdf, docs_dir / 'problem_statement.md')
    
    # 2. Datasets
    # We want to add specific Time Range info here as requested
    pdf.add_page()
    pdf.chapter_title("2. Datasets Used & Integrity Check")
    # Read the existing doc but maybe preyface it? 
    # Actually, simpler to just use specific generated text if we want dynamic info, 
    # but the doc is static. Let's just append the doc.
    with open(docs_dir / 'datasets_used.md', 'r') as f:
        content = f.read()
    # We can inject info if we had it, but for now we follow the doc.
    pdf.chapter_body_text(content)

    # 3. Methodology
    add_markdown_section(pdf, docs_dir / 'methodology.md')

    # 4. Standard Analysis
    pdf.add_page()
    pdf.chapter_title("4. Exploratory Data Analysis (Standard)")
    # Re-add the standard plots from existing logic
    # Enrolment Trend
    pdf.add_plot(os.path.join(FIGURES_DIR, 'enrolment_trend.png'), "Enrolment Trends (7-Day Mav Avg)")
    # Clusters
    pdf.add_plot(os.path.join(FIGURES_DIR, 'clustering_states.png'), "State Clustering (Enrolment vs Biometric)", h=100)
    # Anomalies
    pdf.add_plot(os.path.join(FIGURES_DIR, 'enrolment_anomalies.png'), "Detected Operational Spikes/Drops", h=70)

    # --- NEW SECTIONS ---
    # 5. Advanced Insights
    pdf.add_advanced_insights_section()

    # 6. Day-Wise Analysis (New)
    pdf.add_daywise_insights_section()

    # 7. Impact
    pdf.add_impact_section()

    # --- CODE APPENDIX ---
    pdf.add_page()
    pdf.chapter_title("8. Appendix: Reproducible Codebase")
    pdf.chapter_body_text("The following files encompass the complete analytical pipeline.")
    
    files_to_include = [
        'src/main_submission.py',
        'src/advanced_analytics.py',
        'src/analytics.py', 
        'src/reporting_extended.py'
    ]
    for relative_path in files_to_include:
        full_path = src_dir.parent / relative_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                 content = f.read()
            # FPDF (standard fonts) does not support Unicode emojis. 
            # We strip them to avoid encoding errors.
            content = content.encode('latin-1', 'replace').decode('latin-1')
            pdf.add_code_file(str(full_path), content)

    output_path = os.path.join(REPORTS_DIR, "Aadhaar_Solution_Submission.pdf")
    pdf.output(output_path)
    print(f"Submission Report saved as {output_path}")

if __name__ == "__main__":
    generate_enhanced_report()
