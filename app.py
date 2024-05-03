from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, class_code_generator, get_datetime, DataBase

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = DataBase("forum.db")

# represents constants location in db tuple
ID = 0
USERNAME = 1
PASSWORD = 2
USER_TYPE = 3

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
    """leave class feture"""
    if request.method == "POST":
        code = request.form.get("leave_class_code")
        print(code)
        db.delete_from_db("DELETE FROM classes WHERE user_id = (?) AND class_code = (?);", (session["user_id"], code))
        return redirect("/")
    else:
        classes = db.select_priority_from_db("SELECT * FROM classes WHERE user_id = (?);", (session["user_id"], ))
        session["current_class"] = None
        return render_template("/index.html", classes=classes)


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
            rows[0][PASSWORD], request.form.get("password")
        ):
            return redirect("/login")

        session["user_id"] = rows[0][ID]
        session["user_type"] = rows[0][USER_TYPE]

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

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/create_class", methods=["GET", "POST"])
def create_class():
    if request.method == "POST":
        class_name = request.form.get("class_name")
        class_description = request.form.get("class_description")
        class_code = class_code_generator(session["user_id"])

        db.insert_into_db("INSERT INTO classes (user_id, class_code, class_name, class_description) VALUES (?, ?, ?, ?);", (session["user_id"], class_code, class_name, class_description))

        return redirect("/")
    
    else:
        return render_template("/create_class.html")
    

@app.route("/join_class", methods=["GET", "POST"])
def join_class():
    if request.method == "POST":
        code = request.form.get("class_code")

        if code == None:
            return redirect("/")

        class_info = db.select_priority_from_db("SELECT class_name, class_description FROM classes WHERE class_code = (?);", (code, ))
        user_classes = db.select_priority_from_db("SELECT class_name, class_description FROM classes WHERE user_id = (?);", (session["user_id"],))

        if class_info == None:
            return redirect("/")

        if class_info[0] not in user_classes:
            class_name = class_info[0][0]
            class_description = class_info[0][1]
            
            db.insert_into_db("INSERT INTO classes (user_id, class_code, class_name, class_description) VALUES (?, ?, ?, ?);", (session["user_id"], code, class_name, class_description))
        return redirect("/")
    else:
        return render_template("/join_class.html")
    
@app.route("/course", methods=["GET", "POST"])
def class_index():
    if request.method == "POST":
        code = request.form.get("code")
        date_time = get_datetime()
        date = date_time[0]
        time = date_time[1]
 
        if code:
            session["current_class"] = code
            
        post_title = request.form.get("post_title")
        post_body = request.form.get("post_body")

        if post_title:
            db.insert_into_db("INSERT INTO discussion (user_id, class_code, post_title, post_body, date, time) VALUES (?, ?, ?, ?, ?, ?);", (session["user_id"], session["current_class"], post_title, post_body, date, time))

        return redirect("/course")
    else:
        code = session["current_class"]
        current_class = db.select_priority_from_db("SELECT class_name, class_description FROM classes WHERE class_code = (?);", (session["current_class"],))
        discussion = db.select_priority_from_db("SELECT username, post_title, post_body, date, time FROM discussion JOIN users ON user_id = users.id WHERE class_code = (?) ORDER BY date, time ;", (session["current_class"],))
        return render_template("/course.html", discussion=discussion, current_class=current_class, code=code)

    
if __name__ == "__main__":
    app.run(port=8000, debug=True)