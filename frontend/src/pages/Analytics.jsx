import React, { useEffect, useState } from "react";
import AnalyticsCharts from "../components/AnalyticsCharts";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import StatCard from "../components/StatCard";
import { getAnalytics } from "../services/api";

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getAnalytics();
        setAnalytics(data);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalEvents = analytics ? analytics.total_events : 0;
  const verifiedEvents = analytics ? analytics.verified : 0;
  const pendingEvents = analytics ? analytics.pending : 0;
  const suspiciousEvents = analytics ? analytics.suspicious : 0;

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1 p-6">
          <div className="mx-auto max-w-7xl space-y-6">
            <header>
              <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">National Weather Intelligence</p>
              <h1 className="mt-1 text-2xl font-bold text-slate-800">Weather Analytics</h1>
              <p className="mt-1 text-slate-500">Analyze weather events, verification status, severity and geographic distribution across India</p>
            </header>

            {loading ? (
              <div className="flex justify-center p-12">
                <p className="text-slate-500 animate-pulse">Loading analytics data...</p>
              </div>
            ) : (
              <>
                <section aria-label="Analytics summary" className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
                  <StatCard title="Total Events" value={totalEvents} icon="Total" description="Recorded weather events" />
                  <StatCard title="Verified Events" value={verifiedEvents} icon="OK" description="Confirmed by the platform" />
                  <StatCard title="Pending Events" value={pendingEvents} icon="?" description="Awaiting verification" />
                  <StatCard title="Suspicious Events" value={suspiciousEvents} icon="!" description="Requires investigation" />
                </section>

                <AnalyticsCharts analytics={analytics} />
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
