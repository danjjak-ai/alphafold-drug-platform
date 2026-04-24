import os
import sqlite3
import pandas as pd
from datetime import datetime

def generate_report(db_path, output_dir):
    """
    Generate an executive summary report from the discovery database.
    Outputs a Markdown file which can be converted to PDF.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "results_report.md")

    conn = sqlite3.connect(db_path)
    
    # Get target list for the report
    cursor = conn.cursor()
    cursor.execute("SELECT gene_name FROM targets")
    genes = [row[0] for row in cursor.fetchall() if row[0]]
    gene_str = ", ".join(genes) if genes else "specified targets"
    
    # query top candidates
    query = """
    SELECT 
        c.chembl_id, 
        c.name as compound_name,
        t.gene_name as target,
        MIN(d.vina_score) as highest_affinity,
        c.max_phase,
        m.mmgbsa_score
    FROM docking_results d
    JOIN compounds c ON d.compound_id = c.id
    JOIN targets t ON d.target_id = t.id
    LEFT JOIN mmgbsa_results m ON c.id = m.compound_id AND t.id = m.target_id
    GROUP BY c.chembl_id, t.gene_name
    ORDER BY highest_affinity ASC
    LIMIT 10
    """
    try:
        top_df = pd.read_sql_query(query, conn)
    except Exception as e:
        top_df = pd.DataFrame()
        print(f"Error querying top candidates: {e}")
        
    conn.close()

    date_str = datetime.now().strftime("%Y-%m-%d")

    md_content = f"""# Executive Summary: Drug Repurposing Discovery Report
**Generated Date:** {date_str}

## 1. Project Overview
This report summarizes the findings from the Discovery Core platform. The goal is to identify promising FDA-approved (or late clinical phase) drugs that can be repurposed, targeting key proteins ({gene_str}).

## 2. Methodology
* **Target Structures:** Structural models generated via AlphaFold or fetched from RCSB PDB.
* **Virtual Screening:** Molecular docking performed using AutoDock Vina.
* **Refinement:** High-scoring candidates underwent MM-GBSA rescoring (AmberTools).
* **AI Evaluation:** Activity probabilities assessed using Baseline Machine Learning models.

## 3. Top 10 Candidate Drugs

| Rank | ChEMBL ID | Name | Target | Vina Score (kcal/mol) | MM-GBSA (kcal/mol) | Max Phase |
|---:|:---|:---|:---|---:|---:|---:|
"""
    if not top_df.empty:
        for i, row in top_df.iterrows():
            mmgbsa_str = f"{row['mmgbsa_score']:.2f}" if pd.notna(row.get('mmgbsa_score')) else "N/A"
            md_content += f"| {i+1} | {row['chembl_id']} | {row['compound_name'] or 'Unknown'} | {row['target']} | {row['highest_affinity']:.2f} | {mmgbsa_str} | {row['max_phase']} |\n"
    else:
        md_content += "| - | No data available | - | - | - | - | - |\n"

    md_content += """
## 4. Limitations
* In silico predictions require empirical validation.
* AI models depend on historical training data distribution.

## 5. Next Steps Proposed
* **In Vitro Validation:** Select the top 3 candidates for binding affinity assays (e.g., SPR).
* **Cellular Assays:** Test efficacy on AChR clustering in myotube models.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Report successfully generated at: {report_path}")
    print("For PDF output, use tools like pandoc or markdown-pdf.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    results_dir = os.path.join(base_dir, "results")
    generate_report(db_path, results_dir)
