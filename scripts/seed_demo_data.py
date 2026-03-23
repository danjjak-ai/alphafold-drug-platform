"""
seed_demo_data.py
Cloud Run 환경에서 데모용 샘플 데이터를 DB에 삽입하고 3D 구조 파일을 배치합니다.
실제 FDA 승인 약물 10개 + 3개 MG 타깃 + 도킹 결과 시뮬레이션 데이터.
"""
import sqlite3
import os
import random
import shutil

DEMO_COMPOUNDS = [
    ("CHEMBL21333", "Pyridostigmine",      "CC(=O)OC1=CC=[N+](C)C=C1", 180.2, 0.5, 41.1, 1, 4, 4),
    ("CHEMBL1200640","Edrophonium",         "CC[N+](C)(C)c1ccc(O)cc1", 165.2, 0.8, 37.3, 1, 2, 4),
    ("CHEMBL703",   "Neostigmine",          "CN(C)C(=O)Oc1cccc([N+](C)(C)C)c1", 223.3, 1.1, 29.5, 0, 3, 4),
    ("CHEMBL25",    "Prednisone",           "CC12CCC(=O)C=C1CCC3C2CCC4(C)C3CC(=O)C4=O", 358.4, 1.5, 93.1, 1, 5, 4),
    ("CHEMBL112",   "Cyclosporine",         "CCC1NC(=O)C(CC2=CC=CC=C2)N(C)C(=O)CN(C)C(=O)C(C(C)C)NC(=O)C(C(C)C)N(C)C(=O)C(CC(C)C)NC(=O)C(CCCCCC)NC(=O)C(CC(C)C)N(C)C1=O", 1202.6, 2.8, 278.8, 4, 14, 4),
    ("CHEMBL83",    "Tacrolimus",           "CCC1OC(=O)C2CCCCN2C(=O)C(=O)C(CC(=O)C(CC1=O)O)CC1CCC(=O)C(OC)C1", 804.0, 3.1, 178.4, 3, 12, 4),
    ("CHEMBL703285","Rituximab-small",      "CC(C)CC1=CC=CC=C1", 134.2, 4.8, 0.0, 0, 0, 4),
    ("CHEMBL1231",  "Azathioprine",         "CNc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)O)[C@@H](O)[C@H]1O", 277.3, -1.2, 143.6, 4, 9, 4),
    ("CHEMBL998",   "Methotrexate",         "CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(CC(=O)[O-])cc1", 454.4, -1.8, 210.3, 4, 8, 4),
    ("CHEMBL1128",  "Eculizumab-proxy",     "c1ccc(-c2ccccc2)cc1", 154.2, 3.5, 0.0, 0, 0, 4),
]

DEMO_VINA_SCORES = {
    "CHEMBL21333":   (-9.4, -8.1, -7.3),
    "CHEMBL1200640": (-8.8, -7.5, -6.9),
    "CHEMBL703":     (-8.2, -7.0, -6.5),
    "CHEMBL25":      (-7.9, -8.3, -7.1),
    "CHEMBL112":     (-7.5, -6.8, -7.2),
    "CHEMBL83":      (-8.1, -7.6, -8.0),
    "CHEMBL703285":  (-6.3, -5.9, -6.1),
    "CHEMBL1231":    (-7.2, -6.9, -7.5),
    "CHEMBL998":     (-7.8, -7.1, -6.8),
    "CHEMBL1128":    (-6.8, -6.4, -6.9),
}

DEMO_TARGETS = [
    ("P02708", "CHRNA1", "7QL6", "data/structures/targets/7ql6_raw.pdb"),
    ("O15146", "MUSK",   "8S9P", "data/structures/targets/8s9p_raw.pdb"),
    ("O75096", "LRP4",   "8S9P", "data/structures/targets/8s9p_raw.pdb"),
]

def seed(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uniprot_id TEXT NOT NULL UNIQUE,
        gene_name TEXT,
        sequence TEXT,
        pdb_id TEXT,
        structure_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS compounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chembl_id TEXT UNIQUE,
        name TEXT,
        smiles TEXT,
        inchikey TEXT,
        mw REAL,
        logp REAL,
        tpsa REAL,
        hbd INTEGER,
        hba INTEGER,
        max_phase INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS docking_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id INTEGER,
        target_id INTEGER,
        vina_score REAL,
        rmsd_lb REAL,
        rmsd_ub REAL,
        pose_path TEXT,
        run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (compound_id) REFERENCES compounds(id),
        FOREIGN KEY (target_id) REFERENCES targets(id)
    );
    """)
    conn.commit()

    # Seeding targets
    cur.execute("DELETE FROM targets")
    for uniprot, gene, pdb, path in DEMO_TARGETS:
        cur.execute(
            "INSERT OR IGNORE INTO targets (uniprot_id, gene_name, pdb_id, structure_path) VALUES (?,?,?,?)",
            (uniprot, gene, pdb, path)
        )
    conn.commit()
    target_ids = {row[1]: row[0] for row in cur.execute("SELECT id, gene_name FROM targets")}

    # Seeding compounds
    cur.execute("DELETE FROM compounds")
    compound_ids = {}
    for chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, max_phase in DEMO_COMPOUNDS:
        cur.execute(
            "INSERT OR IGNORE INTO compounds (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, max_phase) VALUES (?,?,?,?,?,?,?,?,?)",
            (chembl_id, name, smiles, mw, logp, tpsa, hbd, hba, max_phase)
        )
        cur.execute("SELECT id FROM compounds WHERE chembl_id=?", (chembl_id,))
        compound_ids[chembl_id] = cur.fetchone()[0]
    conn.commit()

    # Seeding docking results & creating mock 3D files
    results_dir = os.path.join("results", "docking")
    os.makedirs(results_dir, exist_ok=True)
    
    rng = random.Random(42)
    targets_list = ["CHRNA1", "MUSK", "LRP4"]
    cur.execute("DELETE FROM docking_results")
    for chembl_id, vina_tuple in DEMO_VINA_SCORES.items():
        cid = compound_ids.get(chembl_id)
        if not cid: continue
        for i, gene in enumerate(targets_list):
            tid = target_ids.get(gene)
            if not tid: continue
            
            vina = float(vina_tuple[i]) + rng.uniform(-0.3, 0.3)
            # Use fixed naming convention for app.py to find it
            pose_path = os.path.join("results", "docking", f"{gene.lower()}_{chembl_id}_out.pdbqt")
            
            cur.execute(
                "INSERT INTO docking_results (compound_id, target_id, vina_score, rmsd_lb, rmsd_ub, pose_path) VALUES (?,?,?,?,?,?)",
                (cid, tid, float(round(vina, 2)), 0.5, 2.0, pose_path)
            )
            
            # Create a mock pdbqt content
            with open(pose_path, "w") as f:
                f.write(f"REMARK  VINA RESULT: {vina:.1f} kcal/mol\n")
                f.write("ATOM      1  N   ASP A   1      25.109  14.654  32.887  1.00  0.00           N\n")
                f.write("END\n")

    # Ensure target PDBs are available
    target_pdb_dir = os.path.join("data", "structures", "targets")
    os.makedirs(target_pdb_dir, exist_ok=True)
    for _, gene, _, _ in DEMO_TARGETS:
        filename = "7ql6_raw.pdb" if gene == "CHRNA1" else "8s9p_raw.pdb"
        dest_path = os.path.join(target_pdb_dir, filename)
        if not os.path.exists(dest_path):
            with open(dest_path, "w") as f:
                f.write(f"REMARK MOCK PDB FOR {gene}\n")
                f.write("ATOM      1  CA  GLY A   1       0.000   0.000   0.000  1.00  0.00           C\n")
                f.write("END\n")

    conn.commit()
    conn.close()
    print(f"[seed_demo_data] Seeding complete. 3D files generated in {results_dir}")

if __name__ == "__main__":
    seed(os.path.join("data", "mg_discovery.db"))
