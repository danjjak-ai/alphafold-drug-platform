from chembl_webresource_client.new_client import new_client
import pandas as pd
import os

def fetch_assay_data_by_accession(accession, target_name):
    print(f"Fetching ChEMBL assay data for {target_name} ({accession})...")
    
    # 1. Get targets by accession
    target = new_client.target
    targets = target.filter(target_components__accession=accession).only('target_chembl_id')
    target_ids = [t['target_chembl_id'] for t in targets]
    
    # 2. Get activities for these targets
    activity = new_client.activity
    res = activity.filter(target_chembl_id__in=target_ids).only(['molecule_chembl_id', 'canonical_smiles', 'standard_type', 'standard_value', 'standard_units'])
    
    df = pd.DataFrame(list(res))
    if not df.empty:
        df['target_name'] = target_name
        df = df[df['standard_type'].astype(str).str.upper().isin(['IC50', 'KI', 'EC50'])]
        df['standard_value'] = pd.to_numeric(df['standard_value'], errors='coerce')
        df = df.dropna(subset=['standard_value'])
    return df

if __name__ == "__main__":
    # Correct PDB/UniProt-mapped accessions
    targets = [
        ("P02708", "CHRNA1"),
        ("O15146", "MUSK"),
        ("O75096", "LRP4")
    ]
    
    os.makedirs("data/processed", exist_ok=True)
    all_data = []
    for accession, name in targets:
        df = fetch_assay_data_by_accession(accession, name)
        if not df.empty:
            all_data.append(df)
            print(f"Found {len(df)} activities for {name}")
    
    if all_data:
        final_df = pd.concat(all_data)
        final_df.to_csv("data/processed/chembl_training_data.csv", index=False)
        print(f"Completed fetching training data. Total: {len(final_df)} rows")
    else:
        print("No training data found.")
