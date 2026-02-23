import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

print("🚀 Advanced Soil Model Training Started...")

os.makedirs("models", exist_ok=True)

df = pd.read_csv("data/soil_fertility_dataset.csv")

# ----------------------------
# Add Feature Engineering
# ----------------------------

df["NPK_ratio"] = df["N"] / (df["P"] + df["K"] + 1)
df["PK_ratio"] = df["P"] / (df["K"] + 1)

# ----------------------------
# Features & Target
# ----------------------------

features = ["N","P","K","ph","moisture","NPK_ratio","PK_ratio"]
X = df[features]
y = df["fertility"]

# ----------------------------
# Scaling
# ----------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ----------------------------
# Split
# ----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# ----------------------------
# Model
# ----------------------------

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))

joblib.dump(model, "models/soil_model.pkl")
joblib.dump(scaler, "models/soil_scaler.pkl")
joblib.dump(accuracy, "models/soil_accuracy.pkl")

print(f"✅ Advanced Soil Model Accuracy: {accuracy*100:.2f}%")