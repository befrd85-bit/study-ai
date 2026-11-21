import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY is not configured on the server."}), 500

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    topic = data.get("topic") or "General Study"

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    system_prompt = (
        f"You are a clear, methodical university Study Assistant. Topic: {topic}. "
        "Explain concepts step by step with relatable examples, generate practice questions "
        "when asked for a quiz, and identify mistakes before giving full solutions when checking answers."
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": question}]}],
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        result = r.json()

        if r.status_code != 200:
            msg = result.get("error", {}).get("message", "AI service error.")
            return jsonify({"error": msg}), r.status_code

        candidates = result.get("candidates") or []
        parts = (candidates[0].get("content") or {}).get("parts") or [] if candidates else []
        answer = parts[0].get("text") if parts else "No response returned."

        return jsonify({"answer": answer})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
