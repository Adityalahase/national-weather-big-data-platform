import React, { useEffect, useState } from "react";
import { getPipelineStatus } from "../services/api";

function PipelineMonitor() {
  const [pipelineData, setPipelineData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getPipelineStatus();
        setPipelineData(data);
      } catch (err) {
        console.error("Failed to fetch pipeline status", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 h-full flex flex-col justify-center items-center">
        <p className="text-slate-400">Loading Pipeline Monitor...</p>
      </div>
    );
  }

  if (!pipelineData) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 h-full">
        <h3 className="text-lg font-semibold text-slate-800 mb-1">Pipeline Monitor</h3>
        <p className="text-sm text-slate-500">Pipeline status is currently unavailable.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 h-full flex flex-col">
      <div className="mb-4 flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold text-slate-800">Pipeline Monitor</h3>
          <p className="text-sm text-slate-500 mt-1">Data processing stages and status</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${pipelineData.overall_status === 'Running' ? 'bg-blue-400' : 'bg-green-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${pipelineData.overall_status === 'Running' ? 'bg-blue-500' : 'bg-green-500'}`}></span>
          </span>
          <span className="text-xs font-semibold text-slate-600">{pipelineData.overall_status}</span>
        </div>
      </div>

      <div className="flex-1 overflow-x-auto">
        <div className="flex items-center min-w-max space-x-2 py-2">
          {pipelineData.stages.map((stage, index) => (
            <React.Fragment key={stage.name}>
              <div className="flex flex-col border border-slate-100 rounded-lg p-3 bg-slate-50 w-40 shrink-0">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-slate-700">{stage.name}</span>
                  <span className="text-xs text-green-600 font-medium">{stage.status}</span>
                </div>
                {Object.entries(stage.metrics || {}).map(([key, val]) => (
                  <div key={key} className="text-xs text-slate-500 mt-1 flex justify-between">
                    <span>{key}</span>
                    <span className="font-semibold text-slate-700">{val}</span>
                  </div>
                ))}
              </div>
              {index < pipelineData.stages.length - 1 && (
                <div className="text-slate-300">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}

export default PipelineMonitor;
