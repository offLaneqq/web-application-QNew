import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///news.db")

#from config import API_KEY
#os.environ["API_KEY"]=API_KEY
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    news = db.execute("SELECT * FROM news ORDER BY date DESC")
    return render_template("index.html", news=news)

@app.route("/news/<id>")
def news(id):
    new = db.execute("SELECT * FROM news WHERE id=?", id)
    return render_template("new_detail.html", new=new)

@app.route("/politics")
def politics():
    new = db.execute("SELECT * FROM news ORDER BY date DESC")
    return render_template("politics.html", new=new)

@app.route("/politics/<id>")
def politicsId(id):
    new = db.execute("SELECT * FROM news WHERE id=?", id)
    return render_template("new_detail.html", new=new)

@app.route("/sport")
def sport():
    sport = db.execute("SELECT * FROM news ORDER BY date DESC")
    return render_template("sport.html", sport=sport)

@app.route("/sport/<id>")
def sportId(id):
    new = db.execute("SELECT * FROM news WHERE id=?", id)
    return render_template("new_detail.html", new=new)

@app.route("/technology")
def tech():
    tech = db.execute("SELECT * FROM news ORDER BY date DESC")
    return render_template("tech.html", tech=tech)

@app.route("/technology/<id>")
def techId(id):
    new = db.execute("SELECT * FROM news WHERE id=?", id)
    return render_template("new_detail.html", new=new)

@app.route("/war")
def war():
    war = db.execute("SELECT * FROM news ORDER BY date DESC")
    return render_template("war.html", war=war)

@app.route("/war/<id>")
def warId(id):
    new = db.execute("SELECT * FROM news WHERE id=?", id)
    return render_template("new_detail.html", new=new)

@app.route("/register", methods=["GET", "POST"])
def register():
    err = 0
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if username != '' and password != '' and confirmation != '':
            if password == confirmation:
                hash = generate_password_hash(password)

                result = db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", username=username, password=hash)

                if not result:
                    return render_template("register.html")

                session["user_id"] = result

                return redirect("/")
            else:
                err = "Введені паролі не збігаються"
                return render_template("register.html", err=err)
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    err = 0

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username != '' and password != '':
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
            # Перевірка чи користувач вірно ввід дані
            if len(rows) == 1 and check_password_hash(rows[0]["password"], password):

                session["user_id"] = rows[0]["id"]

                # Повернути користувача на головну
                news = db.execute("SELECT * FROM news ORDER BY date DESC")
                err = "Ви увійшли в систему під наступним нікнеймом - {0}.".format(username)
                return render_template("index.html", err=err, news=news)
            else:
                err = "Некоректно введений пароль або логін"
                return render_template("login.html", err=err)
        else:
            err = "Заповніть поля логіну та паролю"
            return render_template("login.html", err=err)

    else:
        return render_template("login.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    res = db.execute("SELECT * FROM users WHERE id == :id", id=session["user_id"])

    return render_template("account.html", res=res)

@app.route("/updateAccSettings", methods=["GET", "POST"])
@login_required
def update():
    err = 0
    if request.method == "POST":

        res = db.execute("SELECT * FROM users WHERE id == :id", id=session["user_id"])
        username = request.form.get("username")
        email = request.form.get("email")
        bio = request.form.get("textarea")
        phone = request.form.get("phone")

        if username != res[0]["username"] and username != "":
            db.execute("UPDATE users SET username = :username WHERE id = :id", username=username, id=session["user_id"])
            err = "Дані успішно змінено!"

        if bio != res[0]["biography"]:
            db.execute("UPDATE users SET biography = :bio WHERE id = :id", bio=bio, id=session["user_id"])
            err = "Дані успішно змінено!"

        if email != res[0]["email"] and email != "":
            db.execute("UPDATE users SET email = :email WHERE id = :id", email=email, id=session["user_id"])
            err = "Дані успішно змінено!"

        if phone != res[0]["phone"]:
            db.execute("UPDATE users SET phone = :phone WHERE id = :id", phone=phone, id=session["user_id"])
            err = "Дані успішно змінено!"

        res = db.execute("SELECT * FROM users WHERE id == :id", id=session["user_id"])
        return render_template("account.html", res=res, err=err)

    else:
        return redirect("/")
