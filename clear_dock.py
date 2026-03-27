import sqlite3
import os

db_path = "data/mg_discovery.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get compound IDs
res = cur.execute("SELECT id FROM compounds WHERE chembl_id IN ('CHEMBL21333','CHEMBL703','CHEMBL1200640')").fetchall()
ids = [str(r[0]) for r in res]

print("Deleting old docking results for compound IDs:", ids)

if ids:
    id_list = ",".join(ids)
    cur.execute(f"DELETE FROM docking_results WHERE compound_id IN ({id_list})")
    conn.commit()

print("Done.")
conn.close()
