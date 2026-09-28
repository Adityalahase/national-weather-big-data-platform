import { useOutletContext } from "react-router-dom";
import AdminEventTable from "../components/AdminEventTable";

function SummaryCard({ label, value, accent }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className={`mb-4 h-1.5 w-12 rounded-full ${accent}`} />
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-3xl font-bold tabular-nums text-slate-900">{value}</p>
    </div>
  );
}

export default function AdminPanel() {
  const { events, updateVerificationStatus } = useOutletContext();
  const summary = {
    total: events.length,
    verified: events.filter((event) => event.verification_status === "Verified").length,
    pending: events.filter((event) => event.verification_status === "Pending").length,
    suspicious: events.filter((event) => event.verification_status === "Suspicious").length,
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header>
        <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">National Weather Intelligence</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Admin Panel</h1>
        <p className="mt-2 text-slate-500">Weather event verification and platform management</p>
      </header>

      <section aria-label="Event summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Total Events" value={summary.total} accent="bg-slate-500" />
        <SummaryCard label="Verified Events" value={summary.verified} accent="bg-emerald-500" />
        <SummaryCard label="Pending Events" value={summary.pending} accent="bg-amber-500" />
        <SummaryCard label="Suspicious Events" value={summary.suspicious} accent="bg-rose-500" />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Event Verification</h2>
        <AdminEventTable events={events} onUpdateStatus={updateVerificationStatus} />
      </section>
    </div>
  );
}
