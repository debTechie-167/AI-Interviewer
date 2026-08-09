
import json
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
load_dotenv(BASE_DIR / ".env")

from api.feedback import feedback_bp



from api.interview import (
    interview_bp
)

# The frontend is deliberately served by Flask so browser requests to /api/*
# and page navigation use the same origin in local development.
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

app.register_blueprint(
    interview_bp
)

app.register_blueprint(feedback_bp)



@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/candidates")
def candidates():
    """Return the real candidate profiles used by the interview agents."""
    with (DATA_DIR / "candidates.json").open(encoding="utf-8") as file:
        data = json.load(file)
    return jsonify(data.get("candidates", []))


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
