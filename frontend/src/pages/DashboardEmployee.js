import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import "../styles/dashboard.css";
import { useNavigate } from "react-router-dom";
import API_BASE_URL from "../config";

function DashboardEmployee() {
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [totalSales, setTotalSales] = useState(0);
  const [totalOrders, setTotalOrders] = useState(0);
  const [itemsSold, setItemsSold] = useState(0);
  const [lowStockCount, setLowStockCount] = useState(0);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const statsRes = await fetch(`${API_BASE_URL}/dashboard/stats`);
        const statsData = await statsRes.json();

        setTotalSales(statsData.total_revenue || 0);
        setTotalOrders(statsData.total_orders || 0);
        setItemsSold(statsData.items_sold || 0);
        setLowStockCount(statsData.alerts || 0);
        setOrders(statsData.recent_orders || []);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        setOrders([]);
        setTotalSales(0);
        setTotalOrders(0);
        setItemsSold(0);
        setLowStockCount(0);
      }
    }

    fetchDashboardData();
  }, []);

  return (
    <div className="app-body">
      <div className="app-shell">
        <Sidebar role="Employee" />

        <main className="main-content">
          <header className="topbar">
            <div>
              <h2 className="page-title">Employee Dashboard</h2>
              <p className="page-subtitle">
                Overview of daily orders and cafe status.
              </p>
            </div>

            <div className="topbar-right">
              <span className="topbar-date">
                Today · {new Date().toLocaleTimeString()}
              </span>

              <div className="user-pill">
                <span className="user-avatar">EM</span>
                <span className="user-name">{localStorage.getItem("full_name") || "Employee"}</span>
              </div>
            </div>
          </header>

          <section className="kpi-grid">
            <div className="kpi-card">
              <span className="kpi-label">Total Sales</span>
              <span className="kpi-value" style={{ color: "#4ade80" }}>
                ₱ {totalSales.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="kpi-card">
              <span className="kpi-label">Total Orders</span>
              <span className="kpi-value">{totalOrders}</span>
            </div>

            <div className="kpi-card">
              <span className="kpi-label">Items Sold</span>
              <span className="kpi-value">{itemsSold}</span>
            </div>

            <div className="kpi-card warning">
              <span className="kpi-label">Low Stock Alerts</span>
              <span className="kpi-value">{lowStockCount}</span>
            </div>
          </section>

          <section className="panel" style={{ marginTop: "20px" }}>
            <div className="panel-header">
              <h3>Recent Orders</h3>
              <button className="btn-small" onClick={() => navigate("/orders")}>
                New Order
              </button>
            </div>

            <table className="table">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Order ID</th>
                  <th>Item Sold</th>
                  <th>Qty</th>
                  <th>Total Amount</th>
                  <th>Payment</th>
                </tr>
              </thead>
              <tbody>
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: "center" }}>No recent transactions found.</td>
                  </tr>
                ) : (
                  orders.map((order, index) => (
                    <tr key={index}>
                      <td style={{ fontWeight: "bold" }}>{order.datetime}</td>
                      <td>#{order.order_id}</td>
                      <td>{order.item_name}</td>
                      <td>{order.qty}</td>
                      <td style={{ color: "#4ade80" }}>₱ {order.line_total.toFixed(2)}</td>
                      <td><span className="badge badge-ok">{order.payment_method}</span></td>
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

export default DashboardEmployee;