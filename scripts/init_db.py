import sqlite3
import os

def init_db(db_path):
    print(f"Initializing database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables based on plan.md 0.1
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uniprot_id TEXT NOT NULL,
        gene_name TEXT,
        sequence TEXT,
        pdb_id TEXT,
        structure_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chembl_id TEXT,
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
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS docking_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id INTEGER,
        target_id INTEGER,
        vina_score REAL,
        rmsd_lb REAL,
        rmsd_ub REAL,
        pose_path TEXT,
        run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id) REFERENCES targets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admet_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id INTEGER,
        bbb_permeable BOOLEAN,
        cyp3a4_inhibitor BOOLEAN,
        herg_ic50_pred REAL,
        dili_risk TEXT,
        oral_bioavailability REAL,
        pains_flag BOOLEAN,
        FOREIGN KEY (compound_id) REFERENCES compounds (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id INTEGER,
        target_id INTEGER,
        model_type TEXT,
        activation_prob REAL,
        binding_stability_score REAL,
        confidence REAL,
        run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id) REFERENCES targets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validation_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id INTEGER,
        target_id INTEGER,
        assay_type TEXT,
        result TEXT,
        source TEXT,
        notes TEXT,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id) REFERENCES targets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mmgbsa_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id INTEGER,
        target_id INTEGER,
        mmgbsa_dG REAL,
        vdw_dG REAL,
        elec_dG REAL,
        gb_dG REAL,
        sasa_dG REAL,
        run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id) REFERENCES targets (id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    init_db(db_file)
