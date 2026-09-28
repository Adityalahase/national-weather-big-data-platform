# Member 3 → Backend Contract

## Final source policy
The DS pipeline uses **real Open-Meteo Historical Weather API data based on ERA5 reanalysis**.
It must NOT be presented as direct IMD station observation.

If the team later obtains official IMD observations, add them as another source with a `source` field and preserve provenance.

## Backend endpoint
Create:

GET /api/weather-events

Return the JSON objects from:
`outputs/weather_events.json`

## Event object
Each object contains:

- timestamp
- location.city
- location.state
- location.latitude
- location.longitude
- event_type
- severity
- risk_score
- confidence_score
- anomaly_score
- weather.temperature_c
- weather.humidity_pct
- weather.rainfall_mm
- weather.wind_speed_kmh
- weather.pressure_hpa
- weather.rain_6h_mm
- weather.rain_24h_mm
- source.name
- source.dataset
- source.note
- reasons[]

## Future citizen-report integration
When Member 4/NLP sends citizen reports, backend can attach:
- report_count
- verified_report_count
- suspicious_report_count
- report_locations
- report_event_type
- report_timestamp

The DS engine can later add these as extra features.

## Example response
{
  "event_type": "Heavy Rainfall",
  "severity": "High",
  "risk_score": 78.2,
  "confidence_score": 84.5,
  "anomaly_score": 72.1,
  "location": {
    "city": "Pune",
    "state": "Maharashtra",
    "latitude": 18.5204,
    "longitude": 73.8567
  },
  "source": {
    "name": "Open-Meteo",
    "dataset": "ERA5 reanalysis"
  },
  "reasons": [
    "elevated 24-hour rainfall",
    "anomalous weather pattern"
  ]
}
