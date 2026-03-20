import os
import sqlite3
import pandas as pd
import numpy as np
import pickle
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def smiles_to_fp(smiles, radius=2, nBits=2048):
    """Convert SMILES to Morgan Fingerprint numpy array."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None: return None
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
        arr = np.zeros((0,), dtype=np.int8)
        Chem.DataStructs.ConvertToNumpyArray(fp, arr)
        return arr
    except:
        return None

def train_baseline_model(db_path, model_out_dir):
    print("Fetching all docking results for training...")
    conn = sqlite3.connect(db_path)
    query = """
    SELECT c.smiles, d.vina_score
    FROM docking_results d
    JOIN compounds c ON d.compound_id = c.id
    WHERE d.vina_score IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        print("No docking data available for training.")
        return

    print(f"Loaded {len(df)} records. Applying Morgan Fingerprints...")
    
    # Prepare features (X) and target (y)
    X_list = []
    y_list = []
    
    for _, row in df.iterrows():
        fp = smiles_to_fp(row['smiles'])
        if fp is not None:
            X_list.append(fp)
            y_list.append(row['vina_score'])

    X = np.array(X_list)
    y = np.array(y_list)
    
    print(f"Valid fingerprint generated for {len(X)} compounds.")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    
    # Train
    print("Training RandomForestRegressor Baseline Model...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = rf.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Model Evaluation -> MSE: {mse:.4f}, R2 Score: {r2:.4f}")
    
    # Save
    os.makedirs(model_out_dir, exist_ok=True)
    model_path = os.path.join(model_out_dir, "baseline_rf_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(rf, f)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    models_dir = "models"
    train_baseline_model(db_file, models_dir)
