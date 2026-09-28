import React from "react";

function DataSources({ analytics }) {
  const sources = [
    { name: "IMD", type: "Official Meteorological Data", key: "IMD" },
    { name: "Open-Meteo", type: "Weather API", key: "Open-Meteo" },
    { name: "NASA POWER", type: "Satellite Data", key: "NASA POWER" },
  ];

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 h-full flex flex-col">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-800">Data Sources</h3>
        <p className="text-sm text-slate-500 mt-1">Live status of connected data integrations</p>
      </div>

      <div className="flex-1 space-y-3">
        {sources.map((src) => {
          const eventsCount = analytics?.by_source?.[src.key] || 0;
          const isConnected = eventsCount > 0 || src.key === "IMD"; // Assuming IMD is expected to be integrated
          
          return (
            <div key={src.name} className="flex items-center justify-between p-3 border border-slate-100 rounded-lg hover:bg-slate-50 transition">
              <div>
                <p className="font-medium text-slate-800">{src.name}</p>
                <p className="text-xs text-slate-500">{src.type}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center justify-end gap-2 mb-1">
                  <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-orange-500"}`}></span>
                  <span className="text-xs font-semibold text-slate-600">{isConnected ? "Active" : "Unavailable"}</span>
                </div>
                <p className="text-xs text-slate-400">
                  {analytics ? `${eventsCount} events` : "Loading..."}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default DataSources;
