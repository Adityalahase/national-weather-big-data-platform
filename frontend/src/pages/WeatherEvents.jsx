import { useEffect, useState } from "react";
import EventIntelligence from "../components/EventIntelligence";
import FilterPanel from "../components/FilterPanel";
import IncidentFeed from "../components/IncidentFeed";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import { getEvents } from "../services/api";

const STATUS_STYLES = {
  Verified: "bg-emerald-50 text-emerald-700",
  Pending: "bg-amber-50 text-amber-700",
  Suspicious: "bg-rose-50 text-rose-700",
};

export default function WeatherEvents() {
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [weatherEvents, setWeatherEvents] = useState([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState("");
  const [filters, setFilters] = useState({
    date: "",
    eventType: "",
    state: "",
    verification: "",
    severity: "",
  });
  useEffect(() => {
    const loadEvents = async () => {
      try {
        setEventsLoading(true);
        setEventsError("");

        const events = await getEvents();
        setWeatherEvents(events);
      } catch (error) {
        console.error("[EVENTS] Failed to load backend events:", error);
        setEventsError("Unable to load weather events from backend.");
      } finally {
        setEventsLoading(false);
      }
    };

    loadEvents();
  }, []);
  const filteredEvents = weatherEvents.filter((event) => (
    (!filters.date || event.timestamp.slice(0, 10) === filters.date)
    && (!filters.eventType || event.event_type === filters.eventType)
    && (!filters.state || event.state === filters.state)
    && (!filters.verification || event.verification_status === filters.verification)
    && (!filters.severity || event.severity === filters.severity)
  ));

  useEffect(() => {
    if (selectedEvent && !filteredEvents.some((event) => event.id === selectedEvent.id)) {
      setSelectedEvent(null);
    }
  }, [filteredEvents, selectedEvent]);

  const handleFilterChange = (filterName, value) => {
    setFilters((currentFilters) => ({ ...currentFilters, [filterName]: value }));
  };

  const resetFilters = () => {
    setFilters({ date: "", eventType: "", state: "", verification: "", severity: "" });
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1 p-6">
          <div className="mx-auto max-w-7xl space-y-6">
            <header>
              <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">National Weather Intelligence</p>
              <h1 className="mt-1 text-2xl font-bold text-slate-800">Weather Events</h1>
              <p className="mt-1 text-slate-500">Monitor, filter and investigate weather events across India.</p>
            </header>

            <FilterPanel
              filters={filters}
              onFilterChange={handleFilterChange}
              onReset={resetFilters}
            />

            <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 px-5 py-5">
                <h2 className="text-lg font-semibold text-slate-800">Weather Event List</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Showing {filteredEvents.length} of {weatherEvents.length} recorded weather events
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-left">
                  <thead className="bg-slate-50">
                    <tr>
                      {['ID', 'Event Type', 'City', 'State', 'Severity', 'AI Confidence', 'Verification Status', 'Timestamp'].map((heading) => (
                        <th key={heading} scope="col" className="whitespace-nowrap px-5 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">{heading}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredEvents.map((event) => (
                      <tr key={event.id} onClick={() => setSelectedEvent(event)} className="cursor-pointer transition hover:bg-slate-50">
                        <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold text-slate-800">#{event.id}</td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-slate-700">{event.event_type}</td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">{event.city}</td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">{event.state}</td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-slate-700">{event.severity}</td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold tabular-nums text-slate-700">{event.confidence_score}%</td>
                        <td className="whitespace-nowrap px-5 py-4"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${STATUS_STYLES[event.verification_status] || "bg-slate-100 text-slate-700"}`}>{event.verification_status}</span></td>
                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">{event.timestamp}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <div className="grid gap-6 xl:grid-cols-2">
              <IncidentFeed events={filteredEvents} onSelectEvent={setSelectedEvent} selectedEvent={selectedEvent} />
              <EventIntelligence event={selectedEvent} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
