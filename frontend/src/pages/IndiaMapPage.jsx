import { useEffect, useMemo, useState } from "react";
import EventIntelligence from "../components/EventIntelligence";
import IndiaMap from "../components/IndiaMap";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import TimelineSlider from "../components/TimelineSlider";
import { getEvents } from "../services/api";

export default function IndiaMapPage() {
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [weatherEvents, setWeatherEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await getEvents();
        setWeatherEvents(data);
      } catch (error) {
        console.error("Failed to fetch events:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  const sortedEvents = useMemo(() => (
    [...weatherEvents].sort((firstEvent, secondEvent) => (
      new Date(firstEvent.timestamp).getTime() - new Date(secondEvent.timestamp).getTime()
    ))
  ), [weatherEvents]);

  const earliestTime = sortedEvents.length > 0 ? new Date(sortedEvents[0].timestamp).getTime() : Date.now();
  const latestTime = sortedEvents.length > 0 ? new Date(sortedEvents[sortedEvents.length - 1].timestamp).getTime() : Date.now();
  const [currentTime, setCurrentTime] = useState(earliestTime);

  useEffect(() => {
    if (sortedEvents.length > 0) {
      setCurrentTime(new Date(sortedEvents[0].timestamp).getTime());
    }
  }, [sortedEvents]);

  const visibleEvents = sortedEvents.filter((event) => (
    new Date(event.timestamp).getTime() <= currentTime
  ));

  useEffect(() => {
    if (!isPlaying) return undefined;

    const timeRange = latestTime - earliestTime;
    const step = Math.max(1000, Math.ceil(timeRange / 100));
    const intervalId = window.setInterval(() => {
      setCurrentTime((time) => {
        const nextTime = Math.min(time + step, latestTime);

        if (nextTime >= latestTime) {
          setIsPlaying(false);
        }

        return nextTime;
      });
    }, 250);

    return () => window.clearInterval(intervalId);
  }, [earliestTime, latestTime, isPlaying]);

  const handlePlay = () => {
    if (currentTime >= latestTime) setCurrentTime(earliestTime);
    setIsPlaying(true);
  };

  const handleTimeChange = (time) => {
    setCurrentTime(time);
    setIsPlaying(false);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentTime(earliestTime);
  };

  const handleSelectEvent = (event) => {
    setSelectedEvent(event);

    setTimeout(() => {
      document.getElementById("event-intelligence")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 100);
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
              <h1 className="mt-1 text-2xl font-bold text-slate-800">India Weather Map</h1>
              <p className="mt-1 text-slate-500">Interactive visualization of weather events across India</p>
            </header>

            <IndiaMap
              events={visibleEvents}
              onSelectEvent={handleSelectEvent}
              timeline={(
                <TimelineSlider
                  currentTime={currentTime}
                  earliestTime={earliestTime}
                  latestTime={latestTime}
                  isPlaying={isPlaying}
                  currentEventCount={visibleEvents.length}
                  totalEventCount={sortedEvents.length}
                  onTimeChange={handleTimeChange}
                  onPlay={handlePlay}
                  onPause={() => setIsPlaying(false)}
                  onReset={handleReset}
                />
              )}
            />

            <div id="event-intelligence">
              {selectedEvent ? (
                <EventIntelligence event={selectedEvent} />
              ) : (
                <section className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
                  <h2 className="text-lg font-semibold text-slate-800">Event Intelligence</h2>
                  <p className="mt-2 text-sm text-slate-500">Select a weather event on the map to view intelligence.</p>
                </section>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
