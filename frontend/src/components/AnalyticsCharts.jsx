const CHART_COLORS = [
  "#0f766e",
  "#0284c7",
  "#7c3aed",
  "#d97706",
  "#e11d48",
  "#4f46e5",
];

const SEVERITY_COLORS = {
  Low: "#16a34a",
  Medium: "#d97706",
  High: "#dc2626",
  Critical: "#7f1d1d",
};

const STATUS_COLORS = {
  Verified: "#16a34a",
  Pending: "#d97706",
  Suspicious: "#dc2626",
  Rejected: "#64748b",
};

function getDistribution(events, field) {
  return events.reduce((counts, event) => {
    const label = event[field] || "Unknown";
    counts[label] = (counts[label] || 0) + 1;
    return counts;
  }, {});
}

function toChartData(distribution) {
  return Object.entries(distribution)
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value || a.label.localeCompare(b.label));
}

function EmptyChart() {
  return (
    <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500">
      No weather events available
    </div>
  );
}

function HorizontalBarChart({ data, colors = CHART_COLORS }) {
  if (!data.length) return <EmptyChart />;

  const maximum = Math.max(...data.map(({ value }) => value), 1);

  return (
    <div className="space-y-4">
      {data.map(({ label, value }, index) => (
        <div key={label} className="space-y-1.5">
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="truncate font-medium text-slate-700" title={label}>
              {label}
            </span>
            <span className="shrink-0 font-semibold tabular-nums text-slate-900">{value}</span>
          </div>
          <div
            className="h-2.5 overflow-hidden rounded-full bg-slate-100"
            role="progressbar"
            aria-label={`${label}: ${value} events`}
            aria-valuemin={0}
            aria-valuemax={maximum}
            aria-valuenow={value}
          >
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${(value / maximum) * 100}%`,
                backgroundColor: colors[index % colors.length],
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function DistributionChart({ data, colorMap }) {
  if (!data.length) return <EmptyChart />;

  const total = data.reduce((sum, { value }) => sum + value, 0);
  let cursor = 0;
  const segments = data.map(({ label, value }, index) => {
    const start = cursor;
    cursor += (value / total) * 100;
    return `${colorMap[label] || CHART_COLORS[index % CHART_COLORS.length]} ${start}% ${cursor}%`;
  });

  return (
    <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
      <div
        className="relative grid h-36 w-36 shrink-0 place-items-center rounded-full"
        style={{ background: `conic-gradient(${segments.join(", ")})` }}
        role="img"
        aria-label={data.map(({ label, value }) => `${label}: ${value}`).join(", ")}
      >
        <div className="grid h-24 w-24 place-items-center rounded-full bg-white text-center shadow-sm">
          <span className="text-2xl font-bold tabular-nums text-slate-900">{total}</span>
          <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Events</span>
        </div>
      </div>

      <ul className="w-full space-y-3">
        {data.map(({ label, value }, index) => {
          const color = colorMap[label] || CHART_COLORS[index % CHART_COLORS.length];
          return (
            <li key={label} className="flex items-center justify-between gap-3 text-sm">
              <span className="flex min-w-0 items-center gap-2 text-slate-600">
                <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: color }} />
                <span className="truncate">{label}</span>
              </span>
              <span className="shrink-0 font-semibold tabular-nums text-slate-900">
                {value} <span className="font-normal text-slate-500">({Math.round((value / total) * 100)}%)</span>
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function ChartCard({ title, subtitle, children }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="mb-6">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
      </div>
      {children}
    </section>
  );
}

/**
 * Reusable dashboard analytics generated from weather-event fields.
 * No chart package is required; charts use accessible, dependency-free React markup.
 */
export default function AnalyticsCharts({ analytics }) {
  if (!analytics) return null;

  const eventTypes = toChartData(analytics.by_event_type || {});
  const states = toChartData(analytics.by_state || {});
  
  const statusesData = {
    Verified: analytics.verified || 0,
    Pending: analytics.pending || 0,
    Suspicious: analytics.suspicious || 0,
    Rejected: analytics.rejected || 0,
  };
  Object.keys(statusesData).forEach(k => {
    if (statusesData[k] === 0) delete statusesData[k];
  });
  const statuses = toChartData(statusesData);
  
  const severities = toChartData(analytics.by_severity || {});

  return (
    <section aria-labelledby="analytics-heading" className="space-y-6">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">National Weather Intelligence</p>
          <h2 id="analytics-heading" className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
            Analytics Overview
          </h2>
        </div>
        <p className="text-sm text-slate-500">Based on {analytics.total_events || 0} recorded weather event{(analytics.total_events || 0) === 1 ? "" : "s"}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard title="Weather Events by Event Type" subtitle="Distribution of recorded weather hazards">
          <HorizontalBarChart data={eventTypes} />
        </ChartCard>

        <ChartCard title="Weather Events by State" subtitle="Geographic distribution of recorded events">
          <HorizontalBarChart data={states} colors={["#0369a1", "#0f766e", "#4f46e5", "#b45309", "#be123c"]} />
        </ChartCard>

        <ChartCard title="Verification Status Distribution" subtitle="Current validation status of weather events">
          <DistributionChart data={statuses} colorMap={STATUS_COLORS} />
        </ChartCard>

        <ChartCard title="Severity Distribution" subtitle="Event severity across the monitoring network">
          <DistributionChart data={severities} colorMap={SEVERITY_COLORS} />
        </ChartCard>
      </div>
    </section>
  );
}
