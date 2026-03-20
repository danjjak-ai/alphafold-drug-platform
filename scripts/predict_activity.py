import sqlite3
import joblib
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
import os
from tqdm import tqdm

def get_fingerprint(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)

def run_predictions(db_path, model_path):
    print("Loading Baseline AI Model...")
    if not os.path.exists(model_path):
        print("Model not found! Run train_ai_model.py first.")
        return
        
    model = joblib.load(model_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Needs target ids for CHRNA1 and MUSK
    cursor.execute("SELECT id, gene_name FROM targets")
    targets = cursor.fetchall()
    
    cursor.execute("SELECT id, chembl_id, smiles FROM compounds")
    compounds = cursor.fetchall()
    
    print(f"Predicting AI Activity for {len(compounds)} compounds...")
    
    predictions_to_insert = []
    
    for cp_id, chembl_id, smiles in tqdm(compounds):
        fp = get_fingerprint(smiles)
        if fp is None:
            continue
            
        X = np.array(list(fp)).reshape(1, -1)
        # Because our baseline model is naive (target-agnostic), 
        # we predict the same pChEMBL for all active targets just to populate the DB.
        try:
            pred_pchembl = float(model.predict(X)[0])
            # pseudo-probability (sigmoid of centered pchembl around 6.0)
            activation_prob = 1 / (1 + np.exp(-(pred_pchembl - 6.0)))
            
            for tg_id, tg_name in targets:
                predictions_to_insert.append((
                    cp_id, tg_id, 'RandomForest_Baseline', 
                    activation_prob, pred_pchembl, 0.70 # mock confidence
                ))
        except:
            pass
            
    # Insert
    cursor.executemany("""
    INSERT INTO activity_predictions 
    (compound_id, target_id, model_type, activation_prob, binding_stability_score, confidence)
    VALUES (?, ?, ?, ?, ?, ?)
    """, predictions_to_insert)
    
    conn.commit()
    conn.close()
    print("Successfully populated AI predictions.")

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    model_file = os.path.join("models", "ai_baseline_model.pkl")
    run_predictions(db_file, model_file)
