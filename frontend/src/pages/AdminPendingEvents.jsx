import { useOutletContext } from "react-router-dom";
import AdminEventTable from "../components/AdminEventTable";

export default function AdminPendingEvents() {
  const { events, updateVerificationStatus } = useOutletContext();
  const pendingEvents = events.filter((event) => event.verification_status === "Pending");

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header>
        <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">Admin Console</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Pending Events</h1>
        <p className="mt-2 text-slate-500">Events awaiting verification.</p>
      </header>
      {pendingEvents.length ? (
        <AdminEventTable events={pendingEvents} onUpdateStatus={updateVerificationStatus} />
      ) : (
        <p className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500">No pending events.</p>
      )}
    </div>
  );
}
