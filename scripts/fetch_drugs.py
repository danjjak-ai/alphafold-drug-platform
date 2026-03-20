from chembl_webresource_client.new_client import new_client
from rdkit import Chem
from rdkit.Chem import Descriptors, FilterCatalog
import sqlite3
import os
from tqdm import tqdm

def get_pains_filter():
    params = FilterCatalog.FilterCatalogParams()
    params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
    return FilterCatalog.FilterCatalog(params)

def fetch_fda_drugs(db_path):
    print("Fetching FDA-approved small molecule drugs from ChEMBL...")
    molecule = new_client.molecule
    pains_filter = get_pains_filter()

    # Query: Small molecule, FDA approved (max_phase=4)
    res = molecule.filter(molecule_type='Small molecule', max_phase=4).only(['molecule_chembl_id', 'pref_name', 'molecule_structures', 'molecule_properties'])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    count = 0
    for mol in tqdm(res, total=len(res)):
        chembl_id = mol['molecule_chembl_id']
        name = mol.get('pref_name', '')
        smiles = (mol.get('molecule_structures') or {}).get('canonical_smiles', '')

        if not smiles:
            continue

        rdmol = Chem.MolFromSmiles(smiles)
        if rdmol is None:
            continue

        # RDKit Properties
        mw = Descriptors.MolWt(rdmol)
        logp = Descriptors.MolLogP(rdmol)
        tpsa = Descriptors.TPSA(rdmol)
        hbd = Descriptors.NumHDonors(rdmol)
        hba = Descriptors.NumHAcceptors(rdmol)

        # PAINS Filtering (flag only for now as per plan.md)
        pains_flag = pains_filter.HasMatch(rdmol)

        # Filter criteria as per plan.md 1.3:
        # MW 150~500, Lipinski RO5 (HBD<=5, HBA<=10), TPSA < 140
        # Lipinski check (simplified)
        if 150 <= mw <= 500 and tpsa < 140 and hbd <= 5 and hba <= 10:
            cursor.execute("""
            INSERT INTO compounds (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, max_phase)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, 4))
            count += 1

    conn.commit()
    conn.close()
    print(f"Saved {count} compounds to database.")

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    fetch_fda_drugs(db_file)
