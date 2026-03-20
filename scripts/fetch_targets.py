import requests
import sqlite3
import os

def fetch_uniprot_data(uniprot_id):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        gene_name = data.get('genes', [{}])[0].get('geneName', {}).get('value', '')
        sequence = data.get('sequence', {}).get('value', '')
        # Get primary PDB ID from cross references
        pdb_id = None
        for xref in data.get('uniProtKBCrossReferences', []):
            if xref.get('database') == 'PDB':
                pdb_id = xref.get('id')
                break
        return {
            'uniprot_id': uniprot_id,
            'gene_name': gene_name,
            'sequence': sequence,
            'pdb_id': pdb_id
        }
    return None

def save_target(db_path, target_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO targets (uniprot_id, gene_name, sequence, pdb_id)
    VALUES (?, ?, ?, ?)
    """, (target_data['uniprot_id'], target_data['gene_name'], target_data['sequence'], target_data['pdb_id']))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    targets = ["P02708", "O15146", "O75096"]
    for tid in targets:
        print(f"Fetching data for {tid}...")
        data = fetch_uniprot_data(tid)
        if data:
            save_target(db_file, data)
            print(f"Saved {data['gene_name']} ({tid})")
        else:
            print(f"Failed to fetch {tid}")
