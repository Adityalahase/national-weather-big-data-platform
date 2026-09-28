import { useState } from "react";

const STATUS_STYLES = {
  Verified: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  Pending: "bg-amber-50 text-amber-700 ring-amber-600/20",
  Suspicious: "bg-rose-50 text-rose-700 ring-rose-600/20",
};

const SEVERITY_STYLES = {
  Low: "bg-emerald-50 text-emerald-700",
  Medium: "bg-amber-50 text-amber-700",
  High: "bg-orange-50 text-orange-700",
  Critical: "bg-rose-50 text-rose-700",
};

export default function AdminEventTable({ events, onUpdateStatus }) {
  const [selectedEvent, setSelectedEvent] = useState(null);

  return (
    <>
      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left">
            <thead className="bg-slate-50">
              <tr>
                {["ID", "Event Type", "Location", "Severity", "Confidence", "Status", "Timestamp", "Action"].map((heading) => (
                  <th key={heading} scope="col" className="whitespace-nowrap px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-slate-50/80">
                  <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold text-slate-800">#{event.id}</td>
                  <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-slate-700">{event.event_type}</td>
                  <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">{event.city}, {event.state}</td>
                  <td className="whitespace-nowrap px-5 py-4"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${SEVERITY_STYLES[event.severity] || "bg-slate-100 text-slate-700"}`}>{event.severity}</span></td>
                  <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold tabular-nums text-slate-700">{event.confidence_score}%</td>
                  <td className="whitespace-nowrap px-5 py-4"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${STATUS_STYLES[event.verification_status] || "bg-slate-100 text-slate-700 ring-slate-200"}`}>{event.verification_status}</span></td>
                  <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">{event.timestamp}</td>
                  <td className="px-5 py-4">
                    <div className="flex min-w-max items-center gap-2">
                      <button type="button" onClick={() => setSelectedEvent(event)} className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-50">View</button>
                      <button type="button" onClick={() => onUpdateStatus(event.id, "Verified")} className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-700">Verify</button>
                      <button type="button" onClick={() => onUpdateStatus(event.id, "Suspicious")} className="rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-rose-700">Mark Suspicious</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {selectedEvent && (
        <section className="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <h2 className="text-lg font-semibold text-slate-900">Selected Event Details</h2>
          <p className="mt-1 text-sm text-slate-500">Event #{selectedEvent.id}: {selectedEvent.event_type}</p>
          <dl className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div><dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Location</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{selectedEvent.city}, {selectedEvent.state}</dd></div>
            <div><dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Severity</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{selectedEvent.severity}</dd></div>
            <div><dt className="text-xs font-medium uppercase tracking-wide text-slate-400">AI Confidence</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{selectedEvent.confidence_score}%</dd></div>
            <div><dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Timestamp</dt><dd className="mt-1 text-sm font-semibold text-slate-700">{selectedEvent.timestamp}</dd></div>
          </dl>
        </section>
      )}
    </>
  );
}
