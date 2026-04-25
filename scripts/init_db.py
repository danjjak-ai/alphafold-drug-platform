import sqlite3
import os

def init_db(db_path):
    print(f"Initializing database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── diseases 테이블: 시스템 전역 키 ───────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diseases (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT    NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ── targets 테이블 ────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        uniprot_id    TEXT NOT NULL,
        gene_name     TEXT,
        sequence      TEXT,
        pdb_id        TEXT,
        structure_path TEXT,
        disease_id    INTEGER REFERENCES diseases(id),
        created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ── compounds 테이블 ─────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compounds (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        chembl_id  TEXT,
        name       TEXT,
        smiles     TEXT,
        inchikey   TEXT,
        mw         REAL,
        logp       REAL,
        tpsa       REAL,
        hbd        INTEGER,
        hba        INTEGER,
        max_phase  INTEGER,
        disease_id INTEGER REFERENCES diseases(id),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS docking_results (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id   INTEGER,
        target_id     INTEGER,
        vina_score    REAL,
        rmsd_lb       REAL,
        rmsd_ub       REAL,
        pose_path     TEXT,
        run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id)   REFERENCES targets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admet_results (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id        INTEGER,
        bbb_permeable      BOOLEAN,
        cyp3a4_inhibitor   BOOLEAN,
        herg_ic50_pred     REAL,
        dili_risk          TEXT,
        oral_bioavailability REAL,
        pains_flag         BOOLEAN,
        FOREIGN KEY (compound_id) REFERENCES compounds (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_predictions (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id           INTEGER,
        target_id             INTEGER,
        model_type            TEXT,
        activation_prob       REAL,
        binding_stability_score REAL,
        confidence            REAL,
        run_timestamp         DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id)   REFERENCES targets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validation_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id INTEGER,
        target_id   INTEGER,
        assay_type  TEXT,
        result      TEXT,
        source      TEXT,
        notes       TEXT,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id)   REFERENCES targets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mmgbsa_results (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        compound_id   INTEGER,
        target_id     INTEGER,
        mmgbsa_score  REAL,
        mmgbsa_dG     REAL,
        vdw_dG        REAL,
        elec_dG       REAL,
        gb_dG         REAL,
        sasa_dG       REAL,
        run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (compound_id) REFERENCES compounds (id),
        FOREIGN KEY (target_id)   REFERENCES targets (id)
    )
    """)

    # ── 마이그레이션: 기존 테이블에 disease_id 컬럼 추가 ──────────
    _migrate_add_column(cursor, "targets",   "disease_id", "INTEGER REFERENCES diseases(id)")
    _migrate_add_column(cursor, "compounds", "disease_id", "INTEGER REFERENCES diseases(id)")
    _migrate_add_column(cursor, "mmgbsa_results", "mmgbsa_score", "REAL")

    conn.commit()
    conn.close()
    print("Database initialization complete.")


def _migrate_add_column(cursor, table, column, col_def):
    """컬럼이 없으면 추가 (안전한 마이그레이션)"""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
        print(f"  [migrate] Added column '{column}' to '{table}'")
    except Exception:
        pass  # 이미 존재하면 무시


if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    init_db(db_file)
