import { useOutletContext } from "react-router-dom";
import AdminEventTable from "../components/AdminEventTable";

export default function AdminSuspiciousEvents() {
  const { events, updateVerificationStatus } = useOutletContext();
  const suspiciousEvents = events.filter((event) => event.verification_status === "Suspicious");

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header>
        <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">Admin Console</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Suspicious Events</h1>
        <p className="mt-2 text-slate-500">Events flagged for additional review.</p>
      </header>
      {suspiciousEvents.length ? (
        <AdminEventTable events={suspiciousEvents} onUpdateStatus={updateVerificationStatus} />
      ) : (
        <p className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500">No suspicious events.</p>
      )}
    </div>
  );
}
