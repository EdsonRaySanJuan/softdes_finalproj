import { useEffect, useState, useCallback } from "react";
import Sidebar from "../components/Sidebar";
import API_BASE_URL from "../config";
import "../styles/dashboard.css";

function Automation() {
  const [logs, setLogs] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isRunningBot, setIsRunningBot] = useState(false);

  const normalizeArray = (payload, key) => {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload[key])) return payload[key];
    return [];
  };

  const fetchLogs = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/rpa/logs`);
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);

      const data = await res.json();
      console.log("RPA LOGS API RESPONSE:", data);

      const normalizedLogs = normalizeArray(data, "logs");
      setLogs(normalizedLogs);
    } catch (err) {
      console.error("Error fetching RPA logs:", err);
      setLogs([]);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  const runBotNow = async () => {
    setIsRunningBot(true);
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 60000); // 60s timeout

      const res = await fetch(`${API_BASE_URL}/rpa/run-bot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
      });

      clearTimeout(timeout);

      const data = await res.json();
      console.log("RUN BOT RESPONSE:", data);

      if (!res.ok || data.success === false) {
        throw new Error(data.message || data.error || "Failed to run bot");
      }

      alert(data.message || "Bot executed successfully");
      fetchLogs();
    } catch (err) {
      if (err.name === "AbortError") {
        alert("Server is waking up. Please try again in 30 seconds.");
      } else {
        alert(`Bot run failed: ${err.message}`);
      }
      console.error("Error running bot:", err);
    } finally {
      setIsRunningBot(false);
    }
  };

  useEffect(() => {
    fetchLogs(); // warms up Render server on page load
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, [fetchLogs]);

  const safeLogs = Array.isArray(logs) ? logs : [];

  return (
    <div className="app-body">
      <div className="app-shell">
        <Sidebar role="Admin" />

        <main className="main-content">
          <header className="topbar">
            <div>
              <h2 className="page-title">Robotic Process Automation</h2>
              <p className="page-subtitle">
                Monitor bot activity and automated inventory tasks.
              </p>
            </div>

            <div className="topbar-right" style={{ display: "flex", gap: "10px" }}>
              <button
                className="btn-primary"
                onClick={runBotNow}
                disabled={isRunningBot}
              >
                {isRunningBot ? "Running Bot..." : "Run Bot Now"}
              </button>

              <button
                className="btn-ghost"
                onClick={fetchLogs}
                disabled={isRefreshing}
              >
                {isRefreshing ? "Refreshing..." : "Manual Refresh"}
              </button>
            </div>
          </header>

          <section className="kpi-grid">
            <div className="kpi-card">
              <span className="kpi-label">Active Bots</span>
              <span className="kpi-value">1</span>
              <span className="kpi-extra">Inventory-Master-V1</span>
            </div>

            <div className="kpi-card">
              <span className="kpi-label">Total Automations</span>
              <span className="kpi-value">{safeLogs.length}</span>
              <span className="kpi-extra">Tasks completed</span>
            </div>
          </section>

          <section className="panel" style={{ marginTop: "20px" }}>
            <div className="panel-header">
              <h3>Live Bot Activity</h3>
              <span className="badge badge-ok">Bot Online</span>
            </div>

            <table className="table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Bot Name</th>
                  <th>Task Performed</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {safeLogs.length === 0 ? (
                  <tr>
                    <td
                      colSpan="4"
                      style={{ textAlign: "center", padding: "30px", color: "#888" }}
                    >
                      No automation logs recorded yet. Run the bot to see activity.
                    </td>
                  </tr>
                ) : (
                  safeLogs.map((log, index) => (
                    <tr key={log.id || index}>
                      <td style={{ color: "#A9B3AE" }}>{log.timestamp || "—"}</td>
                      <td><strong>{log.bot_name || "Unknown Bot"}</strong></td>
                      <td>{log.task_description || "No description"}</td>
                      <td>
                        <span
                          className={`badge ${
                            String(log.status || "").toLowerCase() === "completed"
                              ? "badge-ok"
                              : "badge-warning"
                          }`}
                        >
                          {log.status || "Unknown"}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Automation;