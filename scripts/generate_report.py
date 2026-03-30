import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

class MGReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MG-Repurposing AI Simulator: Discovery Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_report(db_path, output_pdf_path):
    conn = sqlite3.connect(db_path)
    
    # 1. 상위 후보 데이터 조회 (Vina + MM-GBSA)
    query = """
    SELECT 
        c.chembl_id, 
        c.name as compound_name, 
        t.gene_name as target,
        d.vina_score,
        m.mmgbsa_dG
    FROM docking_results d
    JOIN compounds c ON d.compound_id = c.id
    JOIN targets t ON d.target_id = t.id
    LEFT JOIN mmgbsa_results m ON (m.compound_id = c.id AND m.target_id = t.id)
    ORDER BY d.vina_score ASC
    LIMIT 20
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("No data found to generate report.")
        return

    # 2. 시각화 차트 생성
    plt.figure(figsize=(10, 6))
    plt.style.use('ggplot')
    
    # Vina vs MM-GBSA correlation plot
    valid_df = df.dropna(subset=['mmgbsa_dG'])
    if not valid_df.empty:
        plt.scatter(valid_df['vina_score'], valid_df['mmgbsa_dG'], color='teal', alpha=0.6)
        for i, txt in enumerate(valid_df['chembl_id']):
            plt.annotate(txt, (valid_df['vina_score'].iloc[i], valid_df['mmgbsa_dG'].iloc[i]), fontsize=8)
        plt.xlabel('Vina Score (kcal/mol)')
        plt.ylabel('MM-GBSA dG (kcal/mol)')
        plt.title('Binding Affinity Correlation')
        chart_path = "results/reports/affinity_chart.png"
        plt.savefig(chart_path)
        plt.close()
    else:
        chart_path = None

    # 3. PDF 생성
    pdf = MGReport()
    
    # 한글 폰트 추가 시도 (Windows 전용)
    font_path = "C:/Windows/Fonts/malgun.ttf"
    if os.path.exists(font_path):
        pdf.add_font("Malgun", "", font_path)
        kor_font = "Malgun"
    else:
        kor_font = "Arial"

    pdf.add_page()
    
    # 개요 섹션
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1)
    pdf.set_font("Arial", '', 10)
    summary_text = (
        f"This report presents the in-silico screening results for Myasthenia Gravis (MG) drug repurposing. "
        f"A total of {len(df)} top candidates were evaluated across biological targets (CHRNA1, MuSK, LRP4). "
        f"Advanced rescoring using MM-GBSA was applied to prioritize the most promising hits."
    )
    pdf.multi_cell(0, 8, summary_text)
    pdf.ln(5)

    # 차트 섹션
    if chart_path:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "2. Binding Affinity Analysis", 0, 1)
        pdf.image(chart_path, x=15, w=180)
        pdf.ln(10)

    # 데이터 테이블 섹션
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. Candidate Rankings", 0, 1)
    
    # Table Header
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(30, 8, "ChEMBL ID", 1, 0, 'C', 1)
    pdf.cell(50, 8, "Compound Name", 1, 0, 'C', 1)
    pdf.cell(30, 8, "Target", 1, 0, 'C', 1)
    pdf.cell(35, 8, "Vina Score", 1, 0, 'C', 1)
    pdf.cell(35, 8, "MM-GBSA dG", 1, 1, 'C', 1)

    # Table Body
    pdf.set_font("Arial", '', 8)
    for _, row in df.iterrows():
        pdf.cell(30, 7, str(row['chembl_id']), 1)
        # Handle Potential Unicode in names
        name = str(row['compound_name']) if row['compound_name'] else "N/A"
        pdf.cell(50, 7, name[:25], 1) 
        pdf.cell(30, 7, str(row['target']), 1)
        pdf.cell(35, 7, f"{row['vina_score']:.2f}", 1, 0, 'C')
        mmgbsa_val = f"{row['mmgbsa_dG']:.2f}" if pd.notnull(row['mmgbsa_dG']) else "N/A"
        pdf.cell(35, 7, mmgbsa_val, 1, 1, 'C')

    # Save PDF
    pdf.output(output_pdf_path)
    print(f"Report generated successfully: {output_pdf_path}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    os.makedirs(os.path.join(base_dir, "results", "reports"), exist_ok=True)
    report_path = os.path.join(base_dir, "results", "reports", "MG_Discovery_Report.pdf")
    
    generate_report(db_path, report_path)
