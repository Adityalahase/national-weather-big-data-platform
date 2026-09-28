"""
Weather Data Ingestion — India Meteorological Department (IMD)
SIH 2026 - National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer

Fetches current AWS (Automatic Weather Station) data from the official IMD API
and saves the raw JSON response to disk with a timestamped filename,
and extracts the payload to the normalized database schema.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend to sys.path so we can import the database models
backend_dir = project_root / "backend"
sys.path.append(str(backend_dir))

try:
    from database import SessionLocal, engine, Base
    import models
    HAS_DB = True
except ImportError:
    HAS_DB = False

# Load environment variables
load_dotenv()

IMD_API_KEY = os.environ.get("IMD_API_KEY")
IMD_EMAIL = os.environ.get("IMD_EMAIL")
IMD_PASSWORD = os.environ.get("IMD_PASSWORD")
IMD_API_BASE_URL = os.environ.get("IMD_API_BASE_URL", "https://api.imd.gov.in")
IMD_API_TIMEOUT = int(os.environ.get("IMD_API_TIMEOUT", 30))

# Exact IMD endpoint for AWS/station weather observations based on official docs
IMD_AWS_ENDPOINT = f"{IMD_API_BASE_URL}/api/v1/aws_data"
IMD_TOKEN_ENDPOINT = f"{IMD_API_BASE_URL}/api/oauth/token.php"

RAW_DATA_DIR = Path(__file__).resolve().parent / "data" / "raw"

class IMDAuth:
    """Manages JWT authentication for IMD APIs."""
    def __init__(self):
        self.token = None
        self.expires_at = None

    def get_token(self, force_refresh=False) -> str:
        # Return existing token if valid and not expiring in the next 5 minutes
        if not force_refresh and self.token and self.expires_at:
            if datetime.now() < self.expires_at - timedelta(minutes=5):
                return self.token
                
        if not IMD_EMAIL or not IMD_PASSWORD:
            print("[ERROR] IMD_EMAIL or IMD_PASSWORD not set in environment. Cannot authenticate.")
            sys.exit(1)

        payload = json.dumps({"email": IMD_EMAIL, "password": IMD_PASSWORD}).encode("utf-8")
        req = urllib.request.Request(
            IMD_TOKEN_ENDPOINT, 
            data=payload, 
            headers={"Content-Type": "application/json"}
        )
        try:
            resp = urllib.request.urlopen(req, timeout=IMD_API_TIMEOUT)
            data = json.loads(resp.read().decode("utf-8"))
            self.token = data.get("access_token")
            expires_in = int(data.get("expires_in", 3600))
            self.expires_at = datetime.now() + timedelta(seconds=expires_in)
            return self.token
        except urllib.error.HTTPError as e:
            print(f"[ERROR] JWT generation failed (HTTP {e.code}). Details: {e.read().decode('utf-8')}")
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"[ERROR] Network/Timeout Failure during JWT generation: {e.reason}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to parse JWT response: {e}")
            sys.exit(1)

auth_manager = IMDAuth()

def fetch_imd_aws_data(retries=1) -> dict:
    """Send a GET request to the official IMD API and return the parsed JSON response."""
    if not IMD_API_KEY:
        print("[ERROR] IMD_API_KEY environment variable is not set. Cannot authenticate with IMD.")
        sys.exit(1)

    print(f"[INFO] Fetching IMD AWS Data from {IMD_AWS_ENDPOINT}")
    
    token = auth_manager.get_token()
    
    headers = {
        "X-API-KEY": IMD_API_KEY,
        "Authorization": f"Bearer {token}"
    }
    
    req = urllib.request.Request(IMD_AWS_ENDPOINT, headers=headers)
    
    try:
        response = urllib.request.urlopen(req, timeout=IMD_API_TIMEOUT)
        data = response.read().decode('utf-8')
        if not data.strip():
            print("[ERROR] Received empty response from IMD API.")
            sys.exit(1)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            print("[ERROR] Failed to parse IMD response as JSON. Response might be malformed.")
            sys.exit(1)
            
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        if e.code == 401 and retries > 0:
            print("[WARN] Received 401 Unauthorized. Token might be expired. Refreshing JWT and retrying...")
            auth_manager.get_token(force_refresh=True)
            return fetch_imd_aws_data(retries=retries - 1)
        elif e.code == 401:
            print(f"[ERROR] Authentication Failed (401 Unauthorized).")
            print(f"Details: {body}")
            sys.exit(1)
        elif e.code == 403:
            print(f"[ERROR] Forbidden (403). The IMD API Key does not have permissions for this endpoint or IP is not whitelisted.")
            sys.exit(1)
        elif e.code == 404:
            print(f"[ERROR] Not Found (404). Endpoint missing or invalid route.")
            sys.exit(1)
        elif e.code == 429:
            print(f"[ERROR] Rate Limit Exceeded (429). Too many requests.")
            sys.exit(1)
        else:
            print(f"[ERROR] HTTP Error {e.code}: {e.reason} - {body}")
            sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[ERROR] Network/Timeout Failure connecting to IMD API: {e.reason}")
        sys.exit(1)


def extract_current_weather(payload: dict) -> list:
    """Pull out the observations and normalize into the common schema."""
    
    # Depending on IMD's response wrapper, it might return a list directly, or a dictionary containing the data list.
    # The official documentation sample shows an object structure:
    # { "ID": "B48970CA", "STATION": "LODI ROAD", "CURR_TEMP": "40.8", ... }
    # So the list of stations might be at the root or under a key.
    
    if isinstance(payload, list):
        aws_records = payload
    elif isinstance(payload, dict) and "data" in payload:
        aws_records = payload["data"]
    elif isinstance(payload, dict) and "ID" in payload:
        # A single object was returned
        aws_records = [payload]
    else:
        # Unknown structure, try to find a list
        aws_records = [v for k, v in payload.items() if isinstance(v, list)]
        if aws_records:
            aws_records = aws_records[0]
        else:
            aws_records = []

    if not aws_records:
        print("[INFO] Valid response received from IMD, but no AWS data records were found.")
        return []

    extracted_events = []
    
    def safe_float(val):
        if val is None:
            return None
        # Remove any non-numeric characters except '.' and '-'
        s = str(val).strip()
        # Some IMD strings have stray question marks like '?24.0826947'
        s = "".join(c for c in s if c.isdigit() or c in '.-')
        try:
            return float(s)
        except ValueError:
            return None
    
    for record in aws_records:
        # Parse timestamp from DATE and TIME fields
        # Example: "DATE": "2024-06-06", "TIME": "07:00:00"
        date_str = record.get("DATE", "")
        time_str = record.get("TIME", "")
        timestamp = None
        if date_str and time_str:
            try:
                # IMD uses IST (UTC+5:30)
                ist_zone = timezone(timedelta(hours=5, minutes=30))
                dt_ist = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=ist_zone)
                dt_utc = dt_ist.astimezone(timezone.utc)
                timestamp = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                timestamp = datetime.now(timezone.utc).isoformat()
        else:
            timestamp = datetime.now(timezone.utc).isoformat()
            
        # Determine event type based on weather code or temperature
        weather_code = str(record.get("WEATHER_CODE", ""))
        event_type = "Observation"
        severity = "Low"
        
        try:
            curr_temp = record.get("CURR_TEMP")
            temp = float(curr_temp) if curr_temp is not None else 0.0
            if temp > 40:
                event_type = "Heatwave"
                severity = "High"
            elif temp > 35:
                event_type = "High Temperature"
                severity = "Medium"
        except ValueError:
            pass
            
        try:
            wind_speed = record.get("WIND_SPEED")
            wind = float(wind_speed) if wind_speed is not None else 0.0
            if wind > 30:
                event_type = "High Wind"
                severity = "Medium"
        except ValueError:
            pass

        extracted = {
            "time": timestamp,
            "event_type": event_type,
            "severity": severity,
            "city": record.get("DISTRICT") or record.get("STATION"),
            "state": record.get("STATE"),
            "latitude": safe_float(record.get("Latitude")),
            "longitude": safe_float(record.get("Longitude")),
            "source": "IMD",
            "station_id": record.get("ID"),
            "confidence_score": 100, # Official data
            # Store additional raw metrics for Event Intelligence
            "metadata": {
                "station_id": record.get("ID"),
                "call_sign": record.get("CALL_SIGN"),
                "station_name": record.get("STATION"),
                "temperature_c": record.get("CURR_TEMP"),
                "dew_point_c": record.get("DEW_POINT_TEMP"),
                "relative_humidity": record.get("RH"),
                "wind_direction": record.get("WIND_DIRECTION"),
                "wind_speed": record.get("WIND_SPEED"),
                "mslp": record.get("MSLP"),
                "min_temp": record.get("MIN_TEMP"),
                "max_temp": record.get("MAX_TEMP"),
                "weather_code": record.get("WEATHER_CODE"),
            }
        }
        
        # Only add valid looking records (must have lat/long or city/state)
        if extracted["latitude"] and extracted["longitude"]:
            extracted_events.append(extracted)
        
    return extracted_events


def save_raw_response(payload: dict) -> Path:
    """Save the raw API response as a timestamped JSON file."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"imd_aws_raw_{timestamp}.json"
    filepath = RAW_DATA_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return filepath


def main():
    print("Initializing Live IMD Integration...")
    print(f"Target: {IMD_AWS_ENDPOINT}")
    
    raw_payload = fetch_imd_aws_data()
    saved_path = save_raw_response(raw_payload)
    
    print("\n[SUCCESS] Weather data fetched and saved.")
    print(f"Raw response saved to: {saved_path}")

    extracted_events = extract_current_weather(raw_payload)
    print(f"\nExtracted {len(extracted_events)} normalized events.")
    
    if extracted_events:
        print("Sample normalized event:")
        print(json.dumps(extracted_events[0], indent=2))
        
        # For this isolated ingestion script, we push to DB directly.
        if HAS_DB:
            print(f"Connecting to database to insert {len(extracted_events)} events...")
            db = SessionLocal()
            try:
                inserted = 0
                duplicates = 0
                for record in extracted_events:
                    # Duplicate protection: check if an event with same type, city, and similar time exists
                    ts = datetime.fromisoformat(record["time"].replace("Z", "+00:00"))
                    
                    if record["event_type"] == "Observation":
                        # For periodic observations, only duplicate if exact same station and EXACT timestamp
                        # Using naive datetime for exact equality match with SQLite DateTime column
                        ts_naive = ts.replace(tzinfo=None)
                        exists = db.query(models.WeatherEvent).filter(
                            models.WeatherEvent.event_type == record["event_type"],
                            models.WeatherEvent.station_id == record["station_id"],
                            models.WeatherEvent.source == "IMD",
                            models.WeatherEvent.timestamp == ts_naive
                        ).first()
                    else:
                        # We consider it a duplicate if same type, city, source within 24 hours for discrete alerts
                        time_threshold = ts - timedelta(hours=24)
                        exists = db.query(models.WeatherEvent).filter(
                            models.WeatherEvent.event_type == record["event_type"],
                            models.WeatherEvent.city == record["city"],
                            models.WeatherEvent.source == "IMD",
                            models.WeatherEvent.timestamp >= time_threshold
                        ).first()
                    
                    if exists:
                        duplicates += 1
                        continue
                        
                    event = models.WeatherEvent(
                        event_type=record["event_type"],
                        city=record["city"],
                        state=record["state"],
                        latitude=record["latitude"],
                        longitude=record["longitude"],
                        severity=record["severity"],
                        confidence_score=record["confidence_score"],
                        verification_status="Verified", # Official data is pre-verified
                        timestamp=ts,
                        source="IMD",
                        station_id=record["station_id"]
                    )
                    db.add(event)
                    inserted += 1
                    
                db.commit()
                print(f"[SUCCESS] Database integration complete. Inserted: {inserted}. Skipped duplicates: {duplicates}.")
            except Exception as e:
                db.rollback()
                print(f"[ERROR] Database insertion failed: {e}")
            finally:
                db.close()
        else:
            print("[WARN] Backend modules not found. Could not integrate with DB.")


if __name__ == "__main__":
    main()
