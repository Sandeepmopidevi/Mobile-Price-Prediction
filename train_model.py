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

# Convert column names to lowercase
df.columns = df.columns.str.lower()

# Rename columns
df.rename(columns={
    "company name": "company",
    "ram": "ram",
    "front camera": "front_camera",
    "back camera": "back_camera",
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

df["ram"] = df["ram"].apply(extract_number)
df["front_camera"] = df["front_camera"].apply(extract_number)
df["back_camera"] = df["back_camera"].apply(extract_number)
df["battery"] = df["battery"].apply(extract_number)
df["price"] = df["price"].apply(extract_number)

# Drop missing values
df.dropna(inplace=True)

# Standardize RAM values (round to nearest standard value)
def round_ram(value):
    possible_rams = [2, 3, 4, 6, 8, 12, 16]
    return min(possible_rams, key=lambda x: abs(x - value))  # Find closest match

df["ram"] = df["ram"].apply(round_ram)

# Assign ROM values based on RAM
ram_rom_mapping = {
    2: 32,
    3: 32,
    4: 64,
    6: 128,
    8: 128,
    12: 256,
    16: 512
}

df["rom"] = df["ram"].map(ram_rom_mapping)

# Adjust prices based on ROM (~₹2000 increments)
def adjust_price(row):
    base_price = row["price"]
    expected_rom = ram_rom_mapping[row["ram"]]
    rom_diff = (row["rom"] - expected_rom) // 64  # ROM-based increment
    return base_price + (rom_diff * 2000)

df["price"] = df.apply(adjust_price, axis=1)

# Select features
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
    ("regressor", RandomForestRegressor(n_estimators=200, random_state=42))
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model.fit(X_train, y_train)

# Save model
os.makedirs("models", exist_ok=True)
with open("models/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved successfully!")
