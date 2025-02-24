import pandas as pd
import numpy as np
import pickle
import re
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

# Load dataset
df = pd.read_csv("data/mobile_data.csv", encoding="ISO-8859-1")

# Standardize column names
df.columns = df.columns.str.lower()
df.rename(columns={
    "company name": "company",
    "ram": "ram",
    "front camera": "front_camera",
    "back camera": "back_camera",
    "processor": "processor",
    "battery capacity": "battery",
    "launched price (india)": "price"
}, inplace=True)

# Remove Apple devices
df = df[df["company"].str.lower() != "apple"]

# Function to extract numeric values from strings
def extract_number(value):
    if isinstance(value, str):
        num = re.findall(r"\d+\.?\d*", value.replace(",", ""))
        return float(num[0]) if num else np.nan
    return value

# Apply cleaning function
for col in ["ram", "front_camera", "back_camera", "battery", "price"]:
    df[col] = df[col].apply(extract_number)

# Adding ROM column manually based on domain knowledge
def assign_rom(ram):
    """ Assign ROM based on RAM using domain knowledge """
    if ram <= 2:
        return 32
    elif ram <= 4:
        return 64
    elif ram <= 6:
        return 128
    elif ram <= 8:
        return 256
    elif ram <= 12:
        return 512
    else:
        return 1024

df["rom"] = df["ram"].apply(assign_rom)

# Adjust price based on RAM-ROM combinations
def adjust_price(row):
    base_price = row["price"]
    rom_diff = (row["rom"] - assign_rom(row["ram"])) // 64
    price_adjustment = rom_diff * 2000  # Adjust ROM pricing
    return base_price + price_adjustment

df["price"] = df.apply(adjust_price, axis=1)

# Drop missing values
df.dropna(inplace=True)

# ✅ Ensure 'screen_size' and 'weight' are completely removed
columns_to_keep = ["company", "ram", "rom", "front_camera", "back_camera", "battery", "price"]
df = df[columns_to_keep]  # Only keep required columns

# Select features & target
X = df[["company", "ram", "rom", "front_camera", "back_camera", "battery"]]
y = df["price"].astype(float)

# Define transformations
numeric_features = ["ram", "rom", "front_camera", "back_camera", "battery"]
categorical_features = ["company"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
])

# Create pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model.fit(X_train, y_train)

# Save model
os.makedirs("models", exist_ok=True)
with open("models/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model retrained successfully with refined pricing logic!")
