from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {"message": "Cafe POS Backend minimal test", "status": "online"}