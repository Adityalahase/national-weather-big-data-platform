import SourceReliability from "./SourceReliability";

function EventIntelligence({ event }) {
  if (!event) {
    return (
      <div
        id="event-intelligence"
        className="flex h-[700px] flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="mb-5 flex shrink-0 items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-800">
              Event Intelligence
            </h3>
            <p className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">
              Analysis Dashboard
            </p>
          </div>
        </div>
        <div className="flex flex-1 flex-col items-center justify-center text-slate-400">
          <div className="w-16 h-16 rounded-full bg-slate-50 border border-slate-100 flex items-center justify-center mb-4 text-2xl shadow-inner">
            🔍
          </div>
          <p className="font-medium text-slate-500">Select a weather event to view intelligence</p>
        </div>
      </div>
    );
  }

  // Calculate Risk Score
  let riskScore = 0;

  if (event.severity === "High" || event.severity === "Critical") {
    riskScore = 90;
  } else if (event.severity === "Medium") {
    riskScore = 60;
  } else {
    riskScore = 30;
  }

  // Adjust using AI confidence
  riskScore = Math.round(
    riskScore * (event.confidence_score / 100)
  );

  const riskLabel = riskScore >= 75 ? "High Risk" : riskScore >= 40 ? "Medium Risk" : "Low Risk";
  const riskColor = riskScore >= 75 ? "text-rose-600" : riskScore >= 40 ? "text-amber-600" : "text-emerald-600";
  const riskBarColor = riskScore >= 75 ? "bg-rose-500" : riskScore >= 40 ? "bg-amber-500" : "bg-emerald-500";
  const riskBgColor = riskScore >= 75 ? "bg-rose-50 border-rose-100" : riskScore >= 40 ? "bg-amber-50 border-amber-100" : "bg-emerald-50 border-emerald-100";

  return (
    <div
      id="event-intelligence"
      className="flex h-[700px] flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      {/* Header */}
      <div className="mb-5 flex shrink-0 items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800">
            Event Intelligence
          </h3>
          <p className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">
            Detailed analysis of selected event
          </p>
        </div>
        <span
          className={`px-3 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest border ${event.verification_status === "Verified"
            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
            : event.verification_status === "Pending"
              ? "bg-amber-50 text-amber-700 border-amber-200"
              : "bg-rose-50 text-rose-700 border-rose-200"
            }`}
        >
          {event.verification_status}
        </span>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pr-2 custom-scrollbar">
        {/* Event Title */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 mb-5 relative">
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-2">
              <span className={`w-2 h-2 rounded-full ${event.severity === "High" || event.severity === "Critical" ? "bg-rose-500" : event.severity === "Medium" ? "bg-amber-500" : "bg-emerald-500"
                }`}></span>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Selected Event</p>
            </div>
            <h2 className="text-xl font-bold text-slate-800">
              {event.event_type}
            </h2>
            <p className="text-sm text-slate-600 mt-1 font-medium">
              Location: {event.city}, {event.state}
            </p>
          </div>
        </div>

        {/* Risk + Confidence */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
          {/* Risk Score */}
          <div className={`border rounded-lg p-4 relative ${riskBgColor}`}>
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Calculated Risk
            </p>
            <div className="flex items-baseline gap-1 mt-2">
              <h2 className={`text-2xl font-bold ${riskColor}`}>
                {riskScore}
              </h2>
              <span className="text-xs font-medium text-slate-500">
                / 100
              </span>
            </div>
            <p className={`text-xs font-semibold mt-0.5 ${riskColor}`}>{riskLabel}</p>
            <div className="w-full bg-slate-200 rounded-full h-1 mt-3">
              <div
                className={`h-full rounded-full ${riskBarColor}`}
                style={{ width: `${riskScore}%` }}
              ></div>
            </div>
          </div>

          {/* AI Confidence */}
          <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Analysis Confidence
            </p>
            <div className="flex items-baseline gap-1 mt-2">
              <h2 className="text-2xl font-bold text-blue-700">
                {event.confidence_score}
              </h2>
              <span className="text-xs font-medium text-slate-500">
                %
              </span>
            </div>
            <p className="text-xs font-semibold mt-0.5 text-blue-600">Model Certainty</p>
            <div className="w-full bg-blue-200 rounded-full h-1 mt-3">
              <div
                className="bg-blue-600 h-full rounded-full"
                style={{ width: `${event.confidence_score}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* AI Insight */}
        <div className="mb-5 bg-slate-50 border border-slate-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-700">
              Intelligence Summary
            </h4>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed">
            This <strong>{event.event_type.toLowerCase()}</strong> event reported in{" "}
            <strong>{event.city}, {event.state}</strong> has been analyzed with an interpretation confidence
            of <strong>{event.confidence_score}%</strong>. The current calculated
            risk profile indicates a <strong>{riskLabel.toLowerCase()}</strong> scenario (Score: {riskScore}/100).
          </p>
        </div>

        {/* Event Information */}
        <div className="border border-slate-200 rounded-xl p-5 shadow-sm mb-5 bg-white">
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-800 mb-4 pb-2 border-b border-slate-100">
            Event Metadata
          </h4>
          <div className="grid grid-cols-2 gap-y-4 gap-x-2">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Event ID</p>
              <p className="text-sm font-semibold text-slate-700 mt-0.5 font-mono">{event.id}</p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Severity</p>
              <p className="text-sm font-semibold text-slate-700 mt-0.5">{event.severity}</p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Coordinates</p>
              <p className="text-sm font-semibold text-slate-700 mt-0.5 font-mono">
                {event.latitude.toFixed(2)}, {event.longitude.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Timestamp</p>
              <p className="text-sm font-semibold text-slate-700 mt-0.5">
                {new Date(event.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Verification</p>
              <p className="text-sm font-semibold text-slate-700 mt-0.5">{event.verification_status}</p>
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Source</p>
              <p className="text-sm font-semibold text-slate-700 mt-0.5">{event.source || "Unknown"}</p>
            </div>
          </div>
        </div>

        <div className="mb-5">
          <SourceReliability event={event} />
        </div>

        {/* Event Timeline */}
        <div className="border border-slate-200 bg-slate-50/50 rounded-xl p-5 shadow-sm">
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-800 mb-5">Audit Trail</h4>
          <div className="relative pl-3">
            <div className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-slate-200"></div>

            <div className="relative flex gap-4 mb-6 group">
              <div className="relative z-10 w-8 h-8 rounded-full bg-blue-100 border-4 border-white shadow-sm flex items-center justify-center text-blue-600 ring-1 ring-blue-200 group-hover:scale-110 transition-transform">
                <div className="w-2.5 h-2.5 bg-blue-600 rounded-full"></div>
              </div>
              <div className="flex-1 pb-1 pt-1">
                <h5 className="text-sm font-bold text-slate-800">Event Reported</h5>
                <p className="text-xs font-medium text-slate-500 mt-0.5">Weather event received by platform</p>
                <p className="text-[10px] font-bold tracking-wider text-slate-400 mt-1 uppercase">{new Date(event.timestamp).toLocaleString()}</p>
              </div>
            </div>

            <div className="relative flex gap-4 mb-6 group">
              <div className="relative z-10 w-8 h-8 rounded-full bg-indigo-100 border-4 border-white shadow-sm flex items-center justify-center text-indigo-600 ring-1 ring-indigo-200 group-hover:scale-110 transition-transform">
                <div className="w-2.5 h-2.5 bg-indigo-600 rounded-full"></div>
              </div>
              <div className="flex-1 pb-1 pt-1">
                <h5 className="text-sm font-bold text-slate-800">AI Analysis</h5>
                <p className="text-xs font-medium text-slate-500 mt-0.5">Confidence score generated: {event.confidence_score}%</p>
              </div>
            </div>

            <div className="relative flex gap-4 mb-6 group">
              <div className="relative z-10 w-8 h-8 rounded-full bg-amber-100 border-4 border-white shadow-sm flex items-center justify-center text-amber-600 ring-1 ring-amber-200 group-hover:scale-110 transition-transform">
                <div className="w-2.5 h-2.5 bg-amber-500 rounded-full"></div>
              </div>
              <div className="flex-1 pb-1 pt-1">
                <h5 className="text-sm font-bold text-slate-800">Verification</h5>
                <p className="text-xs font-medium text-slate-500 mt-0.5">Report evaluated for credibility</p>
              </div>
            </div>

            <div className="relative flex gap-4 group">
              <div className={`relative z-10 w-8 h-8 rounded-full border-4 border-white shadow-sm flex items-center justify-center ring-1 transition-transform group-hover:scale-110 ${event.verification_status === "Verified"
                ? "bg-emerald-100 text-emerald-600 ring-emerald-200"
                : event.verification_status === "Suspicious"
                  ? "bg-rose-100 text-rose-600 ring-rose-200"
                  : "bg-amber-100 text-amber-600 ring-amber-200"
                }`}
              >
                <div className={`w-2.5 h-2.5 rounded-full ${event.verification_status === "Verified" ? "bg-emerald-500" : event.verification_status === "Suspicious" ? "bg-rose-500" : "bg-amber-500"
                  }`}></div>
              </div>
              <div className="flex-1 pb-1 pt-1">
                <h5 className="text-sm font-bold text-slate-800">Final Status</h5>
                <p className="text-xs font-bold mt-0.5 uppercase tracking-wider text-slate-600">{event.verification_status}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EventIntelligence;
