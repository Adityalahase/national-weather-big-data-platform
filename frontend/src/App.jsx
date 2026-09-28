import Dashboard from "./pages/Dashboard";
import AdminPanel from "./pages/AdminPanel";
import AdminLogin from "./pages/AdminLogin";
import AdminEvents from "./pages/AdminEvents";
import AdminPendingEvents from "./pages/AdminPendingEvents";
import AdminSuspiciousEvents from "./pages/AdminSuspiciousEvents";
import Analytics from "./pages/Analytics";
import IndiaMapPage from "./pages/IndiaMapPage";
import WeatherEvents from "./pages/WeatherEvents";
import AdminLayout from "./components/AdminLayout";
import ProtectedAdminRoute from "./components/ProtectedAdminRoute";
import { AdminAuthProvider } from "./components/AdminAuthContext";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { SidebarProvider } from "./components/Sidebar";

function App() {
  return (
    <BrowserRouter>
      <AdminAuthProvider>
        <SidebarProvider>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/events" element={<WeatherEvents />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/map" element={<IndiaMapPage />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route element={<ProtectedAdminRoute />}>
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<AdminPanel />} />
                <Route path="events" element={<AdminEvents />} />
                <Route path="events/pending" element={<AdminPendingEvents />} />
                <Route path="events/suspicious" element={<AdminSuspiciousEvents />} />
              </Route>
            </Route>
          </Routes>
        </SidebarProvider>
      </AdminAuthProvider>
    </BrowserRouter>
  );
}

export default App;
