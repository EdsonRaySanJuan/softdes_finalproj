import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import API_BASE_URL from "../config";
import "../styles/dashboard.css";

function Automation() {
  const [logs, setLogs] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchLogs = async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/rpa/logs`);
      const data = await res.json();
      setLogs(data);
    } catch (err) {
      console.error("Error fetching RPA logs:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-body">
      <div className="app-shell">
        <Sidebar role="Admin" />

        <main className="main-content">
          <header className="topbar">
            <div>
              <h2 className="page-title">Robotic Process Automation</h2>
              <p className="page-subtitle">Monitor bot activity and automated inventory tasks.</p>
            </div>
            <div className="topbar-right">
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
              <span className="kpi-value">{logs.length}</span>
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
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan="4" style={{ textAlign: "center", padding: "30px", color: "#888" }}>
                      No automation logs recorded yet. Run your rpa_agent.py to see activity.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id}>
                      <td style={{ color: "#A9B3AE" }}>{log.timestamp}</td>
                      <td><strong>{log.bot_name}</strong></td>
                      <td>{log.task_description}</td>
                      <td>
                        <span className={`badge badge-${log.status.toLowerCase() === "completed" ? "ok" : "warning"}`}>
                          {log.status}
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