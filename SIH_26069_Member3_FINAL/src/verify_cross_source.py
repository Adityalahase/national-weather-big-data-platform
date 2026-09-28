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
    "verified_weather_events_v2.json"
)

print("Reading weather event episodes...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

if df.empty:
    print("No weather episodes found.")
    exit()

df["start_time"] = pd.to_datetime(df["start_time"])
df["end_time"] = pd.to_datetime(df["end_time"])

verified = []

print("Running improved cross-source verification...")

for i, event in df.iterrows():

    city = event["location"]["city"]
    event_type = event["event_type"]
    source = event["source"]

    other_source = (
        "NASA POWER"
        if source == "Open-Meteo"
        else "Open-Meteo"
    )

    # Allow a 6-hour timing difference
    search_start = (
        event["start_time"] -
        pd.Timedelta(hours=6)
    )

    search_end = (
        event["end_time"] +
        pd.Timedelta(hours=6)
    )

    candidates = df[
        (df["location"].apply(
            lambda x: x["city"] == city
        ))
        &
        (df["event_type"] == event_type)
        &
        (df["source"] == other_source)
        &
        (df["start_time"] <= search_end)
        &
        (df["end_time"] >= search_start)
    ].copy()

    best_match = None
    best_score = 0

    for _, other in candidates.iterrows():

        latest_start = max(
            event["start_time"],
            other["start_time"]
        )

        earliest_end = min(
            event["end_time"],
            other["end_time"]
        )

        overlap = (
            earliest_end - latest_start
        ).total_seconds() / 3600

        # If no actual overlap, check distance
        if overlap < 0:

            if other["start_time"] > event["end_time"]:
                time_gap = (
                    other["start_time"] -
                    event["end_time"]
                ).total_seconds() / 3600
            else:
                time_gap = (
                    event["start_time"] -
                    other["end_time"]
                ).total_seconds() / 3600

            if time_gap > 6:
                continue

        else:
            time_gap = 0

        score = 50

        # Stronger score for actual overlap
        if overlap >= 1:
            score += 15

        if overlap >= 3:
            score += 10

        if overlap >= 6:
            score += 5

        # Rainfall evidence
        rain1 = event.get(
            "max_rainfall_24h_mm",
            0
        )

        rain2 = other.get(
            "max_rainfall_24h_mm",
            0
        )

        if rain1 > 0 and rain2 > 0:
            score += 10

        # Risk evidence
        risk1 = event.get(
            "peak_risk_score",
            0
        )

        risk2 = other.get(
            "peak_risk_score",
            0
        )

        if risk1 >= 35 and risk2 >= 35:
            score += 5

        if score > best_score:
            best_score = score
            best_match = other

    # ==========================================
    # FINAL VERIFICATION STATUS
    # ==========================================

    if best_match is None:

        status = "Needs Review"
        agreement = False
        credibility = 45.0

        evidence = (
            "No matching independent source "
            "was found within the allowed time window."
        )

    else:

        agreement = True
        credibility = min(
            round(best_score, 2),
            95
        )

        if credibility >= 80:
            status = "Cross-Source Verified"

        elif credibility >= 65:
            status = "Supported"

        else:
            status = "Needs Review"

        evidence = (
            f"{source} and {other_source} "
            f"showed supporting evidence for "
            f"{event_type} in {city} "
            f"within a 6-hour verification window."
        )

    verified.append({

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

        "peak_risk_score": event[
            "peak_risk_score"
        ],

        "average_confidence": event[
            "average_confidence"
        ],

        "source": source,

        "verification_status": status,

        "source_agreement": agreement,

        "credibility_score": credibility,

        "evidence": evidence
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
        verified,
        f,
        indent=2,
        ensure_ascii=False
    )


result = pd.DataFrame(verified)

print("\n======================================")
print("IMPROVED CROSS-SOURCE VERIFICATION")
print("======================================")

print(
    f"Total episodes : {len(result)}"
)

print("\nVerification status:")
print(
    result["verification_status"].value_counts()
)

print("\nSource agreement:")
print(
    result["source_agreement"].value_counts()
)

print(
    "\nAverage credibility:",
    round(
        result["credibility_score"].mean(),
        2
    )
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("======================================")