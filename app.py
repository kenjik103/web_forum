from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, class_code_generator, get_datetime, DataBase
import os

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = DataBase("forum.db")

# represents constants location in db tuple

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """leave class feature"""
    if request.method == "POST":
        code = request.form.get("leave-class-code")
        db.delete_from_db("DELETE FROM classes WHERE user_id = (?) AND class_code = (?);", (session["user_id"], code))
        return redirect("/")
    else:
        classes = db.select_priority_from_db("SELECT * FROM classes WHERE user_id = (?);", (session["user_id"], ))
        return render_template("/index.html", classes=classes,  user_type = session["user_type"])


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user info
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return redirect("/login")

        elif not request.form.get("password"):
            return redirect("/login")

        rows = db.select_priority_from_db("SELECT * FROM users WHERE username = (?);", (request.form.get("username"), ))

        if len(rows) != 1 or not check_password_hash(
            rows[0][2], request.form.get("password")
        ):
            return redirect("/login")

        session["user_id"] = rows[0][0]
        session["user_type"] = rows[0][3]

        return redirect("/")
    else:
        return render_template("/login.html")



@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        user_type = request.form.get("radio")

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

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/create_class", methods=["GET", "POST"])
@login_required
def create_class():
    if request.method == "POST":
        class_name = request.form.get("class-name")
        class_description = request.form.get("class-description")
        class_code = class_code_generator(session["user_id"])
        bg_img = request.form.get('radio')

        db.insert_into_db("INSERT INTO classes (user_id, class_code, class_name, class_description, bg_img) VALUES (?, ?, ?, ?, ?);", (session["user_id"], class_code, class_name, class_description, bg_img))

        return redirect("/")
    
    else:
        return render_template("/create_class.html")
    

@app.route("/join_class", methods=["GET", "POST"])
@login_required
def join_class():
    if request.method == "POST":
        code = request.form.get("class-code")

        if code == None:
            return redirect("/")

        class_info = db.select_priority_from_db("SELECT class_name, class_description, bg_img FROM classes WHERE class_code = (?);", (code, ))
        user_classes = db.select_priority_from_db("SELECT class_name, class_description, bg_img FROM classes WHERE user_id = (?);", (session["user_id"],))

        if len(class_info) == 0:
            return redirect("/")

        if class_info[0] not in user_classes:
            class_name = class_info[0][0]
            class_description = class_info[0][1]
            bg_img = class_info[0][2]
            
            db.insert_into_db("INSERT INTO classes (user_id, class_code, class_name, class_description, bg_img) VALUES (?, ?, ?, ?, ?);", (session["user_id"], code, class_name, class_description, bg_img))
        return redirect("/")
    else:
        return render_template("/join_class.html")
    
@app.route("/course", methods=["GET", "POST"])
@login_required
def class_index():
    if request.method == "POST":
        post_type = request.form.get("post-button")
        code = request.form.get("code")
        date_time = get_datetime()
        date = date_time[0]
        time = date_time[1]

        if code:
            session["current_class"] = code

        post_body = request.form.get("post-body")
        if post_type == "main":
            post_title = request.form.get("post-title")
            if post_title:
                db.insert_into_db("INSERT INTO discussion (user_id, class_code, post_title, post_body, date, time) VALUES (?, ?, ?, ?, ?, ?);", (session["user_id"], session["current_class"], post_title, post_body, date, time))
        elif post_type == "reply":
            corresponding_id = request.form.get("post-id")
            if post_body:
                db.insert_into_db("INSERT INTO replys (corresponding_post_id, user_id, class_code, post_body, date, time) VALUES (?, ?, ?, ?, ?, ?);", (corresponding_id, session["user_id"], session["current_class"], post_body, date, time))
        return redirect("/course")
    else:
        current_class = db.select_priority_from_db("SELECT class_name, class_description FROM classes WHERE class_code = (?);", (session["current_class"],))
        discussion = db.select_priority_from_db("SELECT username, post_title, post_body, date, time, post_id FROM discussion JOIN users ON user_id = users.id WHERE class_code = (?) ORDER BY date DESC, time DESC;", (session["current_class"],))
        reply_map = {}
        for post in discussion:
            replys = db.select_priority_from_db("SELECT username, post_body, date, time FROM replys JOIN users ON user_id = users.id WHERE class_code = ? AND corresponding_post_id = ? ORDER BY date ASC, time ASC;", (session["current_class"], post[5]))
            reply_map[post[5]] = replys
        return render_template("/course.html", discussion=discussion, current_class=current_class, code=session["current_class"], reply_map=reply_map)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))