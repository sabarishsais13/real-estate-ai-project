import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

# ─────────────────────────────────────────────
# STEP 1: Load data from SQLite
# ─────────────────────────────────────────────
print("📦 Loading data from db.sqlite3 ...")

conn = sqlite3.connect('/mnt/user-data/uploads/db.sqlite3')
df = pd.read_sql_query(
    "SELECT id, title, location, price_value, bhk, type, area, floor, city, badge, image FROM listings_property WHERE is_active=1",
    conn
)
conn.close()

print(f"✅ Loaded {len(df)} properties\n")
print(df[['title', 'city', 'bhk', 'type', 'price_value', 'area']].to_string())

# ─────────────────────────────────────────────
# STEP 2: Clean & Preprocess
# ─────────────────────────────────────────────
print("\n🔧 Preprocessing ...")

# Extract numeric area (e.g. '550 sq.ft' → 550)
df['area_num'] = df['area'].str.extract(r'(\d+)').astype(float)

# Fill missing price
df['price_value'] = df['price_value'].fillna(df['price_value'].median())

# Clean floor - convert G, G+1 → 0, 1
def clean_floor(f):
    if f is None: return 0
    f = str(f).strip().upper()
    if f == 'G': return 0
    if '+' in f: return 1
    try: return int(f)
    except: return 0

df['floor_num'] = df['floor'].apply(clean_floor)

# ─────────────────────────────────────────────
# STEP 3: Encode Categorical Columns
# ─────────────────────────────────────────────
le_city    = LabelEncoder()
le_bhk     = LabelEncoder()
le_type    = LabelEncoder()

df['city_enc']  = le_city.fit_transform(df['city'])
df['bhk_enc']   = le_bhk.fit_transform(df['bhk'])
df['type_enc']  = le_type.fit_transform(df['type'])

# ─────────────────────────────────────────────
# STEP 4: Scale Numeric Features
# ─────────────────────────────────────────────
scaler = MinMaxScaler()

feature_cols = ['city_enc', 'bhk_enc', 'type_enc', 'price_value', 'area_num', 'floor_num']
df['price_value']   = df['price_value'].fillna(0)
df['area_num']      = df['area_num'].fillna(0)

feature_matrix = scaler.fit_transform(df[feature_cols])

print("\n✅ Feature matrix shape:", feature_matrix.shape)

# ─────────────────────────────────────────────
# STEP 5: Build Similarity Matrix
# ─────────────────────────────────────────────
similarity_matrix = cosine_similarity(feature_matrix)
print("✅ Similarity matrix shape:", similarity_matrix.shape)

# ─────────────────────────────────────────────
# STEP 6: Save Everything
# ─────────────────────────────────────────────
os.makedirs('/home/claude/ml_model', exist_ok=True)

# Save encoders, scaler, matrix, dataframe
with open('/home/claude/ml_model/le_city.pkl', 'wb') as f:
    pickle.dump(le_city, f)

with open('/home/claude/ml_model/le_bhk.pkl', 'wb') as f:
    pickle.dump(le_bhk, f)

with open('/home/claude/ml_model/le_type.pkl', 'wb') as f:
    pickle.dump(le_type, f)

with open('/home/claude/ml_model/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('/home/claude/ml_model/similarity_matrix.pkl', 'wb') as f:
    pickle.dump(similarity_matrix, f)

with open('/home/claude/ml_model/feature_matrix.pkl', 'wb') as f:
    pickle.dump(feature_matrix, f)

# Save cleaned dataframe (used during prediction to fetch results)
df.to_pickle('/home/claude/ml_model/properties_df.pkl')

print("\n🎉 Model saved successfully to /ml_model/")

# ─────────────────────────────────────────────
# STEP 7: Quick Test
# ─────────────────────────────────────────────
print("\n🧪 Quick Test — Recommend for: City=Mumbai, BHK=2 BHK, Type=Apartment, Budget=80L")

def recommend(city, bhk, prop_type, budget, top_n=3):
    # Encode user input safely
    city_enc  = le_city.transform([city])[0]   if city      in le_city.classes_     else 0
    bhk_enc   = le_bhk.transform([bhk])[0]     if bhk       in le_bhk.classes_      else 0
    type_enc  = le_type.transform([prop_type])[0] if prop_type in le_type.classes_  else 0

    user_input = scaler.transform([[city_enc, bhk_enc, type_enc, budget, 0, 0]])
    scores     = cosine_similarity(user_input, feature_matrix)[0]
    top_idx    = np.argsort(scores)[::-1][:top_n]

    results = df.iloc[top_idx][['title', 'city', 'bhk', 'type', 'price_value', 'area', 'image', 'location']].copy()
    results['match_score'] = (scores[top_idx] * 100).round(1)
    return results

results = recommend('Mumbai', '2 BHK', 'Apartment', 80)
print(results.to_string())
