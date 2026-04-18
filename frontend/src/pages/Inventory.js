import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import API_BASE_URL from "../config";
import "../styles/inventory.css";

function Inventory() {
  const [items, setItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editFormData, setEditFormData] = useState({});

  const [newItem, setNewItem] = useState({
    item_name: "",
    category: "Coffee Base",
    unit: "g",
    current_stock: "",
    reorder_level: "",
    supplier: ""
  });

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/inventory/`);
      const data = await res.json();
      setItems(data);
    } catch (err) {
      console.error("Failed to fetch inventory:", err);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/inventory/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newItem)
      });
      if (res.ok) {
        alert("Item added!");
        setNewItem({
          item_name: "",
          category: "Coffee Base",
          unit: "g",
          current_stock: "",
          reorder_level: "",
          supplier: ""
        });
        fetchInventory();
      } else {
        const errData = await res.json();
        alert("Error: " + errData.error);
      }
    } catch (err) {
      alert("Backend connection failed!");
    }
  };

  const handleDeleteItem = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
      return;
    }
    try {
      const res = await fetch(`${API_BASE_URL}/inventory/${id}`, {
        method: "DELETE"
      });
      if (res.ok) {
        alert("Item deleted successfully!");
        fetchInventory();
      } else {
        const data = await res.json();
        alert("Error deleting item: " + data.error);
      }
    } catch (err) {
      console.error("Delete request failed:", err);
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setEditFormData(item);
  };

  const handleSaveEdit = async (id) => {
    try {
      const res = await fetch(`${API_BASE_URL}/inventory/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editFormData)
      });

      if (res.ok) {
        setEditingId(null);
        fetchInventory();
      } else {
        const data = await res.json();
        alert("Failed to update: " + data.error);
      }
    } catch (err) {
      console.error("Edit failed:", err);
    }
  };

  const filteredItems = items.filter((item) =>
    item.item_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="app-body">
      <div className="app-shell">
        <Sidebar role="Admin" />

        <main className="main-content">
          <header className="topbar">
            <div>
              <h2 className="page-title">Inventory Management</h2>
              <p className="page-subtitle">Track and manage your cafe ingredients.</p>
            </div>
          </header>

          <section className="inventory-grid">
            <div className="panel add-item-form">
              <h3>Add New Ingredient</h3>
              <form onSubmit={handleAddItem}>
                <input type="text" placeholder="Name" value={newItem.item_name} onChange={(e) => setNewItem({ ...newItem, item_name: e.target.value })} required />
                <select value={newItem.category} onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}>
                  <option>Coffee Base</option>
                  <option>Milk/Dairy</option>
                  <option>Syrups</option>
                  <option>Powders</option>
                  <option>Add-ons/Sinkers</option>
                  <option>Fruit/Lemonade</option>
                </select>
                <input type="text" placeholder="Unit (g, ml, pcs)" value={newItem.unit} onChange={(e) => setNewItem({ ...newItem, unit: e.target.value })} />
                <input type="number" placeholder="Initial Stock" value={newItem.current_stock} onChange={(e) => setNewItem({ ...newItem, current_stock: e.target.value })} required />
                <input type="number" placeholder="Reorder Level" value={newItem.reorder_level} onChange={(e) => setNewItem({ ...newItem, reorder_level: e.target.value })} required />
                <input type="text" placeholder="Supplier" value={newItem.supplier} onChange={(e) => setNewItem({ ...newItem, supplier: e.target.value })} />
                <button type="submit" className="btn-primary">Add Ingredient</button>
              </form>
            </div>

            <div className="panel inventory-table-container">
              <div className="panel-header">
                <h3>Current Stock</h3>
                <input
                  type="text"
                  placeholder="Search ingredients..."
                  className="search-input"
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <table className="table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Stock</th>
                    <th>Level</th>
                    <th>Status</th>
                    <th>Supplier</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredItems.map((item) => (
                    <tr key={item.id}>
                      {editingId === item.id ? (
                        <>
                          <td><input className="edit-input" value={editFormData.item_name} onChange={(e) => setEditFormData({ ...editFormData, item_name: e.target.value })} /></td>
                          <td><input className="edit-input" type="number" value={editFormData.current_stock} onChange={(e) => setEditFormData({ ...editFormData, current_stock: e.target.value })} /></td>
                          <td><input className="edit-input" type="number" value={editFormData.reorder_level} onChange={(e) => setEditFormData({ ...editFormData, reorder_level: e.target.value })} /></td>
                          <td><span className="badge">Editing...</span></td>
                          <td><input className="edit-input" value={editFormData.supplier} onChange={(e) => setEditFormData({ ...editFormData, supplier: e.target.value })} /></td>
                          <td className="actions-cell">
                            <button className="btn-save" onClick={() => handleSaveEdit(item.id)}>Save</button>
                            <button className="btn-cancel" onClick={() => setEditingId(null)}>Cancel</button>
                          </td>
                        </>
                      ) : (
                        <>
                          <td><strong>{item.item_name}</strong></td>
                          <td>{item.current_stock} {item.unit}</td>
                          <td>{item.reorder_level}</td>
                          <td>
                            <span className={`badge badge-${item.status.toLowerCase().replace(" ", "-")}`}>
                              {item.status}
                            </span>
                          </td>
                          <td style={{ color: "#888", fontSize: "0.85rem" }}>{item.supplier || "N/A"}</td>
                          <td className="actions-cell">
                            <button className="btn-edit" onClick={() => startEdit(item)}>Edit</button>
                            <button className="btn-danger-small" onClick={() => handleDeleteItem(item.id, item.item_name)}>Delete</button>
                          </td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Inventory;