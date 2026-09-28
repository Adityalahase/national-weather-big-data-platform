import pandas as pd
import os

# -----------------------------------
# Project paths
# -----------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "citizen",
    "citizen_reports.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "processed_citizen_reports.csv"
)

# -----------------------------------
# Read citizen reports
# -----------------------------------

print("Reading citizen reports...")

df = pd.read_csv(INPUT_FILE)

print(f"Total reports loaded: {len(df)}")

# -----------------------------------
# Clean timestamp
# -----------------------------------

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

# -----------------------------------
# Clean text
# -----------------------------------

df["description"] = (
    df["description"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# -----------------------------------
# Standardize event types
# -----------------------------------

event_mapping = {
    "Heavy Rainfall": "Heavy Rainfall",
    "Waterlogging": "Flooding",
    "Flooding": "Flooding",
    "Thunderstorm": "Thunderstorm",
    "Strong Winds": "Strong Winds",
    "Heatwave": "Heatwave",
    "Dust Storm": "Dust Storm",
    "Fog": "Fog"
}

df["event_type"] = (
    df["event_type"]
    .map(event_mapping)
    .fillna("Other")
)

# -----------------------------------
# Validate coordinates
# -----------------------------------

df["latitude"] = pd.to_numeric(
    df["latitude"],
    errors="coerce"
)

df["longitude"] = pd.to_numeric(
    df["longitude"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "timestamp",
        "city",
        "latitude",
        "longitude",
        "event_type"
    ]
)

# -----------------------------------
# Add verification status
# -----------------------------------

df["verification_status"] = "Pending"

# Initial credibility score
df["credibility_score"] = 50.0

# -----------------------------------
# Remove duplicate reports
# -----------------------------------

df = df.drop_duplicates(
    subset=[
        "city",
        "timestamp",
        "event_type",
        "description"
    ]
)

# -----------------------------------
# Save processed data
# -----------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("CITIZEN REPORT PROCESSING COMPLETE")
print("===================================")

print(f"Valid reports : {len(df)}")

print("\nEvent distribution:")
print(df["event_type"].value_counts())

print("\nSaved to:")
print(OUTPUT_FILE)

print("===================================")