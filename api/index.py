import sys
import json
from pathlib import Path
from flask import Flask, jsonify
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from api.feedback import feedback_bp
from api.interview import interview_bp

app = Flask(__name__)

app.register_blueprint(interview_bp)
app.register_blueprint(feedback_bp)


@app.get("/api/candidates")
def candidates():
    """Return candidate profiles used by the interview UI."""
    candidates_file = DATA_DIR / "candidates.json"
    if not candidates_file.exists():
        return jsonify({"error": "Candidates data file not found"}), 404

    try:
        with candidates_file.open(encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data.get("candidates", []))
    except Exception as exc:
        return jsonify({"error": f"Failed to load candidates: {exc}"}), 500


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})
