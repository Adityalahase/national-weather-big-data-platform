function IncidentFeed({ events, onSelectEvent, selectedEvent }) {
  return (
    <div className="flex h-[700px] flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      {/* Header */}
      <div className="mb-5 flex shrink-0 items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800">
            Live Incident Feed
          </h3>
          <p className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">
            Latest weather-related events
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-rose-600 bg-rose-50 px-3 py-1.5 rounded-full">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
          LIVE
        </div>
      </div>

      {/* Events */}
      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto pr-2 custom-scrollbar">
        {events.map((event) => (
          <button
            key={event.id}
            onClick={() => onSelectEvent(event)}
            className={`w-full text-left p-4 rounded-xl border transition-all duration-200 group ${selectedEvent?.id === event.id
              ? "border-blue-500 bg-blue-50 shadow-sm ring-1 ring-blue-500/20"
              : "border-slate-200 hover:border-blue-300 hover:bg-slate-50 hover:shadow-sm"
              }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex gap-3">
                {/* Severity indicator */}
                <div
                  className={`mt-1 flex shrink-0 h-3 w-3 rounded-full shadow-inner ${event.severity === "High" || event.severity === "Critical"
                    ? "bg-rose-500"
                    : event.severity === "Medium"
                      ? "bg-amber-500"
                      : "bg-emerald-500"
                    }`}
                ></div>
                <div>
                  <p className="font-bold text-slate-800 group-hover:text-blue-700 transition-colors">
                    {event.event_type}
                  </p>
                  <p className="text-xs font-medium text-slate-500 mt-0.5">
                    {event.city}, {event.state}
                  </p>
                </div>
              </div>

              <div className="text-right flex flex-col items-end">
                <p className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                  {new Date(event.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
                <p className="text-[10px] font-medium text-slate-400 mt-1 uppercase">
                  ID: {event.id}
                </p>
              </div>
            </div>

            {/* Status & Confidence */}
            <div className="mt-4 flex items-center justify-between border-t border-slate-100/50 pt-3">
              <div className="flex items-center gap-2">
                <span
                  className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md ${event.verification_status === "Verified"
                    ? "bg-emerald-100 text-emerald-700 border border-emerald-200"
                    : event.verification_status === "Pending"
                      ? "bg-amber-100 text-amber-700 border border-amber-200"
                      : event.verification_status === "Suspicious"
                        ? "bg-rose-100 text-rose-700 border border-rose-200"
                        : "bg-slate-100 text-slate-700 border border-slate-200"
                    }`}
                >
                  {event.verification_status}
                </span>

                <span
                  className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md ${event.severity === "High" || event.severity === "Critical"
                    ? "bg-rose-50 text-rose-600 border border-rose-100"
                    : event.severity === "Medium"
                      ? "bg-amber-50 text-amber-600 border border-amber-100"
                      : "bg-slate-50 text-slate-600 border border-slate-100"
                    }`}
                >
                  {event.severity}
                </span>
              </div>

              <span className="text-xs font-bold text-slate-500 flex items-center gap-1">
                <span className="text-blue-500 shrink-0">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </span>
                Conf: {event.confidence_score}%
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default IncidentFeed;
