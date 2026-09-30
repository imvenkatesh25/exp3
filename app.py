from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from chatbot import CybersecurityChatbot
from security_utils import check_password_strength, analyze_url, generate_security_tips
from database import (
    init_db, save_message, get_chat_history, create_user, verify_user,
    is_admin, get_dashboard_stats, get_users, get_activity,
    get_knowledge, add_knowledge, update_knowledge, delete_knowledge,
    get_topics, create_activity
)
from functools import wraps

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY_BEFORE_DEPLOYMENT"
init_db()
bot = CybersecurityChatbot()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session or not is_admin(session["user_id"]):
            flash("Administrator access required.", "error")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return redirect(url_for("index") if "user_id" in session else url_for("login"))

@app.route("/index")
@login_required
def index():
    return render_template("index.html", username=session.get("username"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = verify_user(username, password)
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            create_activity(user["id"], "LOGIN", "User logged in")
            return redirect(url_for("admin_dashboard") if user["is_admin"] else url_for("index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            flash("Username must be at least 3 characters and password at least 6 characters.", "error")
        elif create_user(username, password):
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists.", "error")
    return render_template("register.html")

@app.route("/logout")
def logout():
    if session.get("user_id"):
        create_activity(session["user_id"], "LOGOUT", "User logged out")
    session.clear()
    return redirect(url_for("login"))

@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    response = bot.respond(message)
    save_message(session["user_id"], message, response)
    create_activity(session["user_id"], "CHAT", message[:200])
    return jsonify({"response": response})

@app.route("/api/history")
@login_required
def history():
    return jsonify(get_chat_history(session["user_id"]))

@app.route("/api/password-check", methods=["POST"])
@login_required
def password_check():
    data = request.get_json(silent=True) or {}
    return jsonify(check_password_strength(data.get("password", "")))

@app.route("/api/url-check", methods=["POST"])
@login_required
def url_check():
    data = request.get_json(silent=True) or {}
    result = analyze_url(data.get("url", ""))
    create_activity(session["user_id"], "URL_CHECK", result.get("input", "")[:200])
    return jsonify(result)

@app.route("/api/tips")
@login_required
def tips():
    return jsonify({"tips": generate_security_tips()})

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "admin_dashboard.html",
        stats=get_dashboard_stats(),
        users=get_users(),
        activities=get_activity(100),
        knowledge=get_knowledge()
    )

@app.route("/admin/knowledge/add", methods=["POST"])
@admin_required
def knowledge_add():
    topic = request.form.get("topic", "").strip()
    keywords = request.form.get("keywords", "").strip()
    answer = request.form.get("answer", "").strip()
    if topic and keywords and answer:
        add_knowledge(topic, keywords, answer)
        create_activity(session["user_id"], "ADMIN_KNOWLEDGE_ADD", topic)
        flash("Knowledge item added.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/knowledge/update/<int:item_id>", methods=["POST"])
@admin_required
def knowledge_update(item_id):
    update_knowledge(
        item_id,
        request.form.get("topic", "").strip(),
        request.form.get("keywords", "").strip(),
        request.form.get("answer", "").strip()
    )
    create_activity(session["user_id"], "ADMIN_KNOWLEDGE_UPDATE", str(item_id))
    flash("Knowledge item updated.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/knowledge/delete/<int:item_id>", methods=["POST"])
@admin_required
def knowledge_delete(item_id):
    delete_knowledge(item_id)
    create_activity(session["user_id"], "ADMIN_KNOWLEDGE_DELETE", str(item_id))
    flash("Knowledge item deleted.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/api/activity")
@admin_required
def admin_activity():
    return jsonify(get_activity(250))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
