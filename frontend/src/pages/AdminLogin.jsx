import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAdminAuth } from "../components/AdminAuthContext";
import { loginAdmin } from "../services/api";

export default function AdminLogin() {
  const navigate = useNavigate();
  const { login } = useAdminAuth();
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    const form = new FormData(event.target);
    try {
      const data = await loginAdmin(form.get("identity"), form.get("password"));
      login(data.access_token);
      navigate("/admin", { replace: true });
    } catch (err) {
      setError("Invalid username or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10">
      <section className="w-full max-w-md overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="bg-slate-900 px-6 py-7 text-white sm:px-8">
          <p className="text-sm font-semibold uppercase tracking-wider text-teal-300">National Weather Intelligence</p>
          <h1 className="mt-2 text-2xl font-bold">Admin Login</h1>
          <p className="mt-2 text-sm text-slate-300">Secure access for weather platform administration.</p>
        </div>

        <form className="space-y-5 p-6 sm:p-8" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-rose-50 p-3 text-sm text-rose-600 border border-rose-200">
              {error}
            </div>
          )}
          <div>
            <label htmlFor="admin-identity" className="mb-2 block text-sm font-medium text-slate-700">
              Username or Email
            </label>
            <input
              id="admin-identity"
              name="identity"
              type="text"
              autoComplete="username"
              placeholder="Enter your username or email"
              className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          <div>
            <label htmlFor="admin-password" className="mb-2 block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="admin-password"
              name="password"
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          <button type="submit" className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
            Login
          </button>
        </form>
      </section>
    </main>
  );
}
