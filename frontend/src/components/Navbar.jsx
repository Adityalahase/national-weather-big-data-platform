import { useEffect, useRef, useState } from "react";
import { useSidebar } from "./Sidebar";
import { getEvents } from "../services/api";

function getNotificationIcon(event) {
  if (event.verification_status === "Suspicious") return "⚠️";
  if (event.verification_status === "Pending") return "⏳";
  if (event.event_type === "Heavy Rainfall") return "🌧️";
  if (event.event_type === "Heatwave") return "🌡️";
  return "🚨";
}

function getNotificationMessage(event) {
  if (event.verification_status === "Pending") {
    return `${event.event_type} event pending verification in ${event.city}`;
  }

  if (event.verification_status === "Suspicious") {
    return `Suspicious ${event.event_type} report detected in ${event.city}`;
  }

  if (event.severity === "High" && event.verification_status === "Verified") {
    return `High severity ${event.event_type} detected in ${event.city}`;
  }

  return `${event.event_type} update detected in ${event.city}`;
}

function formatNotificationTime(timestamp) {
  return new Date(timestamp).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function createNotifications(events) {
  return events.map((event) => ({
    id: event.id,
    event_id: event.id,
    message: getNotificationMessage(event),
    icon: getNotificationIcon(event),
    city: event.city,
    state: event.state,
    timestamp: event.timestamp,
    is_read: false,
  }));
}

function Navbar({ isAdmin = false, onToggleSidebar }) {
  const sidebar = useSidebar();
  const handleToggle = onToggleSidebar || sidebar.toggleSidebar;
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(() => localStorage.getItem("weather-theme") === "dark");
  const [notifications, setNotifications] = useState([]);
  
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await getEvents();
        setNotifications(createNotifications(data));
      } catch (error) {
        console.error("Failed to fetch events for notifications:", error);
      }
    };
    fetchEvents();
  }, []);
  const notificationRef = useRef(null);

  const unreadCount = notifications.filter(
    (notification) => !notification.is_read,
  ).length;

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode);
    localStorage.setItem("weather-theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setIsNotificationOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const markNotificationAsRead = (notificationId) => {
    setNotifications((currentNotifications) => currentNotifications.map((notification) => (
      notification.id === notificationId
        ? { ...notification, is_read: true }
        : notification
    )));
  };

  const markAllAsRead = () => {
    setNotifications((currentNotifications) => currentNotifications.map((notification) => ({
      ...notification,
      is_read: true,
    })));
  };

  return (
    <>
      <header className="fixed inset-x-0 top-0 z-[1100] h-16 overflow-visible bg-slate-900 text-white flex items-center justify-between shadow-md">

        {/* Left: YouTube-style Static Hamburger Button + Logo & Title */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Hamburger sits in a w-16 container to align with sidebar icons */}
          <div className="flex w-16 shrink-0 items-center justify-center">
          <button
            type="button"
            aria-label="Guide (☰)"
            title="Guide (☰)"
            onClick={handleToggle}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-slate-300 transition-colors hover:bg-white/10 hover:text-white active:bg-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
          >
            <svg
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          </div>

          <div className="text-2xl drop-shadow-md">🇮🇳</div>

          <div>
            <h1 className="text-sm font-black uppercase tracking-wider text-white">
              National Weather Intelligence
            </h1>

            <p className="hidden sm:block text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">
              Real-time Weather Analytics Platform
            </p>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-5 pr-4 sm:pr-6">

          {/* System Status */}
          <div className="flex items-center gap-2 text-sm">
            <span className="w-2.5 h-2.5 bg-green-500 rounded-full"></span>
            <span className="text-slate-300">
              {isAdmin ? "Admin System Online" : "System Online"}
            </span>
          </div>

          <div ref={notificationRef} className="relative z-[10000]">
            <button
              type="button"
              aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ""}`}
              aria-expanded={isNotificationOpen}
              onClick={() => setIsNotificationOpen((isOpen) => !isOpen)}
              className="relative rounded-md p-1 text-xl transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-300"
            >
              🔔
              {unreadCount > 0 && (
                <span className="absolute -right-2 -top-2 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold leading-none text-white">
                  {unreadCount}
                </span>
              )}
            </button>

            <section
              aria-hidden={!isNotificationOpen}
              className={`absolute right-0 top-full z-[9999] mt-3 flex max-h-[380px] w-96 max-w-[calc(100vw-2rem)] origin-top-right flex-col overflow-hidden rounded-xl border border-slate-700 bg-slate-900 text-white shadow-2xl transition-all duration-200 ${isNotificationOpen
                  ? "translate-y-0 scale-100 opacity-100"
                  : "pointer-events-none -translate-y-2 scale-95 opacity-0"
                }`}
            >
              <div className="flex items-center justify-between border-b border-slate-700 px-4 py-3">
                <h2 className="text-sm font-semibold">Notifications</h2>
                <button
                  type="button"
                  onClick={markAllAsRead}
                  className="text-xs font-medium text-sky-300 transition hover:text-sky-200"
                >
                  Mark all as read
                </button>
              </div>

              <div className="min-h-0 flex-1 overflow-y-auto">
                {notifications.map((notification) => {
                  return (
                    <button
                      key={notification.id}
                      type="button"
                      onClick={() => markNotificationAsRead(notification.id)}
                      className={`flex w-full gap-3 border-b border-slate-800 px-4 py-3 text-left transition last:border-b-0 hover:bg-slate-800 ${notification.is_read ? "opacity-60" : "bg-slate-800/40"
                        }`}
                    >
                      <span className="mt-0.5 text-lg" aria-hidden="true">{notification.icon}</span>
                      <span className="min-w-0 flex-1">
                        <span className="block text-sm font-medium leading-5 text-slate-100">{notification.message}</span>
                        <span className="mt-1 block text-xs text-slate-400">
                          {notification.city} · {formatNotificationTime(notification.timestamp)}
                        </span>
                      </span>
                      {!notification.is_read && <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-sky-400" aria-label="Unread" />}
                    </button>
                  );
                })}
              </div>
            </section>
          </div>

          {isAdmin && (
            <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm font-semibold text-slate-200">
              <span aria-hidden="true">🛡️</span>
              <span>Admin</span>
            </div>
          )}

          <button
            type="button"
            aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            aria-pressed={isDarkMode}
            onClick={() => setIsDarkMode((isDark) => !isDark)}
            className="rounded-md p-1 text-xl transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-300"
          >
            {isDarkMode ? "☀️" : "🌙"}
          </button>

        </div>
      </header>
      <div aria-hidden="true" className="h-16" />
    </>
  );
}

export default Navbar;