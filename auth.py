import json
from flask import session, redirect, url_for

def load_users():
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def authenticate_user(code):
    users = load_users()
    for username, data in users.items():
        if data["code"] == code:
            session["username"] = username
            session["role"] = data.get("role", "user")
            return True
    return False

def logout_user():
    session.clear()

def login_required(view_func):
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper
