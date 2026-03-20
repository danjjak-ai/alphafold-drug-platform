import pandas as pd
import numpy as np
import os
import joblib
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def get_fingerprint(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)

def convert_to_p_value(row):
    # Standard units can be 'nM', 'uM', 'M', 'mM'
    val = row['standard_value']
    unit = str(row['standard_units']).lower()
    
    if val <= 0: return np.nan
    
    if unit == 'nm': val_m = val * 1e-9
    elif unit == 'um': val_m = val * 1e-6
    elif unit == 'mm': val_m = val * 1e-3
    elif unit == 'm': val_m = val
    else: val_m = val * 1e-9 # Fallback to nM
    
    return -np.log10(val_m)

def train_model(data_path, model_path):
    df = pd.read_csv(data_path)
    
    # 1. Standardize Activity (pChEMBL)
    df['p_chembl'] = df.apply(convert_to_p_value, axis=1)
    df = df.dropna(subset=['p_chembl', 'canonical_smiles'])
    
    print(f"Final training records: {len(df)}")
    
    # 2. Featurization (X)
    X = []
    y = []
    for idx, row in df.iterrows():
        fp = get_fingerprint(row['canonical_smiles'])
        if fp:
            X.append(list(fp))
            y.append(row['p_chembl'])
    
    X = np.array(X)
    y = np.array(y)
    
    # 3. Model Building
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Baseline...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 4. Evaluation
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Model MSE: {mse:.4f}")
    print(f"Model R2: {r2:.4f}")
    
    # 5. Save Model
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    data_file = "data/processed/chembl_training_data.csv"
    model_file = "models/ai_baseline_model.pkl"
    os.makedirs("models", exist_ok=True)
    
    if os.path.exists(data_file):
        train_model(data_file, model_file)
    else:
        print("Training data not found.")
