import React, { useEffect, useState, useRef } from "react";
import Sidebar from "../components/Sidebar";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import "../styles/reports.css";
import API_BASE_URL from "../config";

import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, Title);
ChartJS.defaults.font.family = 'system-ui, -apple-system, sans-serif';

function Reports() {
  const [report, setReport] = useState({
    total_sales: 0,
    total_orders: 0,
    avg_order: 0,
    top_category: ""
  });

  const [dailyData, setDailyData] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [chartRange, setChartRange] = useState("7");

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [isGenerating, setIsGenerating] = useState(false);
  const reportRef = useRef();

  const fetchSummaryData = async (start, end) => {
    try {
      const url = (start && end)
        ? `${API_BASE_URL}/reports/range?start=${start}&end=${end}`
        : `${API_BASE_URL}/reports/range`;

      const res = await fetch(url);
      const data = await res.json();
      setReport(data);
    } catch (err) {
      console.error("Summary fetch error:", err);
    }
  };

  const fetchChartData = async (range) => {
    try {
      const res = await fetch(`${API_BASE_URL}/reports/chart?range=${range}`);
      const data = await res.json();
      setChartData(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Chart fetch error:", err);
    }
  };

  const fetchDailyTable = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/reports/daily`);
      const data = await res.json();
      setDailyData(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Daily table fetch error:", err);
    }
  };

  useEffect(() => {
    fetchSummaryData();
    fetchChartData("7");
    fetchDailyTable();
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      fetchSummaryData(startDate, endDate);
    }
  }, [startDate, endDate]);

  const handlePreset = (value) => {
    const today = new Date();
    let start = "";
    let end = today.toISOString().split("T")[0];

    if (value === "Today") {
      start = end;
    } else if (value === "Last 7 Days") {
      const past = new Date();
      past.setDate(today.getDate() - 7);
      start = past.toISOString().split("T")[0];
    } else if (value === "Last 30 Days") {
      const past = new Date();
      past.setDate(today.getDate() - 30);
      start = past.toISOString().split("T")[0];
    } else {
      return;
    }

    setStartDate(start);
    setEndDate(end);
  };

  const handleChartChange = (value) => {
    setChartRange(value);
    fetchChartData(value);
  };

  const handleDownloadPDF = async () => {
    const element = reportRef.current;
    if (!element) return;
    setIsGenerating(true);

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        backgroundColor: "#051310"
      });
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
      pdf.save(`Cafe_Sales_Report_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (error) {
      console.error("PDF generation failed:", error);
      alert("Failed to generate PDF.");
    } finally {
      setIsGenerating(false);
    }
  };

  const chartConfig = {
    labels: chartData.map((d) => d.date),
    datasets: [{
      label: "Sales ₱",
      data: chartData.map((d) => d.sales),
      borderColor: "#19C37D",
      backgroundColor: "rgba(25, 195, 125, 0.15)",
      pointBackgroundColor: "#19C37D",
      pointRadius: 4,
      tension: 0.35,
      fill: true
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color: "#A9B3AE" }, grid: { color: "rgba(255, 255, 255, 0.05)" } },
      y: { ticks: { color: "#A9B3AE" }, grid: { color: "rgba(255, 255, 255, 0.05)" } }
    }
  };

  return (
    <div className="app-body">
      <div className="app-shell">
        <Sidebar role="Admin" />
        <main className="main-content">
          <header className="topbar">
            <div>
              <h2 className="page-title">Reports</h2>
              <p className="page-subtitle">Generate summarized sales and order performance.</p>
            </div>
            <div className="topbar-right">
              <select
                onChange={(e) => handlePreset(e.target.value)}
                defaultValue="Today"
                style={{ marginRight: '10px' }}
              >
                <option>Today</option>
                <option>Last 7 Days</option>
                <option>Last 30 Days</option>
                <option>Custom</option>
              </select>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={{ marginRight: '5px' }}
              />
              <span style={{ color: '#fff', marginRight: '5px' }}>to</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={{ marginRight: '15px' }}
              />
              <button
                className="btn-primary"
                onClick={handleDownloadPDF}
                disabled={isGenerating}
              >
                {isGenerating ? "Exporting..." : "Download PDF"}
              </button>
            </div>
          </header>

          <div ref={reportRef} style={{ padding: '10px' }}>
            <section className="kpi-grid">
              <div className="kpi-card">
                <span className="kpi-label">Total Sales</span>
                <span className="kpi-value" style={{ color: '#4ade80' }}>
                  ₱ {Number(report.total_sales).toFixed(2)}
                </span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Total Orders</span>
                <span className="kpi-value">{report.total_orders}</span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Average Order</span>
                <span className="kpi-value">₱ {Number(report.avg_order).toFixed(2)}</span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Top Category</span>
                <span className="kpi-value" style={{ fontSize: '1.2em' }}>
                  {report.top_category || "—"}
                </span>
              </div>
            </section>

            <section className="reports-panel">
              <div className="panel-header">
                <h3>Sales Trend</h3>
                <select
                  value={chartRange}
                  onChange={(e) => handleChartChange(e.target.value)}
                >
                  <option value="3">Last 3 Days</option>
                  <option value="7">Last 7 Days</option>
                  <option value="15">Last 15 Days</option>
                </select>
              </div>
              <div className="chart-wrapper">
                {chartData.length > 0 ? (
                  <Line data={chartConfig} options={chartOptions} />
                ) : (
                  <p style={{ color: "#A9B3AE", textAlign: "center", paddingTop: "50px" }}>
                    No sales data available yet.
                  </p>
                )}
              </div>
            </section>

            <section className="reports-panel">
              <h3 style={{ marginBottom: "15px" }}>Daily Performance Breakdown</h3>
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Orders</th>
                    <th>Total Sales</th>
                    <th>Avg Handling Time</th>
                    <th>Top Category</th>
                  </tr>
                </thead>
                <tbody>
                  {dailyData.length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ textAlign: "center" }}>
                        No daily data available.
                      </td>
                    </tr>
                  ) : (
                    dailyData.map((row, index) => (
                      <tr key={index}>
                        <td style={{ fontWeight: 'bold' }}>{row.date}</td>
                        <td>{row.orders}</td>
                        <td style={{ color: '#4ade80' }}>₱ {Number(row.total_sales).toFixed(2)}</td>
                        <td><span className="badge badge-ok">{row.avg_handling}</span></td>
                        <td>{row.top_category}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Reports;