from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, DataBase

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = DataBase("forum.db")

# represents constants location in db tuple
ID = 0
USERNAME = 1
PASSWORD = 2

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    return render_template("/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return redirect("/login")

        elif not request.form.get("password"):
            return redirect("/login")

        rows = db.select_priority_from_db("SELECT * FROM users WHERE username = (?);", request.form.get("username"))

        print(rows)

        if not rows:
            return redirect("/login")

        session["user_id"] = rows[0][ID]

        return redirect("/")
    else:
        return render_template("/login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        user_type = request.form.get("registerRadio")

        if not username:
            return render_template("/register.html")

        if not password or not confirmation:
            return render_template("/register.html")

        if password != confirmation:
            return render_template("/register.html")

        rows = db.select_from_db("SELECT * FROM users;")

        for row in rows:
            if username in row:
                return render_template("/register.html")

        db.insert_into_db("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?);", (username, generate_password_hash(password), user_type))

        return redirect("/")
    else:
        return render_template("/register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
