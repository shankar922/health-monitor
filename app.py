from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ----------------------------
# Database Initialization
# ----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # Create health data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            heart_rate INTEGER,
            blood_pressure TEXT,
            risk TEXT
        )
    """)

    conn.commit()
    conn.close()


# 🔥 IMPORTANT: Run DB creation when app loads (works on Render)
init_db()


# ----------------------------
# Home Route
# ----------------------------
@app.route("/")
def home():
    if "user_id" in session:
        return render_template("dashboard.html")
    return redirect(url_for("login"))


# ----------------------------
# Register Route
# ----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, password),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists!"

    return render_template("register.html")


# ----------------------------
# Login Route
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password),
        ).fetchone()

        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect(url_for("home"))
        else:
            return "Invalid email or password"

    return render_template("login.html")


# ----------------------------
# Logout
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----------------------------
# Run App (Local Only)
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)


    # ----------------------------
# Check Health Route
# ----------------------------
@app.route("/check_health", methods=["POST"])
def check_health():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        heart_rate = request.form["heart_rate"]
        blood_pressure = request.form["blood_pressure"]

        # Simple health logic
        if int(heart_rate) > 100:
            risk = "High Risk"
        else:
            risk = "Normal"

        # Save to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO health_data (user_id, heart_rate, blood_pressure, risk) VALUES (?, ?, ?, ?)",
            (session["user_id"], heart_rate, blood_pressure, risk),
        )

        conn.commit()
        conn.close()

        return render_template("result.html", risk=risk)

    return render_template("check_health.html")