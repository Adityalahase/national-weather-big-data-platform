import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "weather_event_episodes.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "evidence_scored_events.json"
)

print("Reading weather episodes...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

if df.empty:
    print("No events found.")
    exit()

df["start_time"] = pd.to_datetime(df["start_time"])
df["end_time"] = pd.to_datetime(df["end_time"])

results = []

print("Calculating evidence scores...")

for i, event in df.iterrows():

    score = 0
    evidence = []

    # --------------------------------------
    # 1. Base AI evidence
    # --------------------------------------

    risk = float(event.get("peak_risk_score", 0))
    confidence = float(
        event.get("average_confidence", 0)
    )

    if risk >= 60:
        score += 25
        evidence.append("High AI risk score")

    elif risk >= 35:
        score += 15
        evidence.append("Medium AI risk score")

    else:
        score += 5

    # --------------------------------------
    # 2. Duration evidence
    # --------------------------------------

    duration = float(
        event.get("duration_hours", 0)
    )

    if duration >= 6:
        score += 15
        evidence.append(
            "Long-duration weather episode"
        )

    elif duration >= 3:
        score += 10
        evidence.append(
            "Sustained weather episode"
        )

    elif duration >= 1:
        score += 5

    # --------------------------------------
    # 3. Rainfall evidence
    # --------------------------------------

    rain6 = float(
        event.get("max_rainfall_6h_mm", 0)
    )

    rain24 = float(
        event.get("max_rainfall_24h_mm", 0)
    )

    if rain24 >= 100 or rain6 >= 50:

        score += 20

        evidence.append(
            "Significant rainfall evidence"
        )

    elif rain24 >= 50 or rain6 >= 25:

        score += 12

        evidence.append(
            "Moderate rainfall evidence"
        )

    # --------------------------------------
    # 4. Wind evidence
    # --------------------------------------

    wind = float(
        event.get("max_wind_speed_kmh", 0)
    )

    if wind >= 70:

        score += 20

        evidence.append(
            "Very strong wind evidence"
        )

    elif wind >= 40:

        score += 10

        evidence.append(
            "Strong wind evidence"
        )

    # --------------------------------------
    # 5. Temperature evidence
    # --------------------------------------

    temp = float(
        event.get("max_temperature_c", 0)
    )

    if temp >= 43:

        score += 20

        evidence.append(
            "Extreme temperature evidence"
        )

    elif temp >= 40:

        score += 10

        evidence.append(
            "High temperature evidence"
        )

    # --------------------------------------
    # 6. AI confidence
    # --------------------------------------

    if confidence >= 85:

        score += 10

        evidence.append(
            "High model confidence"
        )

    elif confidence >= 70:

        score += 5

        evidence.append(
            "Moderate model confidence"
        )

    # --------------------------------------
    # Final score
    # --------------------------------------

    credibility = min(score, 100)

    if credibility >= 70:

        status = "Verified"

    elif credibility >= 50:

        status = "Supported"

    else:

        status = "Needs Review"

    results.append({

        "event_id": f"EVT-{i + 1:05d}",

        "start_time": event[
            "start_time"
        ].strftime("%Y-%m-%d %H:%M:%S"),

        "end_time": event[
            "end_time"
        ].strftime("%Y-%m-%d %H:%M:%S"),

        "duration_hours": event[
            "duration_hours"
        ],

        "location": event[
            "location"
        ],

        "event_type": event[
            "event_type"
        ],

        "severity": event[
            "severity"
        ],

        "source": event[
            "source"
        ],

        "risk_score": event[
            "peak_risk_score"
        ],

        "model_confidence": event[
            "average_confidence"
        ],

        "credibility_score": credibility,

        "verification_status": status,

        "evidence": evidence
    })


# --------------------------------------
# Save output
# --------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )


result_df = pd.DataFrame(results)

print("\n======================================")
print("EVIDENCE SCORING COMPLETE")
print("======================================")

print(
    f"Total events : {len(result_df)}"
)

print("\nVerification status:")

print(
    result_df[
        "verification_status"
    ].value_counts()
)

print(
    "\nAverage credibility:",
    round(
        result_df[
            "credibility_score"
        ].mean(),
        2
    )
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("======================================")