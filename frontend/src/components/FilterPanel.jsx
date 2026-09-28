function FilterPanel({ filters, onFilterChange, onReset }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mt-6 transition-shadow hover:shadow-md">
      <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800">
            Weather Event Filters
          </h3>
          <p className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">
            Filter weather intelligence by date, event and location
          </p>
        </div>

        <button
          type="button"
          onClick={onReset}
          className="text-xs font-bold uppercase tracking-wider text-slate-500 hover:text-blue-600 bg-slate-50 hover:bg-blue-50 px-4 py-2 rounded-lg transition-colors border border-slate-200 hover:border-blue-200"
        >
          Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-5">
        {/* Date */}
        <div className="group">
          <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2 group-focus-within:text-blue-600 transition-colors">
            Date
          </label>
          <input
            type="date"
            value={filters.date}
            onChange={(event) => onFilterChange("date", event.target.value)}
            className="w-full font-medium text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 outline-none transition-all hover:border-slate-300 focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 cursor-pointer"
          />
        </div>

        {/* Event */}
        <div className="group">
          <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2 group-focus-within:text-blue-600 transition-colors">
            Event Type
          </label>
          <select
            value={filters.eventType}
            onChange={(event) => onFilterChange("eventType", event.target.value)}
            className="w-full font-medium text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 outline-none transition-all hover:border-slate-300 focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 cursor-pointer appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M5%208l5%205%205-5%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_0.75rem_center]"
          >
            <option value="">All Event Types</option>
            <option>Flood</option>
            <option>Heavy Rainfall</option>
            <option>Heatwave</option>
            <option>Thunderstorm</option>
            <option>Rainfall</option>
            <option>Fog</option>
            <option>Dust Storm</option>
            <option>Strong Winds</option>
          </select>
        </div>

        {/* State */}
        <div className="group">
          <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2 group-focus-within:text-blue-600 transition-colors">
            State
          </label>
          <select
            value={filters.state}
            onChange={(event) => onFilterChange("state", event.target.value)}
            className="w-full font-medium text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 outline-none transition-all hover:border-slate-300 focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 cursor-pointer appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M5%208l5%205%205-5%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_0.75rem_center]"
          >
            <option value="">All States</option>
            <option>Maharashtra</option>
            <option>Rajasthan</option>
            <option>Karnataka</option>
            <option>Assam</option>
          </select>
        </div>

        {/* Verification */}
        <div className="group">
          <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2 group-focus-within:text-blue-600 transition-colors">
            Verification
          </label>
          <select
            value={filters.verification}
            onChange={(event) => onFilterChange("verification", event.target.value)}
            className="w-full font-medium text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 outline-none transition-all hover:border-slate-300 focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 cursor-pointer appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M5%208l5%205%205-5%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_0.75rem_center]"
          >
            <option value="">All Status</option>
            <option>Verified</option>
            <option>Pending</option>
            <option>Suspicious</option>
          </select>
        </div>

        {/* Severity */}
        <div className="group">
          <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2 group-focus-within:text-blue-600 transition-colors">
            Severity
          </label>
          <select
            value={filters.severity}
            onChange={(event) => onFilterChange("severity", event.target.value)}
            className="w-full font-medium text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 outline-none transition-all hover:border-slate-300 focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 cursor-pointer appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M5%208l5%205%205-5%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[position:right_0.75rem_center]"
          >
            <option value="">All Severities</option>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </select>
        </div>

      </div>
    </div>
  );
}

export default FilterPanel;
