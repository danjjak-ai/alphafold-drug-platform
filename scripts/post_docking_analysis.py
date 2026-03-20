import os
import sqlite3
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, QED

def calculate_rdkit_properties(smiles):
    """Calculate basic RDKit properties as a proxy for ADMET."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None: return None
        return {
            'MW': Descriptors.MolWt(mol),
            'LogP': Descriptors.MolLogP(mol),
            'TPSA': Descriptors.TPSA(mol),
            'HBA': Descriptors.NumHAcceptors(mol),
            'HBD': Descriptors.NumHDonors(mol),
            'QED': QED.qed(mol)
        }
    except Exception as e:
        return None

def analyze_docking_results(db_path, output_csv):
    print("Connecting to database...")
    conn = sqlite3.connect(db_path)
    
    # Fetch results with Vina score < -7.0
    query = """
    SELECT d.id as result_id, c.chembl_id, c.smiles, t.gene_name, d.vina_score
    FROM docking_results d
    JOIN compounds c ON d.compound_id = c.id
    JOIN targets t ON d.target_id = t.id
    WHERE d.vina_score <= -7.0
    ORDER BY d.vina_score ASC
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"Found {len(df)} hits with Vina score <= -7.0.")
    
    if len(df) == 0:
        print("No hits found meeting the criteria.")
        conn.close()
        return

    print("Calculating RDKit descriptor properties (ADMET proxy)...")
    properties = []
    for idx, row in df.iterrows():
        props = calculate_rdkit_properties(row['smiles'])
        if props:
            properties.append(props)
        else:
            properties.append({k: None for k in ['MW','LogP','TPSA','HBA','HBD','QED']})
            
    props_df = pd.DataFrame(properties)
    df = pd.concat([df, props_df], axis=1)
    
    # Filter by basic Lipinski's Rule of 5 loose constraints to ensure it's drug-like
    # We will just mark a 'Lipinski_Pass' column
    df['Lipinski_Pass'] = (
        (df['MW'] <= 500) &
        (df['LogP'] <= 5) &
        (df['HBD'] <= 5) &
        (df['HBA'] <= 10)
    )
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Saved filtered candidates to {output_csv}")
    
    # Also save to SQLite table 'post_docking_filtered'
    print("Saving to database table 'post_docking_filtered'...")
    # Drop table if exists to keep it clean for repeated runs
    conn.execute("DROP TABLE IF EXISTS post_docking_filtered")
    df.to_sql("post_docking_filtered", conn, index=False)
    
    print("\nTop 5 Candidates passing Lipinski:")
    top5 = df[df['Lipinski_Pass']].head(5)
    print(top5[['chembl_id', 'gene_name', 'vina_score', 'QED']])
    
    conn.close()

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    out_csv = os.path.join("results", "top_candidates.csv")
    analyze_docking_results(db_file, out_csv)
