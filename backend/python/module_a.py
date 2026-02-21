import sys
import json
import pickle
import numpy as np
from pathlib import Path

script_dir = Path(__file__).parent
model_path = script_dir / 'ml_model.pkl'

def load_model():
    if model_path.exists():
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    return None

def predict_ipo_success(input_data):
    model = load_model()
    if model is None:
        return {
            "probability": 0.5,
            "riskScore": 0.5,
            "error": "Model not trained yet"
        }
    
    try:
        data = json.loads(input_data)
        
        issue_size = data.get('issueSize', 0)
        qib_subscription = data.get('qibSubscription', 1.0)
        hni_subscription = data.get('hniSubscription', 1.0)
        retail_subscription = data.get('retailSubscription', 1.0)
        pe_ratio = data.get('peRatio', 20.0)
        ofs_percentage = data.get('ofsPercentage', 0.5)
        gmp_listing_day = data.get('gmpListingDay', 0)
        
        features = np.array([[
            issue_size,
            qib_subscription,
            hni_subscription,
            retail_subscription,
            pe_ratio,
            ofs_percentage,
            gmp_listing_day
        ]])
        
        probability = model.predict_proba(features)[0][1]
        risk_score = 1 - probability
        
        return {
            "probability": float(probability),
            "riskScore": float(risk_score)
        }
    except Exception as e:
        pass
    
    return {
        "probability": 0.5,
        "riskScore": 0.5
    }

if __name__ == '__main__':
    input_data = sys.argv[1] if len(sys.argv) > 1 else '{}'
    result = predict_ipo_success(input_data)
    print(json.dumps(result))
