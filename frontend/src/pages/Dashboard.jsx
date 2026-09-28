import { useEffect, useRef, useState } from "react";



import { Link } from "react-router-dom";

import Navbar from "../components/Navbar";

import Sidebar from "../components/Sidebar";

import StatCard from "../components/StatCard";

import IncidentFeed from "../components/IncidentFeed";

import EventIntelligence from "../components/EventIntelligence";

import WeatherConditions from "../components/WeatherConditions";

import DataSources from "../components/DataSources";

import PipelineMonitor from "../components/PipelineMonitor";



import {

  getLocationByQuery,

  getCurrentWeather,

  getWeatherByLocation,

  getWeatherForEvent,

} from "../services/weatherService";

import { getCurrentLocation, getLocationName } from "../services/locationService";

import { getEvents, getAnalytics } from "../services/api";



function Dashboard() {

  const [selectedEvent, setSelectedEvent] = useState(null);

  const [weatherEvents, setWeatherEvents] = useState([]);

  const [analytics, setAnalytics] = useState(null);

  const [eventsLoading, setEventsLoading] = useState(true);

  const [eventsError, setEventsError] = useState("");

  const [date, setDate] = useState("");

  const [eventType, setEventType] = useState("");

  const [state, setState] = useState("");

  const [verification, setVerification] = useState("");

  const [severity, setSeverity] = useState("");

  const [filterPanelKey, setFilterPanelKey] = useState(0);

  const [selectedLocation, setSelectedLocation] = useState(null);

  const [selectedWeather, setSelectedWeather] = useState(null);

  const [weatherStatus, setWeatherStatus] = useState("loading");

  const [locationQuery, setLocationQuery] = useState("");

  const [locationMessage, setLocationMessage] = useState("");

  const [weatherStatusMessage, setWeatherStatusMessage] = useState("Detecting current location...");

  const [isRetryingLocation, setIsRetryingLocation] = useState(false);

  const locationRequestRef = useRef(null);



  useEffect(() => {

    const loadEvents = async () => {

      try {

        setEventsLoading(true);

        setEventsError("");



        const [events, stats] = await Promise.all([

          getEvents(),

          getAnalytics()

        ]);

        setWeatherEvents(events);

        setAnalytics(stats);

      } catch (error) {

        console.error("[EVENTS] Failed to load backend events:", error);

        setEventsError("Unable to load weather events from backend.");

      } finally {

        setEventsLoading(false);

      }

    };



    loadEvents();

  }, []);

  const filters = { date, eventType, state, verification, severity };



  const filteredEvents = weatherEvents.filter((event) => (

    (!date || event.timestamp.slice(0, 10) === date)

    && (!eventType || event.event_type === eventType)

    && (!state || event.state === state)

    && (!verification || event.verification_status === verification)

    && (!severity || event.severity === severity)

  ));



  useEffect(() => {

    if (selectedEvent && !filteredEvents.some((event) => event.id === selectedEvent.id)) {

      setSelectedEvent(null);

    }

  }, [filteredEvents, selectedEvent]);



  useEffect(() => {

    let isActive = true;



    const loadCurrentWeather = async () => {

      console.log("[LOCATION] requesting browser location");

      console.log("[LOCATION] geolocation supported:", typeof navigator.geolocation);

      console.log("[LOCATION] secure context:", window.isSecureContext);



      const setLocationError = (message) => {

        setSelectedLocation({

          city: "Current location",

          latitude: null,

          longitude: null,

          accuracy: null,

        });

        setSelectedWeather(null);

        setWeatherStatus("error");

        setWeatherStatusMessage(message);

        setIsRetryingLocation(false);

        console.error("[LOCATION] error:", message);

      };



      try {

        const { coords } = await getCurrentLocation();

        if (!isActive) return;

        console.log("[LOCATION] success");

        console.log("[LOCATION] latitude:", coords.latitude);

        console.log("[LOCATION] longitude:", coords.longitude);

        console.log("[LOCATION] accuracy:", coords.accuracy);

        setSelectedLocation({

          city: "Current location",

          latitude: coords.latitude,

          longitude: coords.longitude,

          accuracy: coords.accuracy,

        });

        setIsRetryingLocation(false);

        setWeatherStatus("loading");

        setWeatherStatusMessage("Loading weather...");



        try {

          const observation = await getCurrentWeather(coords.latitude, coords.longitude);

          if (!isActive) return;

          setSelectedWeather(observation);

          setWeatherStatus("ready");



          try {

            const location = await getLocationName(

              coords.latitude,

              coords.longitude,

              coords.accuracy,

            );

            if (isActive) setSelectedLocation(location);

          } catch (error) {

            // Keep the real weather and the safe Current location label.

            console.error("[GEOCODING] error:", error);

          }

        } catch {

          if (!isActive) return;

          setSelectedWeather(null);

          setWeatherStatus("error");

          setWeatherStatusMessage("Unable to load current weather.");

          setIsRetryingLocation(false);

          console.error("[WEATHER] error: unable to load current weather");

        }

      } catch (error) {

        if (!isActive) return;

        console.error("[LOCATION] error:", {

          code: error.code,

          message: error.message,

        });

        const messages = {

          1: "Location permission is required to show weather for your current location.",

          2: "Your current location is unavailable.",

          3: "Timed out while detecting your current location.",

        };

        const stateMessage = messages[error.code] || error.message || "Unable to determine your current location.";

        setLocationError(`${stateMessage}`);

      }

    };



    locationRequestRef.current = loadCurrentWeather;

    loadCurrentWeather();

    return () => {

      isActive = false;

      locationRequestRef.current = null;

    };

  }, []);



  const retryLocation = () => {

    setIsRetryingLocation(true);

    setSelectedWeather(null);

    setWeatherStatus("loading");

    setWeatherStatusMessage("Detecting current location...");

    setLocationMessage("");

    locationRequestRef.current?.();

  };



  const handleLocationSearch = (event) => {

    event.preventDefault();

    const location = getLocationByQuery(locationQuery);



    if (!location) {

      setLocationMessage("Location not found in the demo search data.");

      setSelectedLocation(null);

      setSelectedWeather(null);

      setWeatherStatus("unavailable");

      setWeatherStatusMessage("");

      return;

    }



    const result = getWeatherByLocation(location.latitude, location.longitude);

    setLocationQuery("");

    setLocationMessage("");

    setSelectedLocation(result.location);

    setSelectedWeather(result.observation);

    setWeatherStatus(result.observation ? "ready" : "unavailable");

    setWeatherStatusMessage("");

  };



  const handleFilterChange = (field, value) => {

    const normalizedValue = value.startsWith("All ") ? "" : value;



    if (field === "date") setDate(normalizedValue);

    if (field === "eventType") setEventType(normalizedValue);

    if (field === "state") setState(normalizedValue);

    if (field === "verification") setVerification(normalizedValue);

    if (field === "severity") setSeverity(normalizedValue);

  };



  const handleFilterPanelChange = (event) => {

    const label = event.target.closest("div")?.querySelector("label")?.textContent?.trim();

    const fieldByLabel = {

      Date: "date",

      "Event Type": "eventType",

      State: "state",

      Verification: "verification",

      Severity: "severity",

    };



    const field = fieldByLabel[label];

    if (field) handleFilterChange(field, event.target.value);

  };



  const resetFilters = (event) => {

    if (event.target.textContent.trim() !== "Reset Filters") return;



    setDate("");

    setEventType("");

    setState("");

    setVerification("");

    setSeverity("");

    setFilterPanelKey((key) => key + 1);

  };



  const handleViewIntelligence = (event) => {

    setSelectedEvent(event);

    const weatherResult = getWeatherForEvent(event);

    setSelectedLocation(weatherResult.location);

    setSelectedWeather(weatherResult.observation);

    setWeatherStatus(weatherResult.observation ? "ready" : "unavailable");

    setLocationMessage("");

    setWeatherStatusMessage("");



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



        <main className="flex-1 min-w-0 p-6">



          {/* Page Heading */}

          <div className="mb-6 pb-5 border-b border-slate-200 flex flex-col md:flex-row md:justify-between md:items-end gap-4">

            <div>

              <div className="flex items-center gap-3">

                <h2 className="text-2xl font-bold text-slate-800">

                  National Weather Intelligence

                </h2>

                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800">

                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>

                  System Operational

                </span>

              </div>

              <p className="mt-1 text-sm text-slate-500">

                Real-time weather monitoring, event intelligence and situational awareness.

              </p>

            </div>

            

            <div className="flex flex-wrap gap-3">

              <Link to="/map" className="px-4 py-2 bg-white border border-slate-200 text-sm font-bold text-slate-700 rounded-lg hover:bg-slate-50 transition shadow-sm">

                🗺️ Weather Map

              </Link>

              <Link to="/events" className="px-4 py-2 bg-white border border-slate-200 text-sm font-bold text-slate-700 rounded-lg hover:bg-slate-50 transition shadow-sm">

                🌧️ Event Feed

              </Link>

              <Link to="/analytics" className="px-4 py-2 bg-white border border-slate-200 text-sm font-bold text-slate-700 rounded-lg hover:bg-slate-50 transition shadow-sm">

                📈 Analytics

              </Link>

            </div>

          </div>



          {/* Statistics */}

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">



            <StatCard

              title="Total Reports"

              value={analytics ? analytics.total_events : "..."}

              icon="📡"

              description="Reports collected"

            />



            <StatCard

              title="Verified Reports"

              value={analytics ? analytics.verified : "..."}

              icon="✅"

              description="Successfully verified"

            />



            <StatCard

              title="Active Events"

              value={analytics ? analytics.total_events - analytics.rejected - analytics.suspicious : "..."}

              icon="⚠️"

              description="Currently active"

            />



            <StatCard

              title="Suspicious Reports"

              value={analytics ? analytics.suspicious : "..."}

              icon="🚨"

              description="Requires investigation"

            />



          </div>



          <div className="mt-6">

            <form onSubmit={handleLocationSearch} className="mb-4 flex flex-col gap-2 sm:flex-row">

              <label htmlFor="weather-location-search" className="sr-only">

                Search weather location

              </label>

              <input

                id="weather-location-search"

                value={locationQuery}

                onChange={(event) => setLocationQuery(event.target.value)}

                placeholder="Search city (e.g. Mumbai or Delhi)"

                className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-700 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"

              />

              <button

                type="submit"

                className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"

              >

                Search location

              </button>

            </form>

            {locationMessage && (

              <p className="mb-3 text-sm text-rose-600">{locationMessage}</p>

            )}

            <WeatherConditions

              observation={selectedWeather}

              location={selectedLocation}

              status={weatherStatus}

              statusMessage={weatherStatusMessage}

              onRetryLocation={retryLocation}

              isRetrying={isRetryingLocation}

            />

          </div>







          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">

            <IncidentFeed

              events={filteredEvents}

              onSelectEvent={handleViewIntelligence}

              selectedEvent={selectedEvent}

            />



            <div id="event-intelligence">

              <EventIntelligence event={selectedEvent} />

            </div>

          </div>



          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">

            <DataSources analytics={analytics} />

            <PipelineMonitor />

          </div>







        </main>



      </div>



    </div>

  );

}



export default Dashboard;

