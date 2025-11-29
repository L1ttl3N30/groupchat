from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    abort,
)
from datetime import timedelta

from models import init_db, add_message, get_messages, clear_messages

app = Flask(__name__)

# NOTE: For a real deployment, change this to a strong, random value
# and keep it secret.
app.secret_key = "replace-with-a-long-random-secret-key"

# Session lifetime (for optional username)
app.permanent_session_lifetime = timedelta(days=30)

# Optional simple admin feature: clearing messages.
# Leave this False for normal use.
ADMIN_ENABLED = False

# Optional simple admin password for /admin/clear (if enabled).
ADMIN_PASSWORD = "changeme-admin-password"


@app.before_first_request
def setup_database():
    init_db()


@app.route("/", methods=["GET"])
def index():
    username = session.get("username", "")
    return render_template("chat.html", username=username)


@app.route("/send", methods=["POST"])
def send_message():
    text = request.form.get("text", "").strip()
    username = request.form.get("username", "").strip()

    if username:
        # Store username in session
        session.permanent = True
        session["username"] = username
    else:
        # Fallback to existing session username if provided
        username = session.get("username") or "Anonymous"

    if not text:
        return jsonify({"status": "error", "error": "Message is empty"}), 400

    if len(text) > 2000:
        return jsonify({"status": "error", "error": "Message too long"}), 400

    add_message(username, text)
    return jsonify({"status": "ok"})


@app.route("/messages", methods=["GET"])
def messages():
    msgs = get_messages()
    return jsonify(msgs)


@app.route("/admin/clear", methods=["POST"])
def admin_clear():
    if not ADMIN_ENABLED:
        abort(404)

    password = request.form.get("password", "")
    if password != ADMIN_PASSWORD:
        return jsonify({"status": "error", "error": "Invalid admin password"}), 403

    clear_messages()
    return jsonify({"status": "ok", "message": "All messages cleared"})


if __name__ == "__main__":
    # Listen on all interfaces, port 5000 so LAN devices can access it.
    # Access from other devices on the same LAN with:
    #   http://<server-local-ip>:5000
    app.run(host="0.0.0.0", port=5000, debug=False)
