const REVERSE_GEOCODING_URL = "https://nominatim.openstreetmap.org/reverse";

export function getCurrentLocation() {
  if (!navigator.geolocation) {
    return Promise.reject(new Error("Location is unavailable in this browser."));
  }

  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 0,
    });
  });
}

export async function getLocationName(latitude, longitude, accuracy = null) {
  const params = new URLSearchParams({
    lat: String(latitude),
    lon: String(longitude),
    format: "jsonv2",
    addressdetails: "1",
    "accept-language": "en",
  });
  const requestUrl = `${REVERSE_GEOCODING_URL}?${params.toString()}`;
  console.log("[GEOCODING] request:", requestUrl);
  const response = await fetch(requestUrl);

  if (!response.ok) {
    console.error("[GEOCODING] error:", response.status, response.statusText);
    throw new Error(`Location service returned ${response.status}.`);
  }

  const data = await response.json();
  const address = data.address || {};
  const city = address.city
    || address.town
    || address.village
    || address.municipality
    || address.county;

  if (!city) {
    console.error("[GEOCODING] error: response returned no city", data);
    throw new Error("Location service returned no city.");
  }

  const location = {
    city,
    state: address.state || address.state_district || "",
    country: address.country || "",
    latitude,
    longitude,
    accuracy,
  };
  console.log("[GEOCODING] success:", location);
  return location;
}

export async function searchLocation(query) {
  const params = new URLSearchParams({
    name: query,
    count: "1",
    language: "en",
    format: "json"
  });
  const requestUrl = `https://geocoding-api.open-meteo.com/v1/search?${params.toString()}`;
  console.log("[GEOCODING] search request:", requestUrl);
  
  const response = await fetch(requestUrl);
  if (!response.ok) {
    throw new Error(`Geocoding service returned ${response.status}`);
  }
  
  const data = await response.json();
  if (!data.results || data.results.length === 0) {
    return null;
  }
  
  const result = data.results[0];
  return {
    city: result.name,
    state: result.admin1 || "",
    country: result.country || "",
    latitude: result.latitude,
    longitude: result.longitude,
  };
}
