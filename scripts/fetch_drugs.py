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


def ensure_disease(conn, disease_name):
    """diseases 테이블에 질환을 등록하고 disease_id를 반환한다."""
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO diseases (name) VALUES (?)", (disease_name,))
    conn.commit()
    cur.execute("SELECT id FROM diseases WHERE name = ?", (disease_name,))
    row = cur.fetchone()
    return row[0] if row else None


def fetch_drugs_for_targets(db_path, disease_name=None):
    conn = sqlite3.connect(db_path)

    # 질환 등록 및 disease_id 취득
    disease_id = None
    if disease_name:
        disease_id = ensure_disease(conn, disease_name)
        print(f"Disease '{disease_name}' id={disease_id}")

    # 해당 질환의 타겟만 조회 (없으면 전체)
    if disease_id:
        rows = conn.execute(
            "SELECT gene_name FROM targets WHERE disease_id = ?", (disease_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT gene_name FROM targets").fetchall()
    genes = [r[0] for r in rows if r[0]]
    conn.close()

    print(f"Searching ChEMBL for drugs related to targets: {genes} / disease: {disease_name}")
    molecule = new_client.molecule
    pains_filter = get_pains_filter()

    all_molecules = []

    # 1. 타겟별 ChEMBL 검색
    if genes:
        target_client = new_client.target
        for gene in genes:
            print(f"  Fetching drugs for target gene: {gene}")
            res_target = target_client.filter(
                target_components__accession__contains=gene
            ).only(['target_chembl_id'])
            for t in res_target:
                activities = new_client.activity.filter(
                    target_chembl_id=t['target_chembl_id'], pchembl_value__gte=5
                )
                m_ids = [a['molecule_chembl_id'] for a in activities[:50]]
                if m_ids:
                    mols = molecule.filter(
                        molecule_chembl_id__in=m_ids, molecule_type='Small molecule'
                    ).only(['molecule_chembl_id', 'pref_name', 'molecule_structures', 'molecule_properties'])
                    all_molecules.extend(list(mols))

    # 2. 질환 키워드 검색 (결과 부족 시)
    if len(all_molecules) < 10 and disease_name:
        print(f"  Searching ChEMBL by disease keyword: {disease_name}")
        res = molecule.filter(
            molecule_type='Small molecule', term=disease_name
        ).only(['molecule_chembl_id', 'pref_name', 'molecule_structures', 'molecule_properties'])
        all_molecules.extend(list(res[:100]))

    # 3. 폴백: FDA 승인 약물
    if not all_molecules:
        print("  No specific drugs found. Fetching general FDA-approved molecules...")
        res = molecule.filter(
            molecule_type='Small molecule', max_phase=4
        ).only(['molecule_chembl_id', 'pref_name', 'molecule_structures', 'molecule_properties'])
        all_molecules = list(res[:100])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    count = 0
    seen = set()

    for mol in tqdm(all_molecules, desc="Processing compounds"):
        chembl_id = mol['molecule_chembl_id']
        if chembl_id in seen:
            continue
        seen.add(chembl_id)

        name = mol.get('pref_name', '') or chembl_id
        smiles = (mol.get('molecule_structures') or {}).get('canonical_smiles', '')
        if not smiles:
            continue

        rdmol = Chem.MolFromSmiles(smiles)
        if rdmol is None:
            continue

        mw   = Descriptors.MolWt(rdmol)
        tpsa = Descriptors.TPSA(rdmol)
        hbd  = Descriptors.NumHDonors(rdmol)
        hba  = Descriptors.NumHAcceptors(rdmol)
        logp = Descriptors.MolLogP(rdmol)

        if 150 <= mw <= 600 and tpsa < 140 and hbd <= 5 and hba <= 10:
            cursor.execute("""
            INSERT OR IGNORE INTO compounds
                (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, max_phase, disease_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, 4, disease_id))
            count += 1
            if count >= 100:
                break

    conn.commit()
    conn.close()
    print(f"Saved {count} compounds (disease_id={disease_id}) to database.")


if __name__ == "__main__":
    disease = sys.argv[1] if len(sys.argv) > 1 else None
    db_file = os.path.join("data", "mg_discovery.db")
    fetch_drugs_for_targets(db_file, disease)
