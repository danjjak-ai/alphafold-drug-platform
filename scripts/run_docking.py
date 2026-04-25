import os
import sqlite3
import subprocess
import re
from multiprocessing import Pool
from tqdm import tqdm

def get_receptor_center(pdbqt_path):
    # Simple COM calculation from PDBQT
    coords = []
    with open(pdbqt_path, 'r') as f:
        for line in f:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append((x, y, z))
                except:
                    continue
    if not coords:
        return (0, 0, 0)
    avg_x = sum(c[0] for c in coords) / len(coords)
    avg_y = sum(c[1] for c in coords) / len(coords)
    avg_z = sum(c[2] for c in coords) / len(coords)
    return (avg_x, avg_y, avg_z)

def run_single_docking(args):
    vina_exe, receptor_path, ligand_path, out_dir, center, size, cp_id, tg_id, db_path = args
    chembl_id = os.path.splitext(os.path.basename(ligand_path))[0]
    target_name = os.path.splitext(os.path.basename(receptor_path))[0]
    
    out_pdbqt = os.path.join(out_dir, f"{target_name}_{chembl_id}_out.pdbqt")
    log_file = os.path.join(out_dir, f"{target_name}_{chembl_id}_log.txt")
    
    # Run Vina
    cmd = [
        vina_exe,
        "--receptor", receptor_path,
        "--ligand", ligand_path,
        "--center_x", str(center[0]),
        "--center_y", str(center[1]),
        "--center_z", str(center[2]),
        "--size_x", str(size[0]),
        "--size_y", str(size[1]),
        "--size_z", str(size[2]),
        "--out", out_pdbqt,
        "--cpu", "2" # 2 CPUs per dock
    ]
    
    try:
        with open(log_file, "w") as log:
            subprocess.run(cmd, stdout=log, stderr=subprocess.PIPE, check=True)
            
        # Parse best score from log or out_pdbqt
        # In PDBQT output, it looks like "REMARK VINA RESULT: -8.2"
        score = None
        if os.path.exists(out_pdbqt):
            with open(out_pdbqt, 'r') as f:
                for line in f:
                    if "REMARK VINA RESULT" in line:
                        match = re.search(r"RESULT:\s+([-+]?\d*\.\d+|\d+)", line)
                        if match:
                            score = float(match.group(1))
                            break
        
        if score is not None:
            # Save to DB
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO docking_results (compound_id, target_id, vina_score, pose_path)
            VALUES (?, ?, ?, ?)
            """, (cp_id, tg_id, score, out_pdbqt))
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        # print(f"Docking error {chembl_id} on {target_name}: {e}")
        pass
    return False

def run_docking_batch(db_path, vina_exe, disease_name=None):
    results_dir = os.path.join("results", "docking")
    os.makedirs(results_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    disease_id = None
    if disease_name:
        row = cursor.execute("SELECT id FROM diseases WHERE name = ?", (disease_name,)).fetchone()
        if row:
            disease_id = row[0]
            print(f"[INFO] Filtering by disease: {disease_name} (id={disease_id})")
        else:
            print(f"[WARN] Disease '{disease_name}' not found. Processing all records.")

    # Get targets (filter by disease if possible)
    if disease_id:
        cursor.execute("SELECT id, gene_name, structure_path FROM targets WHERE disease_id = ?", (disease_id,))
    else:
        cursor.execute("SELECT id, gene_name, structure_path FROM targets")
    targets = cursor.fetchall()
    
    # Get compounds (filter by disease if possible)
    if disease_id:
        cursor.execute("SELECT id, chembl_id FROM compounds WHERE disease_id = ?", (disease_id,))
    else:
        cursor.execute("SELECT id, chembl_id FROM compounds")
    compounds = cursor.fetchall()
    conn.close()
    
    if not targets or not compounds:
        print("[WARN] No targets or compounds found for processing.")
        return

    # Pre-calculate centers
    target_info = []
    for tg_id, gene_name, structure_path in targets:
        path = structure_path
        if not path or not os.path.exists(path):
            if gene_name:
                path = os.path.join("data", "structures", "targets", f"{gene_name.lower()}.pdbqt")
        
        if path and os.path.exists(path):
            center = get_receptor_center(path)
            target_info.append((tg_id, path, center))

    # Task list (Target x Compound)
    tasks = []
    for tg_id, tg_path, center in target_info:
        for cp_id, chembl_id in compounds:
            lig_path = os.path.join("data", "structures", "ligands", f"{chembl_id}.pdbqt")
            if os.path.exists(lig_path):
                tasks.append((vina_exe, tg_path, lig_path, results_dir, center, (40, 40, 40), cp_id, tg_id, db_path))
    
    if not tasks:
        print("[WARN] No docking tasks generated (check if .pdbqt files exist in data/structures/)")
        return

    print(f"Starting {len(tasks)} docking tasks for {disease_name if disease_name else 'all diseases'}...")
    with Pool(4) as p:
        list(tqdm(p.imap(run_single_docking, tasks), total=len(tasks)))

if __name__ == "__main__":
    import sys
    db_file = os.path.join("data", "mg_discovery.db")
    disease = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Vina path handle
    v_path = "scripts/vina.exe"
    if not os.path.exists(v_path):
        v_path = "vina" # assume in PATH (for colab/linux)
        
    run_docking_batch(db_file, v_path, disease)

