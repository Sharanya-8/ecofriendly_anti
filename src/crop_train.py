import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score

print("🚀 Advanced Crop Model Training Started...")

os.makedirs("models", exist_ok=True)

# Load dataset
df = pd.read_csv("data/crop_recommendation_dataset_final.csv")

# ----------------------------
# Feature Engineering
# ----------------------------

df["NPK_ratio"] = df["N"] / (df["P"] + df["K"] + 1)
df["PK_ratio"] = df["P"] / (df["K"] + 1)
df["temp_humidity"] = df["temperature"] * df["humidity"]

# Rainfall category
df["rainfall_category"] = pd.cut(
    df["rainfall"],
    bins=[0, 100, 200, 1000],
    labels=[0, 1, 2]
)

# ----------------------------
# Features & Target
# ----------------------------

features = [
    "N","P","K","ph","temperature","humidity","rainfall",
    "NPK_ratio","PK_ratio","temp_humidity","rainfall_category"
]

X = df[features]
y = df["crop"]

# Encode crop labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# ----------------------------
# Scaling
# ----------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ----------------------------
# Train-Test Split
# ----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded,
    test_size=0.25,
    random_state=42,
    stratify=y_encoded
)

# ----------------------------
# Advanced Model
# ----------------------------

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# Evaluation
# ----------------------------

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# ----------------------------
# Save Artifacts
# ----------------------------

joblib.dump(model, "models/crop_model.pkl")
joblib.dump(le, "models/crop_label_encoder.pkl")
joblib.dump(scaler, "models/crop_scaler.pkl")
joblib.dump(accuracy, "models/crop_accuracy.pkl")

print(f"✅ Advanced Crop Model Accuracy: {accuracy*100:.2f}%")