import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "weather_events_multisource.json"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "weather_event_episodes.json"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Reading multi-source weather events...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.json_normalize(data)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

df = df.dropna(
    subset=["timestamp"]
)

# ==========================================
# EVENT GROUPING
# ==========================================

# Only significant weather events
event_types = [
    "Heavy Rainfall",
    "Fog",
    "Strong Winds",
    "Thunderstorm",
    "Heatwave",
    "Dust Storm"
]

df = df[
    df["event_type"].isin(event_types)
].copy()

df = df.sort_values(
    ["source.name", "location.city", "event_type", "timestamp"]
)

episodes = []

print("Grouping continuous weather events...")

for (source, city, event_type), group in df.groupby(
    ["source.name", "location.city", "event_type"]
):

    group = group.sort_values("timestamp")

    current_records = []
    previous_time = None

    for _, row in group.iterrows():

        current_time = row["timestamp"]

        # Start a new episode if gap > 2 hours
        if (
            previous_time is not None
            and current_time - previous_time > pd.Timedelta(hours=2)
        ):

            if current_records:
                episodes.append(
                    current_records
                )

            current_records = []

        current_records.append(row)

        previous_time = current_time

    if current_records:
        episodes.append(current_records)


# ==========================================
# CREATE EPISODE SUMMARY
# ==========================================

final_episodes = []

for records in episodes:

    episode = pd.DataFrame(records)

    first = episode.iloc[0]
    last = episode.iloc[-1]

    start_time = first["timestamp"]
    end_time = last["timestamp"]

    duration_hours = (
        (end_time - start_time).total_seconds()
        / 3600
    ) + 1

    peak_risk = episode["risk_score"].max()

    max_anomaly = episode["anomaly_score"].max()

    avg_confidence = episode[
        "confidence_score"
    ].mean()

    max_rain_24h = episode[
        "weather.rain_24h_mm"
    ].max()

    max_rain_6h = episode[
        "weather.rain_6h_mm"
    ].max()

    max_wind = episode[
        "weather.wind_speed_kmh"
    ].max()

    max_temp = episode[
        "weather.temperature_c"
    ].max()

    severity_order = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }

    episode["severity_rank"] = episode[
        "severity"
    ].map(severity_order)

    highest_severity = episode.loc[
        episode["severity_rank"].idxmax(),
        "severity"
    ]

    final_episodes.append({

        "start_time": start_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "end_time": end_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "duration_hours": round(
            duration_hours,
            2
        ),

        "location": {
            "city": first["location.city"],
            "state": first["location.state"],
            "latitude": first["location.latitude"],
            "longitude": first["location.longitude"]
        },

        "event_type": first["event_type"],

        "severity": highest_severity,

        "peak_risk_score": round(
            peak_risk,
            2
        ),

        "max_anomaly_score": round(
            max_anomaly,
            2
        ),

        "average_confidence": round(
            avg_confidence,
            2
        ),

        "max_rainfall_6h_mm": round(
            max_rain_6h,
            2
        ),

        "max_rainfall_24h_mm": round(
            max_rain_24h,
            2
        ),

        "max_wind_speed_kmh": round(
            max_wind,
            2
        ),

        "max_temperature_c": round(
            max_temp,
            2
        ),

        "source": first["source.name"],

        "source_type": first["source.source_type"],

        "observations": len(episode)
    })


# ==========================================
# SAVE
# ==========================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_episodes,
        f,
        indent=2,
        ensure_ascii=False
    )


print("\n======================================")
print("WEATHER EVENT AGGREGATION COMPLETE")
print("======================================")

print(
    f"Hourly event records : {len(df)}"
)

print(
    f"Weather episodes     : {len(final_episodes)}"
)

print("\nEpisode distribution:")

episode_df = pd.DataFrame(
    final_episodes
)

if not episode_df.empty:
    print(
        episode_df["event_type"].value_counts()
    )

print("\nSaved to:")
print(OUTPUT_FILE)

print("======================================")