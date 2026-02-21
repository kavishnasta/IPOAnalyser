import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
from pathlib import Path

script_dir = Path(__file__).parent
model_path = script_dir / 'ml_model.pkl'

def train_ipo_model(csv_path):
    df = pd.read_csv(csv_path)
    
    feature_columns = [
        'Issue_Size',
        'QIB_Subscription',
        'HNI_Subscription',
        'Retail_Subscription',
        'PE_Ratio',
        'OFS_Percentage',
        'GMP_Listing_Day'
    ]
    
    X = df[feature_columns].fillna(0)
    y = df['Positive_Listing_Gain'].astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to {model_path}")
    return model

if __name__ == '__main__':
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'ipo_data.csv'
    train_ipo_model(csv_path)
