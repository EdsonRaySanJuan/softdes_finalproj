import React, { useMemo, useState } from "react";
import Sidebar from "../components/Sidebar";
import "../styles/orders.css";
import { API_BASE_URL } from "../config";

const ADDON_PRICE = 10;

const menuData = {
  lemonade: {
    label: "Lemonade",
    description: "22oz drinks",
    items: [
      { name: "Lemonade (Regular)", prices: { Regular: 40 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Green Apple Lemonade", prices: { Regular: 50 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Strawberry Lemonade", prices: { Regular: 50 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Blueberry Lemonade", prices: { Regular: 50 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Peach Lemonade", prices: { Regular: 50 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Lychee Lemonade", prices: { Regular: 50 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Strawberry Lemon", prices: { Regular: 60 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Blue Lemonade", prices: { Regular: 60 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Red Fizz Lemonade", prices: { Regular: 60 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Cucumber Lemonade", prices: { Regular: 60 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
      { name: "Honey Ginger", prices: { Regular: 65 }, addons: ["Yakult", "Dutchmill", "Nata", "Chia Seeds"] },
    ],
  },

  yogurtSmoothies: {
    label: "Yogurt Smoothies",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Strawberry", prices: { Grande: 60, Venti: 70 }, addons: [] },
      { name: "Blueberry", prices: { Grande: 60, Venti: 70 }, addons: [] },
      { name: "Passion Fruit", prices: { Grande: 60, Venti: 70 }, addons: [] },
      { name: "Biscoff", prices: { Grande: 70, Venti: 80 }, addons: [] },
    ],
  },

  fruitSoda: {
    label: "Fruit Soda",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Green Apple", prices: { Grande: 58, Venti: 68 }, addons: ["Yakult"] },
      { name: "Strawberry", prices: { Grande: 58, Venti: 68 }, addons: ["Yakult"] },
      { name: "Blueberry", prices: { Grande: 58, Venti: 68 }, addons: ["Yakult"] },
      { name: "Peach", prices: { Grande: 58, Venti: 68 }, addons: ["Yakult"] },
      { name: "Lychee", prices: { Grande: 58, Venti: 68 }, addons: ["Yakult"] },
      { name: "Lemon", prices: { Grande: 58, Venti: 68 }, addons: ["Yakult"] },
      { name: "Ginger Ale", prices: { Grande: 58, Venti: 68 }, addons: ["Yakult"] },
    ],
  },

  hotCoffee: {
    label: "Hot Coffee",
    description: "12oz hot coffee",
    items: [
      { name: "Americano", prices: { Regular: 58 }, addons: ["Premium Upgrade"] },
      { name: "Cà Phê Español", prices: { Regular: 58 }, addons: ["Premium Upgrade"] },
      { name: "Hot Latte", prices: { Regular: 58 }, addons: ["Premium Upgrade"] },
      { name: "Caramel Macchiato", prices: { Regular: 58 }, addons: ["Premium Upgrade"] },
      { name: "Salted Caramel", prices: { Regular: 58 }, addons: ["Premium Upgrade"] },
      { name: "Matcha Espresso", prices: { Regular: 58 }, addons: ["Premium Upgrade"] },
    ],
  },

  hotTea: {
    label: "Hot Tea",
    description: "12oz hot tea",
    items: [
      { name: "Green Tea", prices: { Regular: 50 }, addons: ["Extra Bag"] },
      { name: "Spearmint Tea", prices: { Regular: 50 }, addons: ["Extra Bag"] },
      { name: "Chamomile Tea", prices: { Regular: 50 }, addons: ["Extra Bag"] },
      { name: "Hibiscus Tea", prices: { Regular: 50 }, addons: ["Extra Bag"] },
      { name: "Butterfly Pea Tea", prices: { Regular: 50 }, addons: ["Extra Bag"] },
    ],
  },

  milkTea: {
    label: "Milk Tea",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Matcha", prices: { Grande: 38, Venti: 48 }, addons: ["Salty Cream", "Cream Cheese", "Oreo", "Coffee Jelly", "Boba Pearl", "Sugar Jelly", "Nata"] },
      { name: "Wintermelon", prices: { Grande: 38, Venti: 48 }, addons: ["Salty Cream", "Cream Cheese", "Oreo", "Coffee Jelly", "Boba Pearl", "Sugar Jelly", "Nata"] },
      { name: "Oreo", prices: { Grande: 38, Venti: 48 }, addons: ["Salty Cream", "Cream Cheese", "Coffee Jelly", "Boba Pearl", "Sugar Jelly", "Nata"] },
      { name: "Red Velvet", prices: { Grande: 38, Venti: 48 }, addons: ["Salty Cream", "Cream Cheese", "Oreo", "Coffee Jelly", "Boba Pearl", "Sugar Jelly", "Nata"] },
      { name: "Dark Choco", prices: { Grande: 38, Venti: 48 }, addons: ["Salty Cream", "Cream Cheese", "Oreo", "Coffee Jelly", "Boba Pearl", "Sugar Jelly", "Nata"] },
      { name: "Sugar Jelly Milk Tea", prices: { Grande: 38, Venti: 48 }, addons: ["Salty Cream", "Cream Cheese", "Oreo", "Coffee Jelly", "Boba Pearl", "Nata"] },
    ],
  },

  oolongTea: {
    label: "Oolong Tea",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Lychee", prices: { Grande: 45, Venti: 55 }, addons: ["Lemon Grass Oolong Upgrade"] },
      { name: "Peach", prices: { Grande: 45, Venti: 55 }, addons: ["Lemon Grass Oolong Upgrade"] },
      { name: "Lemon", prices: { Grande: 45, Venti: 55 }, addons: ["Lemon Grass Oolong Upgrade"] },
      { name: "Calamansi", prices: { Grande: 45, Venti: 55 }, addons: ["Lemon Grass Oolong Upgrade"] },
      { name: "Passion Fruit", prices: { Grande: 45, Venti: 55 }, addons: ["Lemon Grass Oolong Upgrade"] },
    ],
  },

  greenTea: {
    label: "Green Tea",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Strawberry Lychee", prices: { Grande: 55, Venti: 65 }, addons: [] },
      { name: "Strawberry", prices: { Grande: 55, Venti: 65 }, addons: [] },
      { name: "Lychee", prices: { Grande: 55, Venti: 65 }, addons: [] },
      { name: "Peach", prices: { Grande: 55, Venti: 65 }, addons: [] },
      { name: "Calamansi", prices: { Grande: 55, Venti: 65 }, addons: [] },
      { name: "Passion Fruit", prices: { Grande: 55, Venti: 65 }, addons: [] },
    ],
  },

  nonCoffee: {
    label: "Non-Coffee",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Strawberry Milk", prices: { Grande: 38, Venti: 48 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Blueberry Milk", prices: { Grande: 38, Venti: 48 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Oreo Milk", prices: { Grande: 38, Venti: 48 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Swissmiss", prices: { Grande: 38, Venti: 48 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Strawberry Oreo", prices: { Grande: 38, Venti: 48 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Strawberry Matcha", prices: { Grande: 38, Venti: 48 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Ube Milk", prices: { Grande: 38, Venti: 48 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Sea Salt Cocoa", prices: { Grande: 65, Venti: 75 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Choco Salt Cocoa", prices: { Grande: 65, Venti: 75 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Choco-Berry", prices: { Grande: 65, Venti: 75 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Milky Biscoff", prices: { Grande: 65, Venti: 75 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Nutella", prices: { Grande: 65, Venti: 75 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
    ],
  },

  frappuccino: {
    label: "Frappuccino",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Macchiato", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Caramel", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Dark Mocha", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Coffee Crumble", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Coffee Fudge", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Almond Fudge", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Mocha Jelly", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Coffee Jelly", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Nutella", prices: { Grande: 75, Venti: 85 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
    ],
  },

  nonCoffeeFrappe: {
    label: "Non-Coffee Frappe",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Cookies & Cream", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Milo Cream", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Strawberry", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Blueberry", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Purple Yam", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Matcha Oreo", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Matcha Strawberry", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Ube Oreo", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Chocolate Chip Cream", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
      { name: "Nutella Cream", prices: { Grande: 70, Venti: 80 }, addons: ["Oreo", "Coffee Jelly", "Extra Shot", "Boba Pearl", "Sugar Jelly", "Nata", "Milk", "Whip Cream", "Salty Cream"] },
    ],
  },

  vietnameseCoffee: {
    label: "Cà Phê Espresso",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Americano", prices: { Grande: 38, Venti: 48 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Cà Phê Español", prices: { Grande: 38, Venti: 48 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Iced Latte", prices: { Grande: 38, Venti: 48 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Matcha Latte", prices: { Grande: 38, Venti: 48 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Salted Caramel", prices: { Grande: 38, Venti: 48 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Oreo Latte", prices: { Grande: 38, Venti: 48 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Dark Mocha Latte", prices: { Grande: 38, Venti: 48 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
    ],
  },

  premium: {
    label: "Premium",
    description: "Grande 16oz / Venti 22oz",
    items: [
      { name: "Strawberry Latte", prices: { Grande: 45, Venti: 55 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Matcha Espresso", prices: { Grande: 45, Venti: 55 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Salty Cream Latte", prices: { Grande: 45, Venti: 55 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Sea Salt Latte", prices: { Grande: 45, Venti: 55 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Barista's Drink", prices: { Grande: 45, Venti: 55 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Dulce De Leche", prices: { Grande: 55, Venti: 65 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Velvet Cream Latte", prices: { Grande: 55, Venti: 65 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "White Mocha Latte", prices: { Grande: 55, Venti: 65 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Vanilla Sweet Cream", prices: { Grande: 55, Venti: 65 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Toffee Nut Latte", prices: { Grande: 55, Venti: 65 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Almond Latte", prices: { Grande: 55, Venti: 65 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Peanut Butter Latte", prices: { Grande: 70, Venti: 80 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Biscoff Latte", prices: { Grande: 70, Venti: 80 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
      { name: "Nutella Latte", prices: { Grande: 70, Venti: 80 }, addons: ["Extra Shot", "Milk", "Whip Cream", "Salty Cream", "Coffee Jelly", "Oreo"] },
    ],
  },
};

export default function Orders() {
  const [selectedCategory, setSelectedCategory] = useState("lemonade");
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedSize, setSelectedSize] = useState("");
  const [selectedAddons, setSelectedAddons] = useState([]);
  const [cart, setCart] = useState([]);
  const [cash, setCash] = useState("");
  const [table, setTable] = useState("Walk-in");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentCategory = menuData[selectedCategory];

  const total = useMemo(() => {
    return cart.reduce((sum, item) => sum + item.line_total, 0);
  }, [cart]);

  const cashValue = Number(cash) || 0;
  const change = cashValue - total;

  // ── MODAL COMPUTED VALUES ─────────────────────────────────────────────────
  // Price of the currently selected size in the modal
  const modalBasePrice = selectedItem && selectedSize
    ? (selectedItem.prices[selectedSize] || 0)
    : 0;

  // Total addon cost in the modal (+₱10 each)
  const modalAddonCost = selectedAddons.length * ADDON_PRICE;

  // Total shown in the modal before adding to cart
  const modalTotal = modalBasePrice + modalAddonCost;

  const openItemModal = (item) => {
    setSelectedItem({
      ...item,
      category: currentCategory.label,
    });
    // FIX: Default to the first size key (e.g. "Grande", not empty string)
    const firstSize = Object.keys(item.prices)[0];
    setSelectedSize(firstSize);
    setSelectedAddons([]);
  };

  const closeItemModal = () => {
    setSelectedItem(null);
    setSelectedSize("");
    setSelectedAddons([]);
  };

  const toggleAddon = (addon) => {
    setSelectedAddons((prev) =>
      prev.includes(addon)
        ? prev.filter((a) => a !== addon)
        : [...prev, addon]
    );
  };

  const addToCart = () => {
    if (!selectedItem || !selectedSize) return;

    const unitPrice = selectedItem.prices[selectedSize];
    // FIX: Include addon costs in unit_price and line_total
    const addonCost = selectedAddons.length * ADDON_PRICE;
    const totalUnitPrice = unitPrice + addonCost;

    const newItem = {
      category: selectedItem.category,
      item_name: selectedItem.name,
      // FIX: Send the size key exactly as it appears in prices (e.g. "Grande", "Venti", "Regular")
      // The backend normalize_size() will lowercase it correctly
      size: selectedSize,
      qty: 1,
      unit_price: totalUnitPrice,
      // FIX: Store addons as array of objects with name + price for payload
      addons: selectedAddons.map((name) => ({ name, price: ADDON_PRICE })),
      addons_text: selectedAddons.length ? selectedAddons.join(", ") : "None",
      line_total: totalUnitPrice,
    };

    setCart((prev) => [...prev, newItem]);
    closeItemModal();
  };

  const updateCartQty = (index, delta) => {
    setCart((prev) =>
      prev
        .map((item, i) => {
          if (i !== index) return item;
          const newQty = item.qty + delta;
          if (newQty <= 0) return null;
          return {
            ...item,
            qty: newQty,
            line_total: item.unit_price * newQty,
          };
        })
        .filter(Boolean)
    );
  };

  const removeCartItem = (index) => {
    setCart((prev) => prev.filter((_, i) => i !== index));
  };

  const clearCart = () => {
    setCart([]);
    setCash("");
    setTable("Walk-in");
  };

  const handlePayAndPrint = async () => {
    if (cart.length === 0) {
      alert("Cart is empty.");
      return;
    }

    if (cashValue < total) {
      alert("Insufficient cash.");
      return;
    }

    setIsSubmitting(true);

    try {
      const token = localStorage.getItem("token");

      const payload = {
        items: cart.map((item) => ({
          name: item.item_name,
          category: item.category,
          // FIX: size is already the correct key ("Grande", "Venti", "Regular")
          // backend normalize_size() handles lowercasing
          size: item.size,
          qty: item.qty,
          unitPrice: item.unit_price,
          // FIX: addons are already stored as [{name, price}] objects
          addons: item.addons,
        })),
        total,
        cash: cashValue,
        change,
        table,
        payment_method: "Cash",
      };

      const response = await fetch(`${API_BASE_URL}/orders/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      console.log("Order saved:", data);

      if (!response.ok) {
        alert(data.error || "Failed to process order.");
        return;
      }

      let message = `Order #${data.order_id} processed successfully.\nTotal: ₱${total.toFixed(2)}\nCash: ₱${cashValue.toFixed(2)}\nChange: ₱${Math.max(0, change).toFixed(2)}`;

      if (data.inventory_warnings && data.inventory_warnings.length > 0) {
        message += `\n\nInventory warnings:\n- ${data.inventory_warnings.join("\n- ")}`;
      }

      alert(message);
      clearCart();
    } catch (error) {
      console.error("Checkout error:", error);
      alert("Network error while processing order.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="orders-page">
      <Sidebar />
      <div className="orders-content">
        <h1>New Order</h1>
        <p>Employees can create and complete cash orders.</p>

        {/* ── CATEGORY TABS ── */}
        <div className="category-tabs">
          {Object.entries(menuData).map(([key, category]) => (
            <button
              key={key}
              className={selectedCategory === key ? "active" : ""}
              onClick={() => setSelectedCategory(key)}
            >
              {category.label}
            </button>
          ))}
        </div>

        {/* ── MENU GRID ── */}
        <div className="menu-section">
          <h2>{currentCategory.label}</h2>
          <p className="category-desc">{currentCategory.description} &bull; {currentCategory.items.length} items</p>
          <div className="menu-grid">
            {currentCategory.items.map((item, index) => {
              const prices = Object.values(item.prices);
              const priceLabel =
                prices.length === 1
                  ? `₱${prices[0]}`
                  : `₱${Math.min(...prices)} – ₱${Math.max(...prices)}`;
              const sizes = Object.keys(item.prices).join(" / ");

              return (
                <div
                  key={index}
                  className="menu-card"
                  onClick={() => openItemModal(item)}
                >
                  <h3>{item.name}</h3>
                  <p className="price-label">{priceLabel}</p>
                  <p className="size-label">{sizes}</p>
                  {item.addons.length > 0 && (
                    <p className="addon-label">+ {item.addons.length} add-ons available</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* ── CART ── */}
        <div className="cart-section">
          <h2>Cart</h2>
          {cart.length === 0 ? (
            <p>No items in cart.</p>
          ) : (
            <table className="cart-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Size</th>
                  <th>Add-ons</th>
                  <th>Qty</th>
                  <th>Unit Price</th>
                  <th>Total</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {cart.map((item, index) => (
                  <tr key={index}>
                    <td>{item.item_name}</td>
                    <td>{item.size}</td>
                    <td>{item.addons_text}</td>
                    <td>
                      <button onClick={() => updateCartQty(index, -1)}>-</button>
                      <span style={{ margin: "0 10px" }}>{item.qty}</span>
                      <button onClick={() => updateCartQty(index, 1)}>+</button>
                    </td>
                    <td>₱{item.unit_price.toFixed(2)}</td>
                    <td>₱{item.line_total.toFixed(2)}</td>
                    <td>
                      <button onClick={() => removeCartItem(index)}>Remove</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="payment-panel">
            <h3>Total: ₱{total.toFixed(2)}</h3>

            <label>Table / Customer Type</label>
            <select value={table} onChange={(e) => setTable(e.target.value)}>
              <option value="Walk-in">Walk-in</option>
              <option value="Takeout">Takeout</option>
            </select>

            <label>Cash Received</label>
            <input
              type="number"
              value={cash}
              onChange={(e) => setCash(e.target.value)}
              placeholder="Enter cash amount"
              min={0}
            />

            <h4>Change: ₱{change >= 0 ? change.toFixed(2) : "0.00"}</h4>

            <div className="payment-actions">
              <button onClick={clearCart}>Cancel Order</button>
              <button
                onClick={handlePayAndPrint}
                disabled={isSubmitting || cart.length === 0 || cashValue < total}
              >
                {isSubmitting ? "Processing..." : "Pay & Print Receipt"}
              </button>
            </div>
          </div>
        </div>

        {/* ── ITEM MODAL ── */}
        {selectedItem && (
          <div className="modal-overlay" onClick={closeItemModal}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={closeItemModal}>×</button>
              <h2>{selectedItem.name}</h2>
              <p>Choose size and optional add-ons.</p>

              {/* SIZE — toggle buttons matching the UI in screenshots */}
              <div className="size-section">
                <label>SIZE</label>
                <div className="size-buttons">
                  {Object.entries(selectedItem.prices).map(([size, price]) => (
                    <button
                      key={size}
                      className={`size-btn ${selectedSize === size ? "active" : ""}`}
                      onClick={() => setSelectedSize(size)}
                    >
                      {size === "Grande" ? "Grande 16oz" : size === "Venti" ? "Venti 22oz" : size} &nbsp;₱{price}
                    </button>
                  ))}
                </div>
              </div>

              {/* ADD-ONS */}
              {selectedItem.addons.length > 0 && (
                <div className="addons-section">
                  <label>ADD-ONS</label>
                  <div className="addons-list">
                    {selectedItem.addons.map((addon, index) => (
                      <label key={index} className="addon-option">
                        <input
                          type="checkbox"
                          checked={selectedAddons.includes(addon)}
                          onChange={() => toggleAddon(addon)}
                        />
                        <span>{addon}</span>
                        <span className="addon-price">+₱{ADDON_PRICE}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* SELECTED TOTAL */}
              <div className="modal-total">
                <span>Selected total</span>
                <span>₱{modalTotal}</span>
              </div>

              <div className="modal-actions">
                <button className="btn-cancel" onClick={closeItemModal}>Cancel</button>
                <button
                  className="btn-add"
                  onClick={addToCart}
                  disabled={!selectedSize}
                >
                  Add to cart
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}