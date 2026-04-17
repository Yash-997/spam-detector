import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from model import predict, ensure_data_file, load_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "app.db")

app = Flask(__name__)


def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            result TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_result(email, result, confidence):
    conn = get_db()
    conn.execute(
        "INSERT INTO history (email, result, confidence, timestamp) VALUES (?, ?, ?, ?)",
        (email[:300], result, confidence, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.execute("""
        DELETE FROM history WHERE id NOT IN (
            SELECT id FROM history ORDER BY id DESC LIMIT 20
        )
    """)
    conn.commit()
    conn.close()


def get_history():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    spam = conn.execute("SELECT COUNT(*) FROM history WHERE result='spam'").fetchone()[0]
    ham = total - spam
    conn.close()
    return {"total": total, "spam": spam, "safe": ham}


@app.route("/")
def index():
    stats = get_stats()
    history = get_history()
    return render_template("index.html", stats=stats, history=history)


@app.route("/predict", methods=["POST"])
def predict_route():
    data = request.get_json(silent=True)
    text = ""

    if data and "text" in data:
        text = data["text"].strip()
    else:
        text = request.form.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        label, confidence = predict(text)
        save_result(text, label, confidence)
        return jsonify({"result": label, "confidence": confidence})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_db()
    ensure_data_file()
    load_model()  # make sure model.py retrains

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)