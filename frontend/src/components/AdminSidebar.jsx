import { NavLink, useNavigate } from "react-router-dom";
import { useAdminAuth } from "./AdminAuthContext";

const adminNavItems = [
  { to: "/admin", label: "Admin Panel", icon: "▦", end: true },
  { to: "/admin/events", label: "Event Verification", icon: "✓" },
  { to: "/admin/events/pending", label: "Pending Events", icon: "⏳" },
  { to: "/admin/events/suspicious", label: "Suspicious Events", icon: "⚠️" },
];

function AdminSidebar({ isOpen, onToggle }) {
  const navigate = useNavigate();
  const { logout } = useAdminAuth();

  const handleLogout = () => {
    logout();
    navigate("/admin/login", { replace: true });
  };

  return (
    <>
      {/* Mobile backdrop overlay when admin sidebar is open */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[950] bg-black/50 backdrop-blur-xs md:hidden"
          onClick={onToggle}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-[1000] h-screen overflow-visible border-r border-slate-200 bg-white shadow-sm transition-[width] duration-300 ease-in-out ${isOpen ? "w-64 p-4" : "w-16 p-2"
          }`}
      >
        <div className="h-full overflow-y-auto overflow-x-hidden pt-16">
          <div className={`mb-6 flex items-center gap-3 whitespace-nowrap pt-1 transition-all duration-200 ${isOpen ? "px-3 opacity-100" : "justify-center px-0"}`}>
            <span className="text-2xl" title={!isOpen ? "Admin Console" : undefined}>🛡️</span>
            {isOpen && (
              <span className="text-sm font-bold text-slate-800">Admin Console</span>
            )}
          </div>

          {isOpen && (
            <p className="mb-3 whitespace-nowrap px-3 text-xs font-semibold uppercase text-slate-400 transition-opacity duration-200">
              Admin Menu
            </p>
          )}

          <nav className="space-y-1" aria-label="Admin navigation">
            {adminNavItems.map(({ to, label, icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                title={!isOpen ? label : undefined}
                className={({ isActive }) => `flex w-full items-center ${isOpen ? "gap-3 px-4" : "justify-center px-0"
                  } rounded-lg py-3 text-left transition hover:bg-slate-100 ${isActive ? "bg-slate-100 font-semibold text-slate-900" : "text-slate-600"
                  }`}
              >
                <span className="shrink-0" aria-hidden="true">{icon}</span>
                {isOpen && (
                  <span className="whitespace-nowrap transition-opacity duration-200">
                    {label}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>

          <button
            type="button"
            onClick={handleLogout}
            title={!isOpen ? "Logout" : undefined}
            className={`mt-8 flex w-full items-center ${isOpen ? "gap-3 px-4" : "justify-center px-0"
              } rounded-lg py-3 text-slate-600 transition hover:bg-slate-100 cursor-pointer`}
          >
            <span className="shrink-0" aria-hidden="true">↪</span>
            {isOpen && (
              <span className="whitespace-nowrap transition-opacity duration-200">Logout</span>
            )}
          </button>
        </div>
      </aside>

      <div aria-hidden="true" className={`shrink-0 transition-[width] duration-300 ease-in-out ${isOpen ? "w-64" : "w-16"}`} />
    </>
  );
}

export default AdminSidebar;
