import requests
import os
import numpy as np
from rdkit import Chem

def download_pdb(pdb_id, output_path):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        return True
    return False

def save_receptor_pdbqt(mol, output_path):
    # Simple manual PDBQT writer for rigid receptors
    conf = mol.GetConformer()
    with open(output_path, "w", encoding="utf-8") as f:
        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            pos = conf.GetAtomPosition(idx)
            info = atom.GetPDBResidueInfo()
            
            name = info.GetName() if info else f" {atom.GetSymbol():<3}"
            res_name = info.GetResidueName() if info else "UNK"
            chain = info.GetChainId() if info else "A"
            res_num = info.GetResidueNumber() if info else 1
            symbol = atom.GetSymbol().upper()
            
            # Map symbol to AutoDock types
            ad_type = symbol
            if symbol == "H":
                neighbors = atom.GetNeighbors()
                if neighbors and neighbors[0].GetSymbol() in ["O", "N", "S"]:
                    ad_type = "HD"
                else:
                    ad_type = "H"
            elif symbol == "O": ad_type = "OA"
            elif symbol == "N": ad_type = "NA"
            
            # ATOM card format
            line = f"ATOM  {idx+1:>5} {name:<4} {res_name:>3} {chain}{res_num:>4}    "
            line += f"{pos.x:>8.3f}{pos.y:>8.3f}{pos.z:>8.3f}"
            line += f"  1.00  0.00    +0.000 {ad_type:<2}\n"
            f.write(line)
        f.write("TER\n")
    return True

def process_target(pdb_raw, pdbqt_out, chain_ids=None):
    mol = Chem.MolFromPDBFile(pdb_raw, removeHs=False)
    if mol is None:
        return False
    
    if chain_ids:
        rw_mol = Chem.RWMol(mol)
        for atom in reversed(range(rw_mol.GetNumAtoms())):
            res_info = rw_mol.GetAtomWithIdx(atom).GetPDBResidueInfo()
            if res_info is None or res_info.GetChainId().strip() not in chain_ids:
                rw_mol.RemoveAtom(atom)
        mol = rw_mol.GetMol()

    # Add Hs
    mol = Chem.AddHs(mol, addCoords=True)
    
    # Calculate Center
    conf = mol.GetConformer()
    pts = conf.GetPositions()
    center = pts.mean(axis=0)
    print(f"Receptor {pdbqt_out} Center: {center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}")
    
    return save_receptor_pdbqt(mol, pdbqt_out)

if __name__ == "__main__":
    targets_out_dir = os.path.join("data", "structures", "targets")
    os.makedirs(targets_out_dir, exist_ok=True)
    
    print("Preparing CHRNA1 receptor (7QL6)...")
    if not os.path.exists("data/structures/targets/7ql6_raw.pdb"):
        download_pdb("7QL6", "data/structures/targets/7ql6_raw.pdb")
    process_target("data/structures/targets/7ql6_raw.pdb", "data/structures/targets/chrna1.pdbqt", chain_ids=['A', 'D'])
    
    print("Preparing MuSK and LRP4 receptors (8S9P)...")
    if not os.path.exists("data/structures/targets/8s9p_raw.pdb"):
        download_pdb("8S9P", "data/structures/targets/8s9p_raw.pdb")
    process_target("data/structures/targets/8s9p_raw.pdb", "data/structures/targets/musk.pdbqt", chain_ids=['C'])
    process_target("data/structures/targets/8s9p_raw.pdb", "data/structures/targets/lrp4.pdbqt", chain_ids=['B'])
    
    print("Target preparation complete.")
