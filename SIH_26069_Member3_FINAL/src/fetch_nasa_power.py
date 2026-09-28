import requests
import pandas as pd
import os
import time

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITIES_FILE = os.path.join(BASE_DIR, "data", "cities.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw", "nasa_power")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# NASA POWER API
BASE_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"

# Date range
START_DATE = "20260801"
END_DATE = "20260831"

# Load cities
cities = pd.read_csv(CITIES_FILE)

print("NASA POWER Weather Data Collection Started...\n")

all_data = []

for _, city in cities.iterrows():

    city_name = city["city"]
    latitude = city["latitude"]
    longitude = city["longitude"]

    print(f"Fetching data for {city_name}...")

    params = {
        "parameters": "T2M,RH2M,PRECTOTCORR,WS10M,PS",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": START_DATE,
        "end": END_DATE,
        "format": "JSON",
        "time-standard": "lst"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=60)
        response.raise_for_status()

        data = response.json()

        properties = data["properties"]["parameter"]

        temp = properties["T2M"]
        humidity = properties["RH2M"]
        rainfall = properties["PRECTOTCORR"]
        wind = properties["WS10M"]
        pressure = properties["PS"]

        for timestamp in temp:

            all_data.append({
                "source": "NASA POWER",
                "source_type": "public_dataset",
                "timestamp": timestamp,
                "city": city_name,
                "latitude": latitude,
                "longitude": longitude,
                "temperature": temp[timestamp],
                "humidity": humidity[timestamp],
                "rainfall": rainfall[timestamp],
                "wind_speed": wind[timestamp],
                "pressure": pressure[timestamp]
            })

        print(f"✓ {city_name} completed")

    except Exception as e:
        print(f"✗ Error for {city_name}: {e}")

    time.sleep(1)


# Convert to DataFrame
df = pd.DataFrame(all_data)

# Save CSV
output_file = os.path.join(
    OUTPUT_DIR,
    "nasa_power_weather.csv"
)

df.to_csv(output_file, index=False)

print("\n--------------------------------")
print("NASA POWER collection completed!")
print(f"Total records: {len(df)}")
print(f"Saved to: {output_file}")
print("--------------------------------")