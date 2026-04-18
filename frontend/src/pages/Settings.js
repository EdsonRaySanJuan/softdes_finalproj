import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import API_BASE_URL from "../config";
import "../styles/settings.css";

function Settings() {
  const [employees, setEmployees] = useState([]);

  const [fullName, setFullName] = useState("");
  const [userId, setUserId] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("Employee");

  useEffect(() => {
    fetchEmployees();
  }, []);

  async function fetchEmployees() {
    try {
      const res = await fetch(`${API_BASE_URL}/users/`);
      const data = await res.json();
      setEmployees(data);
    } catch (err) {
      console.error("Failed to fetch employees:", err);
    }
  }

  async function handleSaveEmployee() {
    if (!fullName || !userId || !username || !password) {
      alert("Please fill in all fields!");
      return;
    }

    const newEmployee = {
      user_id: userId,
      full_name: fullName,
      username: username,
      password: password,
      role: role,
      status: "Active"
    };

    try {
      const res = await fetch(`${API_BASE_URL}/users/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newEmployee)
      });

      if (res.ok) {
        alert("Employee added successfully!");
        setFullName("");
        setUserId("");
        setUsername("");
        setPassword("");
        fetchEmployees();
      } else {
        const errorData = await res.json();
        alert("Error: " + errorData.error);
      }
    } catch (err) {
      alert("Backend connection failed!");
    }
  }

  return (
    <div className="app-body">
      <div className="app-shell">
        <Sidebar role="Admin" />

        <main className="main-content">
          <header className="topbar">
            <div>
              <h2 className="page-title">Settings</h2>
              <p className="page-subtitle">Manage employee accounts and access levels.</p>
            </div>
          </header>

          <section className="settings-layout">
            <div className="settings-panel">
              <h3>Add Employee</h3>
              <div className="form-card">
                <div className="form-row">
                  <label>Full name</label>
                  <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Juan Dela Cruz" />
                </div>
                <div className="form-row">
                  <label>Employee ID</label>
                  <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="EMP0012" />
                </div>
                <div className="form-row">
                  <label>Username</label>
                  <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="juan_dev" />
                </div>
                <div className="form-row">
                  <label>Role</label>
                  <select value={role} onChange={(e) => setRole(e.target.value)}>
                    <option value="Employee">Employee (Orders)</option>
                    <option value="Admin">Admin (Full Access)</option>
                  </select>
                </div>
                <div className="form-row">
                  <label>Temporary Password</label>
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
                </div>
                <div className="form-actions">
                  <button className="btn-primary" onClick={handleSaveEmployee}>Save Employee</button>
                </div>
              </div>
            </div>

            <div className="settings-panel">
              <div className="panel-header">
                <h3>Registered Employees</h3>
              </div>
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.length === 0 ? (
                    <tr><td colSpan="5" style={{ textAlign: "center" }}>No employees found.</td></tr>
                  ) : (
                    employees.map((emp) => (
                      <tr key={emp.user_id}>
                        <td>{emp.user_id}</td>
                        <td>{emp.full_name}</td>
                        <td>{emp.username}</td>
                        <td>{emp.role}</td>
                        <td>
                          <span className={`badge badge-${emp.status === "Active" ? "ok" : "disabled"}`}>
                            {emp.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Settings;