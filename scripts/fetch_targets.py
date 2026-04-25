import requests
import sqlite3
import os
import sys


def ensure_disease(conn, disease_name):
    """diseases 테이블에 질환을 등록하고 disease_id를 반환한다."""
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO diseases (name) VALUES (?)", (disease_name,))
    conn.commit()
    cur.execute("SELECT id FROM diseases WHERE name = ?", (disease_name,))
    row = cur.fetchone()
    return row[0] if row else None


def search_uniprot_by_disease(disease_name, limit=3):
    print(f"Searching UniProt for targets related to: {disease_name}")
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f'disease:"{disease_name}" AND organism_id:9606 AND reviewed:true',
        "format": "json",
        "size": limit,
        "fields": "accession,gene_names,sequence,xref_pdb"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"  Retrying with broader query...")
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


def save_target(db_path, target_data, disease_id):
    """타겟을 DB에 저장한다. disease_id를 함께 기록한다."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO targets (uniprot_id, gene_name, sequence, pdb_id, disease_id)
    VALUES (?, ?, ?, ?, ?)
    """, (
        target_data['uniprot_id'],
        target_data['gene_name'],
        target_data['sequence'],
        target_data['pdb_id'],
        disease_id
    ))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_targets.py <disease_name>")
        disease = "Alzheimer"
    else:
        disease = sys.argv[1]

    db_file = os.path.join("data", "mg_discovery.db")
    os.makedirs(os.path.dirname(db_file), exist_ok=True)

    # 질환 등록 및 disease_id 취득
    conn = sqlite3.connect(db_file)
    disease_id = ensure_disease(conn, disease)
    conn.close()
    print(f"Disease '{disease}' registered with id={disease_id}")

    targets = search_uniprot_by_disease(disease)
    if not targets:
        print(f"No targets found for disease: {disease}")
    else:
        for data in targets:
            save_target(db_file, data, disease_id)
            print(f"Saved {data['gene_name']} ({data['uniprot_id']}) with PDB: {data['pdb_id']}")
