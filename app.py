"""
Sentiment & Emotion Analyzer
Flask backend that accepts text input, runs it through Hugging Face
sentiment + emotion models, stores results in SQLite, and returns
data for charting on the frontend.
"""

import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify

from models.analyzer import TextAnalyzer
from database.db import init_db, save_analysis, get_all_analyses, get_summary_stats

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Initialize the ML models once at startup (avoids reloading on every request)
analyzer = TextAnalyzer()

# Initialize the SQLite database (creates table if it doesn't exist)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "analysis.db")
init_db(DB_PATH)


@app.route("/")
def index():
    """Home page with the text input form."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Accepts JSON: { "text": "..." }  OR a pasted block with multiple
    lines (each line treated as a separate entry, e.g. multiple reviews).
    Returns sentiment + emotion breakdown for each line plus aggregate stats.
    """
    data = request.get_json(silent=True) or {}
    raw_text = data.get("text", "").strip()

    if not raw_text:
        return jsonify({"error": "No text provided."}), 400

    # Split on newlines so users can paste multiple reviews/tweets at once.
    # Falls back to treating the whole block as one entry if no newlines.
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    if not lines:
        return jsonify({"error": "No valid text found."}), 400

    results = []
    for line in lines:
        result = analyzer.analyze(line)
        save_analysis(
            DB_PATH,
            text=line,
            sentiment_label=result["sentiment"]["label"],
            sentiment_score=result["sentiment"]["score"],
            emotion_label=result["emotion"]["label"],
            emotion_score=result["emotion"]["score"],
            created_at=datetime.utcnow().isoformat(),
        )
        results.append({"text": line, **result})

    return jsonify({
        "results": results,
        "count": len(results),
    })


@app.route("/history")
def history():
    """Page showing all past analyses with aggregate charts."""
    return render_template("history.html")


@app.route("/api/history")
def api_history():
    """Returns all stored analyses as JSON, plus summary counts for charts."""
    records = get_all_analyses(DB_PATH)
    stats = get_summary_stats(DB_PATH)
    return jsonify({"records": records, "stats": stats})


if __name__ == "__main__":
    # Most hosting platforms (Render, Railway, etc.) inject a PORT env var
    # and expect the app to bind to it - falls back to 5000 for local dev.
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
