from fpdf import FPDF
import os
import glob
from pathlib import Path
from src.config import FIGURES_DIR, REPORTS_DIR

# Try importing FPDF, handle if missing
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("FPDF not found. PDF report will not be generated.")

import re

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Aadhaar Data Analysis Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body_text(self, body, style=''):
        self.set_font('Arial', style, 11)
        # Clean markdown if present in body passed directly
        body = clean_markdown(body)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_plot(self, image_path, title='', h=100):
        if os.path.exists(image_path):
            if self.get_y() > 200: # New page if too low
                self.add_page()
            
            if title:
                self.set_font('Arial', 'B', 11)
                self.cell(0, 10, title, 0, 1, 'L')
            
            self.image(image_path, x=10, w=190, h=h)
            self.ln(5) 
        else:
            print(f"Image {image_path} not found.")

    def add_code_file(self, filename, content):
        self.add_page()
        self.chapter_title(f"Code: {os.path.basename(filename)}")
        
        # VS Code Dark Theme Settings
        self.set_fill_color(30, 30, 30)       # Dark Grey Background
        self.set_text_color(220, 220, 220)    # Light Grey Text
        self.set_font('Courier', '', 8)
        
        # Print Code Block with Background Fill
        self.multi_cell(0, 4, content, fill=True)
        
        # Reset to Default (Black Text, White Fill)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)

import re
import ast

def clean_markdown(text):
    # Remove bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove code `text`
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove headers (at start of line/string)
    text = re.sub(r'^#+\s*', '', text)
    return text

def get_function_summaries(src_dir):
    summary = ""
    code_files = sorted(glob.glob(str(src_dir / '*.py')))
    for file_path in code_files:
        filename = os.path.basename(file_path)
        summary += f"\n### Module: {filename}\n"
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
            if not functions:
                 summary += "- No top-level functions.\n"
            for func in functions:
                doc = ast.get_docstring(func)
                first_line = doc.strip().splitlines()[0] if doc else 'No description available'
                summary += f"- {func.name}: {first_line}\n"
        except Exception as e:
            summary += f"- Error parsing {filename}: {e}\n"
    return summary



def add_markdown_section(pdf, filepath, title=None):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return

    if title:
        pdf.add_page()
        pdf.chapter_title(title)
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        # Skip top-level headers if we provided a title, or just print them
        # We'll treat # as H1, ## as H2
        
        # CLEANUP: FPDF latin-1 issues
        line = line.replace('\u2013', '-').replace('\u2014', '-').replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        
        if line.startswith('# '):
            if not title: # If no override title, use the file's H1
                pdf.add_page()
                pdf.chapter_title(clean_markdown(line.replace('# ', '')))
            else:
                pdf.ln(2)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, clean_markdown(line.replace('# ', '')), 0, 1)
        elif line.startswith('## '):
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, clean_markdown(line.replace('## ', '')), 0, 1)
        elif line.startswith('### '):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, clean_markdown(line.replace('### ', '')), 0, 1)
        elif line.startswith('- '):
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 6, '  ' + chr(149) + ' ' + clean_markdown(line.replace('- ', '')))
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '): # specific numbered list handle
             pdf.set_font('Arial', '', 11)
             pdf.multi_cell(0, 6, clean_markdown(line))
        else:
            if line:
                pdf.set_font('Arial', '', 11)
                pdf.multi_cell(0, 6, clean_markdown(line))

def generate_report():
    if not PDF_AVAILABLE:
        return

    print("Generating Judge-Ready PDF Report...")
    pdf = PDFReport()
    
    docs_dir = Path(__file__).resolve().parent.parent / 'docs'
    src_dir = Path(__file__).resolve().parent.parent / 'src'

    # --- SECTION 1: Problem Statement and Approach ---
    add_markdown_section(pdf, docs_dir / 'problem_statement.md')

    # --- SECTION 2: Datasets Used ---
    add_markdown_section(pdf, docs_dir / 'datasets_used.md')

    # --- SECTION 3: Methodology ---
    add_markdown_section(pdf, docs_dir / 'methodology.md')

    # --- SECTION 4: Data Analysis & Visualisation ---
    pdf.add_page()
    pdf.chapter_title("4. Data Analysis & Visualisation")
    pdf.chapter_body_text("The following visualizations demonstrate key findings from the data.")
    
    # Enrolment Trend
    pdf.add_plot(os.path.join(FIGURES_DIR, 'enrolment_trend.png'), "Enrolment Trends (7-Day Mav Avg)")
    
    # Holiday Impact
    pdf.add_plot(os.path.join(FIGURES_DIR, 'holiday_impact.png'), "Impact of Holidays on Volume", h=90)
    pdf.chapter_body_text("Analysis confirms significant operational dip on holidays.")

    # Clusters
    pdf.add_plot(os.path.join(FIGURES_DIR, 'clustering_states.png'), "State Clustering (Enrolment vs Biometric)", h=100)
    
    # Anomalies
    pdf.add_plot(os.path.join(FIGURES_DIR, 'enrolment_anomalies.png'), "Detected Operational Spikes/Drops", h=70)
    
    # Forecast
    pdf.add_plot(os.path.join(FIGURES_DIR, 'enrolment_forecast.png'), "30-Day Enrolment Forecast", h=70)

    # --- SECTION 5: Conclusion & Impact ---
    add_markdown_section(pdf, docs_dir / 'conclusion.md')

    # --- SECTION 6: Functional Capabilities ---
    # Generate summary of working functions
    func_summary = get_function_summaries(src_dir)
    overview_path = docs_dir / 'functional_overview.md'
    with open(overview_path, 'w') as f:
        f.write(func_summary)

    # Add the extracted function info to the PDF
    add_markdown_section(pdf, overview_path, title="6. Functional Capabilities")

    # Save to REPORTS_DIR
    output_path = os.path.join(REPORTS_DIR, "Aadhaar_Data_Insights_Patterns_Anomalies_Predictions.pdf")

    # --- SECTION 7: Appendix - Code Files ---
    # The prompt specifically requests code files to be included in the PDF itself.
    pdf.add_page()
    pdf.chapter_title("7. Appendix: Analysis Source Code")
    pdf.chapter_body_text("The following source code files contain the logic used for the analysis, anomaly detection, and forecasting presented in this report.")

    files_to_include = ['src/analytics.py', 'src/analysis_date_holiday.py']
    for relative_path in files_to_include:
        full_path = src_dir / os.path.basename(relative_path)
        if full_path.exists():
            with open(full_path, 'r') as f:
                 content = f.read()
            pdf.add_code_file(str(full_path), content)

    pdf.output(output_path)
    print(f"Report saved as {output_path}")

if __name__ == "__main__":
    generate_report()
