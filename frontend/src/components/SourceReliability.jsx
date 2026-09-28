const RELIABILITY_STYLES = {
  "High Reliability": {
    badge: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    bar: "bg-emerald-500",
    dot: "bg-emerald-500",
  },
  "Moderate Reliability": {
    badge: "bg-amber-50 text-amber-700 ring-amber-600/20",
    bar: "bg-amber-500",
    dot: "bg-amber-500",
  },
  "Pending Verification": {
    badge: "bg-sky-50 text-sky-700 ring-sky-600/20",
    bar: "bg-sky-500",
    dot: "bg-sky-500",
  },
  "Low Reliability": {
    badge: "bg-rose-50 text-rose-700 ring-rose-600/20",
    bar: "bg-rose-500",
    dot: "bg-rose-500",
  },
};

function getReliabilityAssessment(event) {
  const confidence = Number(event.confidence_score) || 0;

  if (event.verification_status === "Verified") {
    if (confidence >= 80) {
      return {
        label: "High Reliability",
        explanation: "This event is verified and has a high platform confidence score.",
      };
    }

    return {
      label: "Moderate Reliability",
      explanation: "This event is verified, but its platform confidence score is below 80%.",
    };
  }

  if (event.verification_status === "Pending") {
    return {
      label: "Pending Verification",
      explanation: "This event is awaiting verification; its confidence score is shown for assessment.",
    };
  }

  return {
    label: "Low Reliability",
    explanation: "This event is marked suspicious and requires additional validation.",
  };
}

export default function SourceReliability({ event }) {
  if (!event) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <h3 className="text-lg font-semibold text-slate-800">Reliability Assessment</h3>
        <p className="mt-4 rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
          Select a weather event to view its reliability assessment.
        </p>
      </section>
    );
  }

  const confidence = Math.min(100, Math.max(0, Number(event.confidence_score) || 0));
  const assessment = getReliabilityAssessment(event);
  const styles = RELIABILITY_STYLES[assessment.label];

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">Source Reliability</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-800">Reliability Assessment</h3>
          <p className="mt-1 text-sm text-slate-500">Based on the platform verification status and confidence score.</p>
        </div>
        <span className={`inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ring-1 ring-inset ${styles.badge}`}>
          <span className={`h-2 w-2 rounded-full ${styles.dot}`} />
          {assessment.label}
        </span>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <div className="rounded-lg bg-slate-50 p-4">
          <p className="text-sm font-medium text-slate-500">Confidence Score</p>
          <p className="mt-1 text-3xl font-bold tabular-nums text-slate-900">{confidence}%</p>
        </div>
        <div className="rounded-lg bg-slate-50 p-4">
          <p className="text-sm font-medium text-slate-500">Verification Status</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">{event.verification_status}</p>
        </div>
      </div>

      <div className="mt-6">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-medium text-slate-700">Reliability indicator</span>
          <span className="font-semibold tabular-nums text-slate-900">{confidence}%</span>
        </div>
        <div
          className="h-2.5 overflow-hidden rounded-full bg-slate-100"
          role="progressbar"
          aria-label="Event reliability confidence score"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={confidence}
        >
          <div className={`h-full rounded-full transition-all duration-500 ${styles.bar}`} style={{ width: `${confidence}%` }} />
        </div>
      </div>

      <p className="mt-5 border-l-4 border-slate-200 pl-4 text-sm leading-6 text-slate-600">
        {assessment.explanation}
      </p>
    </section>
  );
}
