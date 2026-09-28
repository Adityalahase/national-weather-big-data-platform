import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOCIAL_FILE = os.path.join(
    BASE_DIR, "data", "processed", "processed_social_media.csv"
)

WEATHER_FILE = os.path.join(
    BASE_DIR, "data", "processed", "multi_source_weather.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR, "data", "processed", "verified_social_media.csv"
)

print("Reading social media posts...")
social = pd.read_csv(SOCIAL_FILE)

print("Reading multi-source weather data...")
weather = pd.read_csv(WEATHER_FILE)

social["timestamp"] = pd.to_datetime(
    social["timestamp"], errors="coerce"
)

weather["timestamp"] = pd.to_datetime(
    weather["timestamp"], errors="coerce"
)

social = social.dropna(subset=["timestamp"])
weather = weather.dropna(subset=["timestamp"])

results = []

print("\nStarting social media verification...\n")

for _, post in social.iterrows():

    city = post["city"]
    event = post["event_type"]
    post_time = post["timestamp"]

    # Same city
    city_weather = weather[
        weather["city"].str.lower() == str(city).lower()
    ].copy()

    if city_weather.empty:

        results.append({
            **post.to_dict(),
            "weather_evidence": "No weather data",
            "verification_status": "Unverified",
            "credibility_score": 30.0,
            "verification_reason": "No matching weather data found"
        })

        continue

    # Weather within +/- 3 hours
    city_weather["time_difference"] = abs(
        city_weather["timestamp"] - post_time
    )

    nearby = city_weather[
        city_weather["time_difference"] <= pd.Timedelta(hours=3)
    ].copy()

    if nearby.empty:

        results.append({
            **post.to_dict(),
            "weather_evidence": "No nearby weather data",
            "verification_status": "Unverified",
            "credibility_score": 35.0,
            "verification_reason": "No weather record within 3 hours"
        })

        continue

    # Separate sources
    open_data = nearby[
        nearby["source"] == "Open-Meteo"
    ]

    nasa_data = nearby[
        nearby["source"] == "NASA POWER"
    ]

    # Weather values
    rainfall_values = nearby["rainfall_mm"].dropna()
    wind_values = nearby["wind_speed_kmh"].dropna()
    humidity_values = nearby["humidity_pct"].dropna()
    temperature_values = nearby["temperature_c"].dropna()

    rainfall = (
        rainfall_values.max()
        if len(rainfall_values)
        else 0
    )

    wind = (
        wind_values.max()
        if len(wind_values)
        else 0
    )

    humidity = (
        humidity_values.mean()
        if len(humidity_values)
        else 0
    )

    temperature = (
        temperature_values.max()
        if len(temperature_values)
        else 0
    )

    evidence_points = 0
    reasons = []

    # Event-specific verification
    if event in ["Heavy Rainfall", "Flooding"]:

        if rainfall >= 10:
            evidence_points += 2
            reasons.append(
                f"High rainfall detected ({rainfall:.1f} mm)"
            )

        elif rainfall >= 2:
            evidence_points += 1
            reasons.append(
                f"Rainfall detected ({rainfall:.1f} mm)"
            )

        else:
            reasons.append(
                "Very low rainfall detected"
            )

    elif event == "Strong Winds":

        if wind >= 40:
            evidence_points += 2
            reasons.append(
                f"Strong wind detected ({wind:.1f} km/h)"
            )

        elif wind >= 25:
            evidence_points += 1
            reasons.append(
                f"Moderate wind detected ({wind:.1f} km/h)"
            )

        else:
            reasons.append(
                "Wind speed is relatively low"
            )

    elif event == "Thunderstorm":

        if wind >= 30 and humidity >= 70:
            evidence_points += 2
            reasons.append(
                "Strong wind and high humidity support thunderstorm"
            )

        elif humidity >= 70:
            evidence_points += 1
            reasons.append(
                "High humidity detected"
            )

        else:
            reasons.append(
                "Weak thunderstorm evidence"
            )

    elif event == "Heatwave":

        if temperature >= 40:
            evidence_points += 2
            reasons.append(
                f"High temperature detected ({temperature:.1f} °C)"
            )

        elif temperature >= 35:
            evidence_points += 1
            reasons.append(
                f"Elevated temperature detected ({temperature:.1f} °C)"
            )

        else:
            reasons.append(
                "Temperature does not strongly support heatwave"
            )

    elif event == "Fog":

        if humidity >= 90 and wind <= 10:
            evidence_points += 2
            reasons.append(
                "High humidity and low wind support fog"
            )

        elif humidity >= 85:
            evidence_points += 1
            reasons.append(
                "High humidity detected"
            )

        else:
            reasons.append(
                "Weak fog evidence"
            )

    elif event == "Dust Storm":

        if wind >= 30:
            evidence_points += 2
            reasons.append(
                f"Strong wind supports dust storm ({wind:.1f} km/h)"
            )

        elif wind >= 20:
            evidence_points += 1
            reasons.append(
                "Moderate wind detected"
            )

        else:
            reasons.append(
                "Weak wind evidence"
            )

    # Source agreement
    if not open_data.empty and not nasa_data.empty:

        evidence_points += 1

        reasons.append(
            "Open-Meteo and NASA POWER agree"
        )

    elif not open_data.empty or not nasa_data.empty:

        reasons.append(
            "Weather evidence available from one public dataset"
        )

    # Credibility
    credibility = 40 + (evidence_points * 15)

    credibility = min(95, credibility)

    # Final status
    if credibility >= 70:
        status = "Verified"

    elif credibility >= 50:
        status = "Needs Review"

    else:
        status = "Suspicious"

    results.append({
        **post.to_dict(),

        "weather_evidence": (
            f"Rainfall={rainfall:.1f}mm, "
            f"Wind={wind:.1f}km/h, "
            f"Humidity={humidity:.1f}%, "
            f"Temperature={temperature:.1f}C"
        ),

        "verification_status": status,

        "credibility_score": round(
            credibility, 2
        ),

        "verification_reason": "; ".join(reasons)
    })


verified = pd.DataFrame(results)

verified.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n======================================")
print("SOCIAL MEDIA VERIFICATION COMPLETE")
print("======================================")

print(f"Total posts : {len(verified)}")

print("\nVerification results:")
print(
    verified["verification_status"].value_counts()
)

print("\nAverage credibility:")
print(
    round(
        verified["credibility_score"].mean(),
        2
    )
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("======================================")