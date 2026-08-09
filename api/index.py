import sys
import os
import json
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

# Set BASE_DIR to project root (one level up from /api)
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"

# Ensure root directory is in sys.path for Vercel module resolution
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

# Import blueprints using absolute package paths
from api.feedback import feedback_bp
from api.interview import interview_bp

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# Register API blueprints
app.register_blueprint(interview_bp)
app.register_blueprint(feedback_bp)

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/api/candidates")
def candidates():
    """Return the real candidate profiles used by the interview agents."""
    candidates_file = DATA_DIR / "candidates.json"
    if not candidates_file.exists():
        return jsonify({"error": "Candidates data file not found"}), 404
        
    try:
        with candidates_file.open(encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data.get("candidates", []))
    except Exception as e:
        return jsonify({"error": f"Failed to load candidates: {str(e)}"}), 500


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def index():
    if (FRONTEND_DIR / "index.html").exists():
        return send_from_directory(FRONTEND_DIR, "index.html")
    return jsonify({"status": "API is running", "message": "Frontend index.html not found"}), 200


@app.get("/<path:path>")
def serve_static_pages(path):
    # Do not catch unhandled /api requests as HTML pages
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404

    target_file = FRONTEND_DIR / path
    if target_file.exists() and target_file.is_file():
        return send_from_directory(FRONTEND_DIR, path)

    # Fallback to index.html for SPA client-side routing
    if (FRONTEND_DIR / "index.html").exists():
        return send_from_directory(FRONTEND_DIR, "index.html")
        
    return jsonify({"error": "Resource not found"}), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )