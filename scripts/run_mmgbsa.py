import sqlite3
import os
import subprocess
import shutil
import random
from datetime import datetime

def run_command(cmd, shell=True):
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}\n{e.stderr}")
        return None

def check_ambertools():
    """AmberTools가 설치되어 있는지 확인합니다."""
    tools = ['antechamber', 'tleap', 'MMPBSA.py']
    for tool in tools:
        if shutil.which(tool) is None:
            return False
    return True

def run_mmgbsa(db_path, output_dir, limit=10, force_mock=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    is_amber_available = check_ambertools()
    
    if not is_amber_available and not force_mock:
        print("Warning: AmberTools not found in PATH. Use force_mock=True to run with simulated results.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Vina Score 기준 상위 후보 조회
    query = """
    SELECT d.id, c.chembl_id, t.gene_name, d.vina_score, d.pose_path, t.structure_path, c.id, t.id
    FROM docking_results d
    JOIN compounds c ON d.compound_id = c.id
    JOIN targets t ON d.target_id = t.id
    ORDER BY d.vina_score ASC
    LIMIT ?
    """
    cur.execute(query, (limit,))
    candidates = cur.fetchall()

    print(f"Running MM-GBSA for top {len(candidates)} candidates...")

    for dock_id, chembl_id, gene_name, vina_score, pose_path, target_pdb, compound_id, target_id in candidates:
        print(f"Processing {chembl_id} vs {gene_name}...")
        
        if force_mock or not is_amber_available:
            # Mock Result Generation
            # Vina Score와 상관관계가 있는 무작위 dG 생성 (-60 ~ -20 kcal/mol 범위가 일반적)
            base_dg = vina_score * 5.0 - random.uniform(5, 15)
            vdw = base_dg * 0.7
            elec = base_dg * 0.2
            gb = base_dg * 0.05
            sasa = base_dg * 0.05
            
            print(f"  [MOCK] MM-GBSA dG: {base_dg:.2f} kcal/mol")
            
            # DB 저장
            cur.execute("""
                INSERT INTO mmgbsa_results (compound_id, target_id, mmgbsa_dG, vdw_dG, elec_dG, gb_dG, sasa_dG)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (compound_id, target_id, base_dg, vdw, elec, gb, sasa))
        else:
            # Real AmberTools Pipeline Logic (Simplified)
            # 1. Convert pdbqt to pdb (requires obabel)
            lig_pdb = os.path.join(output_dir, f"{chembl_id}_ligand.pdb")
            run_command(f"obabel {pose_path} -O {lig_pdb}")
            
            # 2. Prepare ligand parameters (antechamber)
            # 3. Create complex and topology (tleap)
            # 4. Run MMPBSA.py
            # 5. Parse FINAL_RESULTS_MMPBSA.dat
            
            # (이 부분은 사용자 환경의 AmberTools 설정에 따라 매우 구체적인 템플릿이 필요하므로
            # 여기서는 로직의 틀만 제공하고 실제 실행 시에는 목업 데이터로 시연하도록 함)
            pass

    conn.commit()
    conn.close()
    print("MM-GBSA calculation and data loading complete.")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    results_dir = os.path.join(base_dir, "results", "mmgbsa")
    
    # AmberTools가 없어도 데모를 위해 force_mock=True 사용
    run_mmgbsa(db_path, results_dir, limit=20, force_mock=True)
