from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fitness_secret_key"

DB_NAME = "fitness.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        workout_name TEXT,
        sets_count INTEGER,
        reps_count INTEGER,
        duration INTEGER,
        calories INTEGER,
        created_at TEXT
    )
""")    

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = email
            return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT workout_name, sets_count, reps_count, duration, calories, created_at
        FROM workouts
        WHERE user_email=?
        ORDER BY id DESC
    """, (session["user"],))

    workouts = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", workouts=workouts)

@app.route("/bmi", methods=["GET", "POST"])
def bmi():
    result = None
    status = None

    if request.method == "POST":
        height = float(request.form["height"]) / 100
        weight = float(request.form["weight"])

        result = round(weight / (height * height), 2)

        if result < 18.5:
            status = "Underweight"
        elif result < 25:
            status = "Normal"
        elif result < 30:
            status = "Overweight"
        else:
            status = "Obese"

    return render_template("bmi.html", result=result, status=status)

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("profile.html")

@app.route("/diet")
def diet():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("diet.html")


@app.route("/workout", methods=["GET", "POST"])
def workout():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        workout_name = request.form["workout_name"]
        sets_count = request.form["sets_count"]
        reps_count = request.form["reps_count"]
        duration = request.form["duration"]
        calories = request.form["calories"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO workouts
            (user_email, workout_name, sets_count, reps_count, duration, calories, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user"],
            workout_name,
            sets_count,
            reps_count,
            duration,
            calories,
            datetime.now().strftime("%Y-%m-%d")
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("workout.html")

@app.route("/progress")
def progress():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT workout_name, calories, created_at
        FROM workouts
        WHERE user_email=?
        ORDER BY id ASC
    """, (session["user"],))

    records = cur.fetchall()
    conn.close()

    labels = []
    calories = []

    for record in records:
        labels.append(record[2])
        calories.append(record[1])

    return render_template(
        "progress.html",
        labels=labels,
        calories=calories
    )

@app.route("/water")
def water():
    return render_template("water.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)