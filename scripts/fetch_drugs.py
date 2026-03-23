from chembl_webresource_client.new_client import new_client
from rdkit import Chem
from rdkit.Chem import Descriptors, FilterCatalog
import sqlite3
import os
import sys
from tqdm import tqdm

def get_pains_filter():
    params = FilterCatalog.FilterCatalogParams()
    params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
    return FilterCatalog.FilterCatalog(params)

def fetch_drugs_for_targets(db_path, disease_name=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT gene_name FROM targets")
    genes = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()

    print(f"Searching ChEMBL for drugs related to targets: {genes} or disease: {disease_name}")
    molecule = new_client.molecule
    pains_filter = get_pains_filter()
    
    all_molecules = []
    
    # 1. Search by targets if available
    if genes:
        target_client = new_client.target
        for gene in genes:
            print(f"Fetching drugs for target gene: {gene}")
            res_target = target_client.filter(target_components__accession__contains=gene).only(['target_chembl_id'])
            for t in res_target:
                t_id = t['target_chembl_id']
                activities = new_client.activity.filter(target_chembl_id=t_id, pchembl_value__gte=5)
                # Get some molecule IDs from activities
                m_ids = [a['molecule_chembl_id'] for a in activities[:50]]
                if m_ids:
                    mols = molecule.filter(molecule_chembl_id__in=m_ids, molecule_type='Small molecule').only(['molecule_chembl_id', 'pref_name', 'molecule_structures', 'molecule_properties'])
                    all_molecules.extend(list(mols))

    # 2. Search by disease if list is still small
    if len(all_molecules) < 10 and disease_name:
        print(f"Searching ChEMBL by disease keyword: {disease_name}")
        res = molecule.filter(molecule_type='Small molecule', term=disease_name).only(['molecule_chembl_id', 'pref_name', 'molecule_structures', 'molecule_properties'])
        all_molecules.extend(list(res[:100]))

    # Fallback: FDA drugs
    if not all_molecules:
        print("No specific drugs found. Fetching general FDA-approved small molecules...")
        res = molecule.filter(molecule_type='Small molecule', max_phase=4).only(['molecule_chembl_id', 'pref_name', 'molecule_structures', 'molecule_properties'])
        all_molecules = list(res[:100])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    count = 0
    seen = set()
    
    for mol in tqdm(all_molecules, desc="Processing compounds"):
        chembl_id = mol['molecule_chembl_id']
        if chembl_id in seen: continue
        seen.add(chembl_id)
        
        name = mol.get('pref_name', '') or chembl_id
        smiles = (mol.get('molecule_structures') or {}).get('canonical_smiles', '')

        if not smiles: continue
        rdmol = Chem.MolFromSmiles(smiles)
        if rdmol is None: continue

        mw = Descriptors.MolWt(rdmol)
        tpsa = Descriptors.TPSA(rdmol)
        hbd = Descriptors.NumHDonors(rdmol)
        hba = Descriptors.NumHAcceptors(rdmol)
        logp = Descriptors.MolLogP(rdmol)

        # Filter criteria: MW 150~600, RO5-ish
        if 150 <= mw <= 600 and tpsa < 140 and hbd <= 5 and hba <= 10:
            cursor.execute("""
            INSERT OR IGNORE INTO compounds (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, max_phase)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, 4))
            count += 1
            if count >= 100: break # Limit for demo purposes

    conn.commit()
    conn.close()
    print(f"Saved {count} compounds to database.")

if __name__ == "__main__":
    disease = sys.argv[1] if len(sys.argv) > 1 else None
    db_file = os.path.join("data", "mg_discovery.db")
    fetch_drugs_for_targets(db_file, disease)
