import { createContext, useContext, useState } from "react";

const AdminAuthContext = createContext(null);

function getInitialAuthState() {
  return sessionStorage.getItem("admin-authenticated") === "true";
}

export function AdminAuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(getInitialAuthState);

  const login = (token) => {
    sessionStorage.setItem("admin-token", token);
    sessionStorage.setItem("admin-authenticated", "true");
    setIsAuthenticated(true);
  };

  const logout = () => {
    sessionStorage.removeItem("admin-token");
    sessionStorage.removeItem("admin-authenticated");
    setIsAuthenticated(false);
  };

  return (
    <AdminAuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AdminAuthContext.Provider>
  );
}

export function useAdminAuth() {
  const auth = useContext(AdminAuthContext);

  if (!auth) throw new Error("useAdminAuth must be used within AdminAuthProvider");

  return auth;
}
