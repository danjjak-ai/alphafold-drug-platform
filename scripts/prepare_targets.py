import requests
import os
import sys
import sqlite3
import numpy as np
from rdkit import Chem

# ─────────────────────────────────────────────────────
# AlphaFold 예측 구조 우선 사용 헬퍼
# ─────────────────────────────────────────────────────
PREDICTED_DIR = os.path.join("data", "structures", "predicted")

def get_best_pdb_path(gene_name: str, fallback_rcsb_path: str) -> tuple[str, str]:
    """
    AlphaFold DB 예측 구조가 있으면 우선 사용하고,
    없으면 RCSB 실험 구조로 폴백한다.

    반환값: (사용할 pdb 경로, 출처 문자열)
    """
    predicted_pdb = os.path.join(PREDICTED_DIR, f"{gene_name.lower()}_alphafold.pdb")
    if os.path.exists(predicted_pdb):
        print(f"  [구조 출처] AlphaFold DB 예측 구조 사용: {predicted_pdb}")
        return predicted_pdb, "alphafold_db"
    print(f"  [구조 출처] RCSB 실험 구조 사용: {fallback_rcsb_path}")
    return fallback_rcsb_path, "rcsb_pdb"

def update_structure_source(db_path: str, gene_name: str, source: str, pdbqt_path: str):
    """targets 테이블의 structure_source와 structure_path를 갱신한다."""
    if not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        # structure_source 컬럼이 없으면 추가 (마이그레이션)
        existing = {r[1] for r in conn.execute("PRAGMA table_info(targets)").fetchall()}
        if "structure_source" not in existing:
            conn.execute("ALTER TABLE targets ADD COLUMN structure_source TEXT DEFAULT 'rcsb_pdb'")
        conn.execute(
            "UPDATE targets SET structure_path = ?, structure_source = ? WHERE gene_name = ?",
            (pdbqt_path, source, gene_name)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [DB 갱신 오류] {e}")

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
    db_path = os.path.join("data", "mg_discovery.db")

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Please run fetch_targets.py first.")
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT gene_name, pdb_id FROM targets")
        db_targets = cursor.fetchall()
        conn.close()

        for gene_name, pdb_id in db_targets:
            if not gene_name:
                continue
                
            print(f"\nProcessing target: {gene_name}...")
            pdb_path, src = get_best_pdb_path(
                gene_name,
                fallback_rcsb_path=os.path.join(targets_out_dir, f"{gene_name.lower()}_raw.pdb")
            )
            
            if src == "rcsb_pdb" and not os.path.exists(pdb_path):
                if pdb_id:
                    print(f"  Downloading PDB {pdb_id} for {gene_name}...")
                    download_pdb(pdb_id, pdb_path)
                else:
                    print(f"  [Warning] No PDB ID found for {gene_name} and no predicted structure available.")
                    continue
            
            if not os.path.exists(pdb_path):
                print(f"  [Error] PDB file not found: {pdb_path}")
                continue

            pdbqt_out = os.path.join(targets_out_dir, f"{gene_name.lower()}.pdbqt")
            
            # Use all chains to ensure dynamic compatibility with any new target
            ok = process_target(pdb_path, pdbqt_out, chain_ids=None)
            if ok:
                update_structure_source(db_path, gene_name, src, pdbqt_out)
                print(f"  Target {gene_name} prepared successfully.")

    print("\nTarget preparation complete.")


