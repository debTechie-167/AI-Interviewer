"""Local development entrypoint. Vercel uses api/index.py directly."""

from pathlib import Path

from flask import jsonify, send_from_directory

from api.index import app

PUBLIC_DIR = Path(__file__).resolve().parent / "public"


@app.get("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.get("/interview")
def serve_interview():
    return send_from_directory(PUBLIC_DIR, "interview.html")


@app.get("/report")
def serve_report():
    return send_from_directory(PUBLIC_DIR, "report.html")


@app.get("/<path:filename>")
def serve_public(filename):
    if filename.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404

    target = PUBLIC_DIR / filename
    if target.is_file():
        return send_from_directory(PUBLIC_DIR, filename)

    return send_from_directory(PUBLIC_DIR, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
