import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
import json

from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
load_dotenv(BASE_DIR / ".env")

from api.feedback import feedback_bp
from api.interview import interview_bp

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# Register API blueprints
app.register_blueprint(interview_bp)
app.register_blueprint(feedback_bp)

# ---------------------------------------------------------
# API Endpoints MUST be defined before wildcard catch-all
# ---------------------------------------------------------

@app.get("/api/candidates")
def candidates():
    """Return the real candidate profiles used by the interview agents."""
    try:
        with (DATA_DIR / "candidates.json").open(encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data.get("candidates", []))
    except Exception as e:
        return jsonify({"error": f"Failed to load candidates: {str(e)}"}), 500


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:path>")
def serve_static_pages(path):
    # Do not catch unhandled /api requests as HTML pages
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404

    if (FRONTEND_DIR / path).exists():
        return send_from_directory(FRONTEND_DIR, path)

    # Fallback to index.html for client-side routing
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
    