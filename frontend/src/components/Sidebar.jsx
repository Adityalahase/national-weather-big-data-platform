import { createContext, useContext, useState } from "react";
import { NavLink } from "react-router-dom";

const SidebarContext = createContext(null);

export function SidebarProvider({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const value = {
    sidebarOpen,
    toggleSidebar: () => setSidebarOpen((prev) => !prev),
    closeSidebar: () => setSidebarOpen(false),
  };

  return <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>;
}

export function useSidebar() {
  const sidebar = useContext(SidebarContext);
  return (
    sidebar || {
      sidebarOpen: true,
      toggleSidebar: () => {},
      closeSidebar: () => {},
    }
  );
}

const navItems = [
  { 
    to: "/", 
    label: "Dashboard", 
    end: true,
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
      </svg>
    )
  },
  { 
    to: "/events", 
    label: "Weather Events",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
      </svg>
    )
  },
  { 
    to: "/analytics", 
    label: "Analytics",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    )
  },
  { 
    to: "/map", 
    label: "India Map",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  },
];

function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useSidebar();

  return (
    <>
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-[950] bg-black/20 backdrop-blur-sm md:hidden transition-opacity duration-300"
          onClick={toggleSidebar}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-[1000] h-screen overflow-visible border-r border-slate-200 bg-white shadow-[1px_0_12px_rgba(0,0,0,0.03)] transition-[width] duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
          sidebarOpen ? "w-64" : "w-16"
        }`}
      >
        <div className="flex h-full flex-col pt-16">
          <div className="flex-1 overflow-y-auto overflow-x-hidden px-3 py-6 custom-scrollbar">
            {sidebarOpen && (
              <p className="mb-4 px-2 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 transition-opacity duration-200">
                Main Menu
              </p>
            )}

            <nav className="flex flex-col gap-1.5">
              {navItems.map(({ to, label, icon, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  title={!sidebarOpen ? label : undefined}
                  className={({ isActive }) =>
                    `group relative flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all duration-120 ease-[cubic-bezier(0.2,0,0,1)] ${
                      sidebarOpen ? "w-full" : "justify-center"
                    } ${
                      isActive
                        ? "bg-slate-100 text-slate-900 font-medium"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {/* Active indicator bar */}
                      <div 
                        className={`absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-teal-700 transition-all duration-200 ${
                          isActive ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-2"
                        }`}
                      />
                      
                      <span className={`shrink-0 transition-transform duration-200 group-hover:scale-105 ${isActive ? "text-teal-700" : ""}`}>
                        {icon}
                      </span>
                      
                      {sidebarOpen && (
                        <span className="truncate whitespace-nowrap text-sm tracking-tight transition-opacity duration-200">
                          {label}
                        </span>
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </aside>

      <div
        aria-hidden="true"
        className={`shrink-0 transition-[width] duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${
          sidebarOpen ? "w-64" : "w-16"
        }`}
      />
    </>
  );
}

export default Sidebar;

