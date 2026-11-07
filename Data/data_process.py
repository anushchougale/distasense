
import pandas as pd
import os

# File paths
RAW_FILE = "Data/Raw/distance_readings.csv"
OUTPUT_FILE = "Data/Processed/data.csv"

# Create output folder
os.makedirs("Data/Processed", exist_ok=True)

# Read raw dataset
df = pd.read_csv(RAW_FILE)

# Convert columns
df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce")

df["Distance_cm"] = pd.to_numeric(
    df["Distance_cm"],
    errors="coerce"
)

# Remove invalid readings
df.dropna(
    subset=["Timestamp", "Distance_cm"],
    inplace=True
)

df = df[df["Distance_cm"].between(2, 400)]

# Remove duplicate timestamps
df.drop_duplicates(
    subset=["Timestamp"],
    inplace=True
)

# Sort by timestamp
df = df.sort_values("Timestamp").reset_index(drop=True)

# Calculate distance change
df["Distance_Change_cm"] = df["Distance_cm"].diff().fillna(0).round(2)

# Save processed dataset
df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Preprocessing completed!")
print("Total records:", len(df))
print("Saved file:", OUTPUT_FILE)
