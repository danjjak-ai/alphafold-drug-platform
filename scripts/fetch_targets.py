import requests
import sqlite3
import os
import sys

def search_uniprot_by_disease(disease_name, limit=3):
    print(f"Searching UniProt for targets related to: {disease_name}")
    # Search for human proteins associated with the disease keyword
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f'disease:"{disease_name}" AND organism_id:9606 AND reviewed:true',
        "format": "json",
        "size": limit,
        "fields": "accession,gene_names,sequence,xref_pdb"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error searching UniProt: {response.status_code}")
        # Fallback to broader keyword search if disease search yields nothing
        params["query"] = f'{disease_name} AND organism_id:9606 AND reviewed:true'
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return []

    data = response.json()
    results = []
    for entry in data.get('results', []):
        uniprot_id = entry.get('primaryAccession')
        gene_name = ""
        genes = entry.get('genes', [])
        if genes:
            gene_name = genes[0].get('geneName', {}).get('value', '')
        
        sequence = entry.get('sequence', {}).get('value', '')
        
        pdb_id = None
        for xref in entry.get('uniProtKBCrossReferences', []):
            if xref.get('database') == 'PDB':
                pdb_id = xref.get('id')
                break
        
        results.append({
            'uniprot_id': uniprot_id,
            'gene_name': gene_name,
            'sequence': sequence,
            'pdb_id': pdb_id
        })
    return results

def save_target(db_path, target_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Use OR IGNORE to avoid duplicates
    cursor.execute("""
    INSERT OR IGNORE INTO targets (uniprot_id, gene_name, sequence, pdb_id)
    VALUES (?, ?, ?, ?)
    """, (target_data['uniprot_id'], target_data['gene_name'], target_data['sequence'], target_data['pdb_id']))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_targets.py <disease_name>")
        # Default for testing
        disease = "Alzheimer"
    else:
        disease = sys.argv[1]

    db_file = os.path.join("data", "mg_discovery.db")
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    
    targets = search_uniprot_by_disease(disease)
    if not targets:
        print(f"No targets found for disease: {disease}")
    else:
        for data in targets:
            save_target(db_file, data)
            print(f"Saved {data['gene_name']} ({data['uniprot_id']}) with PDB: {data['pdb_id']}")
