import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR, "data", "raw", "social_media", "social_media_posts.csv"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "processed_social_media.csv"
)

print("Reading social media posts...")

df = pd.read_csv(INPUT_FILE)

print(f"Total posts loaded: {len(df)}")

# Clean timestamp
df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce"
)

# Clean text
df["text"] = (
    df["text"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# Standardize platform
df["platform"] = (
    df["platform"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

# Extract hashtags
df["hashtags"] = df["text"].str.findall(r"#\w+")

df["hashtags"] = df["hashtags"].apply(
    lambda x: ", ".join(x)
)

# Detect event type from text
def detect_event(text):

    text = text.lower()

    if "flood" in text or "waterlog" in text:
        return "Flooding"

    if "heavy rain" in text or "heavy rainfall" in text:
        return "Heavy Rainfall"

    if "thunderstorm" in text:
        return "Thunderstorm"

    if "strong wind" in text or "strong winds" in text:
        return "Strong Winds"

    if "dust storm" in text:
        return "Dust Storm"

    if "heatwave" in text or "extreme heat" in text:
        return "Heatwave"

    if "fog" in text:
        return "Fog"

    return "Normal"


df["event_type"] = df["text"].apply(detect_event)

# Basic validation
df = df.dropna(
    subset=[
        "post_id",
        "timestamp",
        "city",
        "latitude",
        "longitude"
    ]
)

# Remove duplicate posts
df = df.drop_duplicates(
    subset=["post_id"]
)

# Prototype source label
df["source_type"] = "demo_social_media"

# Initial credibility
df["credibility_score"] = 50.0

# Initial verification status
df["verification_status"] = "Pending"

# Save processed data
df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n======================================")
print("SOCIAL MEDIA PROCESSING COMPLETE")
print("======================================")

print(f"Valid posts : {len(df)}")

print("\nEvent distribution:")
print(df["event_type"].value_counts())

print("\nSaved to:")
print(OUTPUT_FILE)

print("======================================")