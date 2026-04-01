import os
from fpdf import FPDF

def create_pdf(txt_path, pdf_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    for line in text.splitlines():
        
        safe_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(200, 10, txt=safe_line, ln=True)
    
    pdf.output(pdf_path)

data_root = os.path.join(os.path.dirname(__file__), "data", "job descriptions")
software_dir = os.path.join(data_root, "software")

if os.path.exists(software_dir):
    for f in os.listdir(software_dir):
        if f.endswith(".txt") and not (f.endswith("_expected.json") or f.endswith("_actual.json")):
            txt_file = os.path.join(software_dir, f)
            pdf_file = os.path.splitext(txt_file)[0] + ".pdf"
            print(f"Creating {pdf_file}...")
            create_pdf(txt_file, pdf_file)
