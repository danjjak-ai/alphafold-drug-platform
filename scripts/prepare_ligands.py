import sqlite3
import os
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation
from tqdm import tqdm

def prepare_ligands(db_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, chembl_id, smiles FROM compounds")
    compounds = cursor.fetchall()

    print(f"Preparing 3D conformers and PDBQT for {len(compounds)} compounds...")
    preparer = MoleculePreparation()

    for cp_id, chembl_id, smiles in tqdm(compounds):
        out_file = os.path.join(output_dir, f"{chembl_id}.pdbqt")
        if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
            continue

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            continue

        # Add Hydrogens
        mol = Chem.AddHs(mol)

        # Generate 3D Conformer
        res = AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        if res == -1:
            res = AllChem.EmbedMolecule(mol, useRandomCoords=True)

        if res == -1:
            continue

        # Energy Minimization
        try:
            AllChem.MMFFOptimizeMolecule(mol)
        except:
            pass

        # Convert to PDBQT via Meeko (0.7.1 API)
        try:
            preparer.prepare(mol)
            pdbqt_string = preparer.write_pdbqt_string()
            with open(out_file, "w") as f:
                f.write(pdbqt_string)
        except Exception as e:
            # print(f"Error {chembl_id}: {e}")
            pass

    conn.close()
    print("Ligand preparation complete.")

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    ligands_dir = os.path.join("data", "structures", "ligands")
    prepare_ligands(db_file, ligands_dir)
