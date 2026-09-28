function StatCard({ title, value, icon, description }) {
  return (
    <div className="group relative overflow-hidden bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:border-slate-300 hover:shadow-md transition-all duration-200">
      <div className="flex items-start justify-between relative z-10">
        <div className="flex-1">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            {title}
          </p>
          <h2 className="text-4xl font-extrabold text-slate-800 mt-3 tracking-tight group-hover:text-slate-900 transition-colors">
            {value}
          </h2>
          <p className="text-xs font-medium text-slate-400 mt-2">
            {description}
          </p>
        </div>
        <div className="w-12 h-12 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center text-2xl group-hover:bg-slate-100 transition-colors shrink-0">
          {icon}
        </div>
      </div>
    </div>
  );
}

export default StatCard;