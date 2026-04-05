import pickle
import numpy as np
import os

# ─────────────────────────────────────────────
# Load all saved model files
# ─────────────────────────────────────────────
BASE = os.path.dirname(__file__)

with open(os.path.join(BASE, 'le_city.pkl'), 'rb') as f:
    le_city = pickle.load(f)

with open(os.path.join(BASE, 'le_bhk.pkl'), 'rb') as f:
    le_bhk = pickle.load(f)

with open(os.path.join(BASE, 'le_type.pkl'), 'rb') as f:
    le_type = pickle.load(f)

with open(os.path.join(BASE, 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

with open(os.path.join(BASE, 'similarity_matrix.pkl'), 'rb') as f:
    similarity_matrix = pickle.load(f)

with open(os.path.join(BASE, 'feature_matrix.pkl'), 'rb') as f:
    feature_matrix = pickle.load(f)

import pandas as pd
df = pd.read_pickle(os.path.join(BASE, 'properties_df.pkl'))

# ─────────────────────────────────────────────
# Valid Options (for frontend dropdowns)
# ─────────────────────────────────────────────
VALID_CITIES = list(le_city.classes_)      # ['Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Mumbai']
VALID_BHK    = list(le_bhk.classes_)       # ['1 BHK', '2 BHK', '3 BHK', 'Plot', 'Studio']
VALID_TYPES  = list(le_type.classes_)      # ['Apartment', 'Independent House', 'Plot', 'Villa']


# ─────────────────────────────────────────────
# Main Recommend Function
# ─────────────────────────────────────────────
def get_recommendations(city, bhk, prop_type, budget, top_n=3):
    """
    Returns top N property recommendations as a list of dicts.

    Args:
        city      (str): e.g. 'Mumbai', 'Bangalore', 'Chennai', 'Delhi', 'Hyderabad'
        bhk       (str): e.g. '1 BHK', '2 BHK', '3 BHK', 'Studio', 'Plot'
        prop_type (str): e.g. 'Apartment', 'Villa', 'Independent House', 'Plot'
        budget    (float): Price in Lakhs e.g. 80
        top_n     (int): Number of results to return (default 3)

    Returns:
        list of dicts with property details + match_score
    """

    # Safe encode — fallback to 0 if unknown value
    city_enc  = int(le_city.transform([city])[0])     if city      in le_city.classes_      else 0
    bhk_enc   = int(le_bhk.transform([bhk])[0])       if bhk       in le_bhk.classes_       else 0
    type_enc  = int(le_type.transform([prop_type])[0]) if prop_type in le_type.classes_     else 0

    # Build user input vector
    user_vector = np.array([[city_enc, bhk_enc, type_enc, float(budget), 0, 0]])

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        user_scaled = scaler.transform(user_vector)

    # Compute similarity scores against all properties
    from sklearn.metrics.pairwise import cosine_similarity
    scores = cosine_similarity(user_scaled, feature_matrix)[0]

    # Get top N
    top_idx = np.argsort(scores)[::-1][:top_n]
    top_props = df.iloc[top_idx].copy()
    top_props['match_score'] = (scores[top_idx] * 100).round(1)

    # Return as list of dicts (JSON serializable)
    results = []
    for _, row in top_props.iterrows():
        results.append({
            'id':          int(row['id']),
            'title':       row['title'],
            'city':        row['city'],
            'location':    row['location'],
            'bhk':         row['bhk'],
            'type':        row['type'],
            'price':       row['price_value'],
            'area':        row['area'],
            'image':       row['image'],
            'match_score': row['match_score'],
        })

    return results


# ─────────────────────────────────────────────
# Quick test when run directly
# ─────────────────────────────────────────────
if __name__ == '__main__':
    test = get_recommendations(
        city='Mumbai',
        bhk='2 BHK',
        prop_type='Apartment',
        budget=80
    )
    for r in test:
        print(f"✅ {r['title']} | {r['city']} | ₹{r['price']}L | Score: {r['match_score']}%")
