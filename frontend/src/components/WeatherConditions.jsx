const compassDirections = [
  "N",
  "NNE",
  "NE",
  "ENE",
  "E",
  "ESE",
  "SE",
  "SSE",
  "S",
  "SSW",
  "SW",
  "WSW",
  "W",
  "WNW",
  "NW",
  "NNW",
];

function getCompassDirection(degrees) {
  if (typeof degrees !== "number" || Number.isNaN(degrees)) return null;

  const normalizedDegrees = ((degrees % 360) + 360) % 360;
  return compassDirections[Math.round(normalizedDegrees / 22.5) % 16];
}

function formatValue(value, unit) {
  return value === null || value === undefined || value === ""
    ? "Unavailable"
    : `${value}${unit}`;
}

function WeatherConditions({
  observation,
  location,
  status = "ready",
  statusMessage,
  onRetryLocation,
  isRetrying = false,
}) {
  const windDirection = observation?.wind_direction;
  const compassDirection = getCompassDirection(windDirection);
  const conditions = [
    {
      label: "Temperature",
      value: formatValue(observation?.temperature, " °C"),
      icon: "🌡️",
    },
    {
      label: "Rainfall",
      value: formatValue(observation?.rainfall, " mm"),
      icon: "🌧️",
    },
    {
      label: "Humidity",
      value: formatValue(observation?.humidity, " %"),
      icon: "💧",
    },
    {
      label: "Wind Speed",
      value: formatValue(observation?.wind_speed, " km/h"),
      icon: "💨",
    },
    {
      label: "Wind Direction",
      value: windDirection === null || windDirection === undefined || windDirection === ""
        ? "Unavailable"
        : `${windDirection}°${compassDirection ? ` (${compassDirection})` : ""}`,
      icon: "🧭",
    },
    {
      label: "Air Pressure",
      value: formatValue(observation?.air_pressure, " hPa"),
      icon: "⏱️",
    },
  ];
  const accuracy = location?.accuracy;
  const isLowAccuracy = typeof accuracy === "number" && accuracy > 1000;
  const isVeryLowAccuracy = typeof accuracy === "number" && accuracy > 5000;
  const formattedAccuracy = typeof accuracy === "number"
    ? accuracy >= 1000
      ? `${(accuracy / 1000).toFixed(1)} km`
      : `${Math.round(accuracy)} m`
    : null;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between border-b border-slate-100 pb-4 mb-5">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800">Weather Conditions</h3>
          <p className="mt-1 text-xs font-medium text-slate-500">
            Current atmospheric observations
          </p>
        </div>
        {location?.city && (
          <div className="text-right">
            <p className="text-sm font-medium text-slate-600">
              📍 {location.city}{location.state ? `, ${location.state}` : ""}
            </p>
            {typeof location.accuracy === "number" && (
              <p className="mt-1 text-xs text-slate-400">
                Location accuracy: ±{formattedAccuracy}
              </p>
            )}
          </div>
        )}
      </div>

      {status === "loading" ? (
        <p className="rounded-lg bg-slate-50 p-5 text-sm text-slate-500">
          {statusMessage || "Loading weather conditions..."}
        </p>
      ) : status === "unavailable" ? (
        <p className="rounded-lg bg-amber-50 p-5 text-sm text-amber-800">
          {statusMessage || "Weather data unavailable for this location."}
        </p>
      ) : status === "error" ? (
        <div className="rounded-lg bg-rose-50 p-5 text-sm text-rose-800">
          <p>{statusMessage || "Unable to load current weather."}</p>
          {onRetryLocation && (
            <button
              type="button"
              onClick={onRetryLocation}
              disabled={isRetrying}
              className="mt-3 rounded-lg bg-rose-700 px-3 py-2 text-xs font-semibold text-white transition hover:bg-rose-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isRetrying ? "Detecting location..." : "Retry Location"}
            </button>
          )}
        </div>
      ) : (
        <div>
          {isLowAccuracy && (
            <div className="mb-4 rounded-lg bg-amber-50 p-3 text-xs text-amber-800">
              Location accuracy is low (±{formattedAccuracy}). Enable GPS/location services for better accuracy.
              {isVeryLowAccuracy && onRetryLocation && (
                <button
                  type="button"
                  onClick={onRetryLocation}
                  disabled={isRetrying}
                  className="ml-2 font-semibold underline disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isRetrying ? "Detecting..." : "Retry Location"}
                </button>
              )}
            </div>
          )}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {conditions.map(({ label, value, icon }) => (
              <div
                key={label}
                className="flex items-center gap-4 rounded-xl border border-slate-100 bg-slate-50 p-4 transition-colors hover:border-slate-200 hover:bg-white"
              >
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white text-2xl shadow-sm border border-slate-100">
                  {icon}
                </span>
                <div className="min-w-0">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">{label}</p>
                  <p className="mt-0.5 truncate text-lg font-extrabold text-slate-900">{value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

export default WeatherConditions;
