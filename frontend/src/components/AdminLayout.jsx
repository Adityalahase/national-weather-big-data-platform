import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import AdminSidebar from "./AdminSidebar";
import Navbar from "./Navbar";
import { getAdminEvents, updateVerificationStatusApi } from "../services/api";

export default function AdminLayout() {
  const [events, setEvents] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await getAdminEvents();
      setEvents(data);
    } catch (error) {
      console.error("Failed to fetch events for admin:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const updateVerificationStatus = async (eventId, verificationStatus) => {
    try {
      await updateVerificationStatusApi(eventId, verificationStatus);
      setEvents((currentEvents) => currentEvents.map((event) => (
        event.id === eventId ? { ...event, verification_status: verificationStatus } : event
      )));
    } catch (error) {
      console.error("Failed to update verification status:", error);
      alert("Failed to update verification status.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar isAdmin onToggleSidebar={() => setSidebarOpen((isOpen) => !isOpen)} />
      <div className="flex">
        <AdminSidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen((isOpen) => !isOpen)}
        />
        <main className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet context={{ events, updateVerificationStatus }} />
        </main>
      </div>
    </div>
  );
}
