import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# ✅ Step 1: Load data
csv_path = 'face_data.csv'
if not os.path.exists(csv_path):
    print("❌ face_data.csv not found!")
    exit()

df = pd.read_csv(csv_path, header=None)

# ✅ Step 2: Rename columns: 1404 features + 1 label
df.columns = list(range(df.shape[1] - 1)) + ['label']

# ✅ Step 3: Split into X and y
X = df.drop('label', axis=1)
y = df['label']

# ✅ Step 4: Train/test split (optional, for real training)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Step 5: Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# ✅ Step 6: Save model to file
joblib.dump(model, 'face_model.pkl')
print("✅ Model saved successfully as face_model.pkl")
