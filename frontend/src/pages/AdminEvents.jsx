import { useOutletContext } from "react-router-dom";
import AdminEventTable from "../components/AdminEventTable";

export default function AdminEvents() {
  const { events, updateVerificationStatus } = useOutletContext();

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header>
        <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">Admin Console</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Event Verification</h1>
        <p className="mt-2 text-slate-500">Review all weather events and update their verification status.</p>
      </header>
      <AdminEventTable events={events} onUpdateStatus={updateVerificationStatus} />
    </div>
  );
}
