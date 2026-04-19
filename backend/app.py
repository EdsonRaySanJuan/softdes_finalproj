import os
from flask import Flask, jsonify
from flask_cors import CORS

from db import init_db
from routes.report_routes import report_bp
from routes.dashboard_routes import dashboard_bp
from routes.order_routes import order_bp
from routes.inventory_routes import inventory_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.rpa_routes import rpa_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://softdes-finalproj.vercel.app",
                "http://localhost:3000",
                "http://localhost:5173"
            ]
        }
    },
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

init_db()

app.register_blueprint(report_bp, url_prefix="/api/reports")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(order_bp, url_prefix="/api/orders")
app.register_blueprint(inventory_bp, url_prefix="/api/inventory")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/users")
app.register_blueprint(rpa_bp, url_prefix="/api/rpa")


@app.route("/")
def home():
    return {"message": "Cafe POS Backend is running", "status": "online"}


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)