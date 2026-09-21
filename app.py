import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from flask_session import Session
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "Missing OPENAI_API_KEY. Create a .env file in the same folder as app.py with: OPENAI_API_KEY=your_key_here"
    )

client = OpenAI(api_key=api_key)

PROFILE_PATH = Path(__file__).resolve().parent / "agent_profile.txt"
PROFILE_TEXT = PROFILE_PATH.read_text(encoding="utf-8").strip()

MAX_HISTORY_MESSAGES = 20
MAX_MESSAGES_PER_SESSION = 60  # basic abuse/cost guard for a public kiosk link
MAX_MESSAGE_LENGTH = 500

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24).hex()
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Store session data server-side; conversation history overflows the 4KB cookie limit otherwise.
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=str(Path(__file__).resolve().parent / ".flask_session"),
    SESSION_PERMANENT=False,
)
Session(app)


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message is empty."}), 400
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": "That message is too long for Jimini."}), 400

    sent_count = session.get("sent_count", 0)
    if sent_count >= MAX_MESSAGES_PER_SESSION:
        return jsonify({"error": "Jimini needs a breather. Come back in a bit."}), 429

    history = session.get("history", [])
    history.append({"role": "user", "content": user_message})
    history = history[-MAX_HISTORY_MESSAGES:]

    messages = [{"role": "system", "content": PROFILE_TEXT}, *history]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
    except Exception:
        return jsonify({"error": "Jimini is having a moment. Try again shortly."}), 502

    reply = response.choices[0].message.content.strip()
    history.append({"role": "assistant", "content": reply})

    session["history"] = history[-MAX_HISTORY_MESSAGES:]
    session["sent_count"] = sent_count + 1

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
