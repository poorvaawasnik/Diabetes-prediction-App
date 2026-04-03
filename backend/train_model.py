import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Create model folder
os.makedirs("model", exist_ok=True)

# Load dataset
df = pd.read_csv("data/diabetes.csv")

# Replace zero values
cols = ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']
df[cols] = df[cols].replace(0, np.nan)
df.fillna(df.mean(), inplace=True)

# Add new columns if missing
if "FamilyHistory" not in df.columns:
    df["FamilyHistory"] = 0

if "PhysicalActivity" not in df.columns:
    df["PhysicalActivity"] = 0

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

pickle.dump(model, open("model/diabetes_model.pkl", "wb"))
pickle.dump(scaler, open("model/scaler.pkl", "wb"))

print("✅ Model trained and saved successfully!")