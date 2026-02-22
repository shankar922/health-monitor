from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "health_secret_key"

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    risk = None

    if request.method == "POST":
        heart_rate = int(request.form["heart_rate"])
        bp = int(request.form["bp"])
        sugar = int(request.form["sugar"])

        # Risk logic
        if heart_rate < 90 and bp < 120 and sugar < 140:
            risk = "LOW RISK 🟢"
        elif heart_rate < 110 and bp < 140:
            risk = "MEDIUM RISK 🟡"
        else:
            risk = "HIGH RISK 🔴 ALERT!"

        # Save to database
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO health (user_id, heart_rate, bp, sugar, risk) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], heart_rate, bp, sugar, risk)
        )
        conn.commit()
        conn.close()

    return render_template("dashboard.html", risk=risk)

# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    records = conn.execute(
        "SELECT heart_rate, bp, sugar, risk FROM health WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("history.html", records=records)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()
