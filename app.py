from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from functools import wraps
import threading
import os

app = Flask(__name__)
app.secret_key = "супер_секретний_ключ"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Стан ---
stop_flag = {"stop": False}
status_log = []
post_counter = {"count": 0}

# --- Коди доступу ---
VALID_CODES = {
    "1234": "Іван",
    "abcd": "Марія",
    "test": "Тестовий",
}

# --- Авторизація ---
def authenticate_user(code):
    if code in VALID_CODES:
        session["logged_in"] = True
        session["username"] = VALID_CODES[code]
        return True
    return False

def logout_user():
    session.clear()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- Імпортуємо логіку ---
from fb_bot_logic import post_to_facebook_groups  # Переконайся, що цей файл існує

# --- Роутинг ---
@app.route("/")
@login_required
def index():
    return render_template("index.html", status=status_log, counter=post_counter["count"], user=session["username"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        code = request.form.get("code")
        if authenticate_user(code):
            return redirect(url_for("index"))
        return render_template("login.html", error="Невірний код")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/post", methods=["POST"])
@login_required
def post():
    global status_log

    post_text = request.form.get("post_text", "")
    group_links_raw = request.form.get("group_links", "")
    group_links = [link.strip() for link in group_links_raw.splitlines() if link.strip()]
    
    photo = request.files.get("photo")
    if not photo or photo.filename == "":
        status_log.append("❌ Фото не завантажено")
        return redirect("/")

    image_path = os.path.join(UPLOAD_FOLDER, photo.filename)
    photo.save(image_path)

    status_log.clear()
    post_counter["count"] = 0
    stop_flag["stop"] = False

    threading.Thread(target=post_to_facebook_groups, args=(
        post_text, group_links, image_path, status_log, stop_flag, post_counter
    )).start()

    return redirect("/")

@app.route("/stop")
@login_required
def stop():
    stop_flag["stop"] = True
    status_log.append("🛑 Зупинка ініційована користувачем.")
    return redirect("/")

@app.route("/status")
@login_required
def status():
    return jsonify({
        "log": status_log,
        "count": post_counter["count"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)



