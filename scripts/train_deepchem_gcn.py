import os
import sqlite3
import pandas as pd
import numpy as np
import deepchem as dc
from sklearn.metrics import mean_squared_error, r2_score

def train_deepchem_gcn(db_path, model_out_dir):
    print("Fetching docking results for DeepChem GCN training...")
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
        print("No docking data available.")
        return

    print(f"Loaded {len(df)} records. Applying ConvMolFeaturizer (Graph Features)...")

    # DeepChem MolGraph Featurizer (PyTorch)
    featurizer = dc.feat.MolGraphConvFeaturizer()
    features = featurizer.featurize(df['smiles'].tolist())
    
    # Filter out failures
    valid_indices = [i for i, f in enumerate(features) if f is not None]
    valid_features = features[valid_indices]
    valid_labels = df['vina_score'].iloc[valid_indices].values.reshape(-1, 1)

    print(f"Valid graph features generated for {len(valid_features)} compounds.")

    # Create DeepChem Dataset
    dataset = dc.data.NumpyDataset(X=valid_features, y=valid_labels)

    # Split dataset
    splitter = dc.splits.RandomSplitter()
    train_dataset, test_dataset = splitter.train_test_split(dataset, frac_train=0.85, seed=42)

    print(f"Training on {len(train_dataset)} samples, testing on {len(test_dataset)} samples.")

    # Define PyTorch GCN Model
    # Since Vina score is a continuous value (affinity), we use mode='regression'
    print("Building DeepChem GCNModel (PyTorch)...")
    model = dc.models.GCNModel(
        n_tasks=1,
        mode='regression',
        dropout=0.2,
        model_dir=os.path.join(model_out_dir, "gcn_model"),
        random_seed=42
    )

    # Train model
    print("Training GCN Model for 20 epochs...")
    model.fit(train_dataset, nb_epoch=20)
    
    # Evaluate
    print("Evaluating GCN Model...")
    
    train_preds = model.predict(train_dataset)
    test_preds = model.predict(test_dataset)
    
    train_r2 = r2_score(train_dataset.y, train_preds)
    test_r2 = r2_score(test_dataset.y, test_preds)
    test_mse = mean_squared_error(test_dataset.y, test_preds)
    
    print(f"Train R2 Score: {train_r2:.4f}")
    print(f"Test R2 Score: {test_r2:.4f}")
    print(f"Test MSE: {test_mse:.4f}")
    
    print(f"GCN Model saved to {os.path.join(model_out_dir, 'gcn_model')}")

if __name__ == "__main__":
    db_file = os.path.join("data", "mg_discovery.db")
    models_dir = "models"
    train_deepchem_gcn(db_file, models_dir)
