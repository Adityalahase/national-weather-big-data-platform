import weatherObservations from "../data/weatherObservations";

const OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast";

function normalizeQuery(query) {
  return query.trim().toLowerCase().replace(/\s+/g, " ");
}

function distanceBetween(first, second) {
  return Math.hypot(
    first.latitude - second.latitude,
    first.longitude - second.longitude,
  );
}

function toLocation(observation) {
  return {
    city: observation.city,
    state: observation.state,
    latitude: observation.latitude,
    longitude: observation.longitude,
  };
}

export async function getCurrentWeather(latitude, longitude) {
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    throw new Error("Valid latitude and longitude are required.");
  }

  const params = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
    current: "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,surface_pressure",
    timezone: "auto",
  });
  const requestUrl = `${OPEN_METEO_URL}?${params.toString()}`;
  console.log("[WEATHER] request:", requestUrl);
  const response = await fetch(requestUrl);

  if (!response.ok) {
    console.error("[WEATHER] error:", response.status, response.statusText);
    throw new Error(`Weather service returned ${response.status}.`);
  }

  const data = await response.json();
  const current = data.current;

  if (!current || current.temperature_2m === undefined) {
    console.error("[WEATHER] error: response has no current conditions", data);
    throw new Error("Weather service returned no current conditions.");
  }

  const observation = {
    latitude,
    longitude,
    temperature: current.temperature_2m,
    rainfall: current.precipitation,
    humidity: current.relative_humidity_2m,
    wind_speed: current.wind_speed_10m,
    wind_direction: current.wind_direction_10m,
    air_pressure: current.surface_pressure,
    timestamp: current.time,
  };
  console.log("[WEATHER] success:", observation);
  return observation;
}

export function getLocationByQuery(query) {
  const normalizedQuery = normalizeQuery(query);
  if (!normalizedQuery) return null;

  const observation = weatherObservations.find((item) => (
    normalizeQuery(item.city) === normalizedQuery
    || normalizeQuery(`${item.city}, ${item.state}`) === normalizedQuery
  ));

  return observation ? toLocation(observation) : null;
}

export function getWeatherByLocation(latitude, longitude) {
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    return { location: null, observation: null };
  }

  const observation = weatherObservations.find((item) => (
    distanceBetween({ latitude, longitude }, item) < 0.0001
  ));

  if (!observation) {
    return {
      location: {
        city: "Current location",
        state: "Weather data unavailable",
        latitude,
        longitude,
      },
      observation: null,
    };
  }

  return {
    location: toLocation(observation),
    observation,
  };
}

export function getWeatherForLocation(location) {
  if (!location) return { location: null, observation: null };

  const coordinateResult = getWeatherByLocation(location.latitude, location.longitude);
  if (coordinateResult.observation) return coordinateResult;

  const observation = weatherObservations.find((item) => (
    normalizeQuery(item.city) === normalizeQuery(location.city)
    && normalizeQuery(item.state) === normalizeQuery(location.state)
  ));

  return {
    location,
    observation: observation || null,
  };
}

export function getWeatherForEvent(event) {
  return getWeatherForLocation(event
    ? {
      city: event.city,
      state: event.state,
      latitude: event.latitude,
      longitude: event.longitude,
    }
    : null);
}

export function getDefaultWeather() {
  const latestObservation = weatherObservations.reduce((latest, observation) => (
    !latest || new Date(observation.timestamp) > new Date(latest.timestamp)
      ? observation
      : latest
  ), null);

  return latestObservation
    ? {
      location: toLocation(latestObservation),
      observation: latestObservation,
    }
    : { location: null, observation: null };
}

export async function geocodeCity(query) {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=1&format=json`;
  try {
    const response = await fetch(url);
    if (!response.ok) return null;
    const data = await response.json();
    if (data.results && data.results.length > 0) {
      const result = data.results[0];
      return {
        city: result.name,
        state: result.admin1 || result.country,
        latitude: result.latitude,
        longitude: result.longitude,
      };
    }
  } catch (error) {
    console.error("Geocoding failed", error);
  }
  return null;
}
