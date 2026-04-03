from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime
from predict import predict_diabetes
from groq import Groq
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ==============================
# PROFILE PIC FOLDER
# ==============================
UPLOAD_FOLDER = "static/profile_pics"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# GROQ AI
# ==============================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# ==============================
# DATABASE INIT
# ==============================
def init_db():

    conn = sqlite3.connect("diabetes.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user',
            profile_pic TEXT DEFAULT 'default.png'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            result TEXT,
            risk REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ==============================
# ROOT
# ==============================
@app.route("/")
def landing():
    return render_template("landing.html")



# ==============================
# REGISTER
# ==============================
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)

        conn = sqlite3.connect("diabetes.db")
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users(username,email,password) VALUES(?,?,?)",
                (username,email,hashed)
            )
            conn.commit()
            flash("Registration successful")
            return redirect(url_for("login"))

        except:
            flash("Username or Email already exists")

        finally:
            conn.close()

    return render_template("register.html")

# ==============================
# LOGIN
# ==============================
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("diabetes.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        conn.close()

        print("LOGIN DEBUG:", user)

        if user is None:
            flash("User not found")
            return redirect(url_for("login"))

        stored_password = user[3]

        if check_password_hash(stored_password, password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect(url_for("home"))

        else:
            flash("Incorrect password")
            return redirect(url_for("login"))

    return render_template("login.html")

# ==============================
# LOGOUT
# ==============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==============================
# HOME / PREDICTION
# ==============================
@app.route("/home", methods=["GET","POST"])
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    result = None
    risk_score = None

    if request.method == "POST":

        try:

            pregnancies = float(request.form.get("Pregnancies",0))
            glucose = float(request.form.get("Glucose",0))
            bp = float(request.form.get("BloodPressure",0))
            skin = float(request.form.get("SkinThickness",0))
            insulin = float(request.form.get("Insulin",0))
            bmi = float(request.form.get("BMI",0))
            dpf = float(request.form.get("DiabetesPedigreeFunction",0))
            age = float(request.form.get("Age",0))

            family_history = float(request.form.get("FamilyHistory",0))
            physical_activity = float(request.form.get("PhysicalActivity",0))

            data = [
                pregnancies,
                glucose,
                bp,
                skin,
                insulin,
                bmi,
                dpf,
                age,
                family_history,
                physical_activity
            ]

            prediction, probability = predict_diabetes(data)

            result = prediction
            risk_score = round(probability * 100, 2)

            session["last_result"] = result
            session["last_risk"] = risk_score

            conn = sqlite3.connect("diabetes.db")
            c = conn.cursor()

            c.execute("""
                INSERT INTO predictions(user_id,result,risk,timestamp)
                VALUES(?,?,?,?)
            """,(
                session["user_id"],
                result,
                risk_score,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print("❌ Prediction Error:", e)

    return render_template(
        "index.html",
        result=result,
        risk_score=risk_score
    )
# ==============================
# HISTORY
# ==============================
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("diabetes.db")
    c = conn.cursor()

    c.execute("""
        SELECT result,risk,timestamp
        FROM predictions
        WHERE user_id=?
        ORDER BY id DESC
    """,(session["user_id"],))

    records = c.fetchall()

    conn.close()

    return render_template("history.html", records=records)

# ==============================
# PROFILE
# ==============================
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("diabetes.db")
    c = conn.cursor()

    user_id = session["user_id"]

    c.execute(
        "SELECT username,email,role,profile_pic FROM users WHERE id=?",
        (user_id,)
    )

    user = c.fetchone()

    print("DEBUG USER:", user)   # 👈 check terminal

    c.execute(
        "SELECT COUNT(*) FROM predictions WHERE user_id=?",
        (user_id,)
    )

    prediction_count = c.fetchone()[0]

    conn.close()

    return render_template(
    "profile.html",
    username=user[0],
    email=user[1],
    role=user[2],
    profile_pic=user[3],
    prediction_count=prediction_count
)

    
# ==============================
# UPLOAD PROFILE PIC
# ==============================
@app.route("/upload_profile_pic", methods=["POST"])
def upload_profile_pic():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if "profile_pic" not in request.files:
        return redirect(url_for("profile"))

    file = request.files["profile_pic"]

    if file.filename == "":
        return redirect(url_for("profile"))

    allowed = {"png","jpg","jpeg"}

    if "." in file.filename and file.filename.rsplit(".",1)[1].lower() in allowed:

        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect("diabetes.db")
        c = conn.cursor()

        c.execute(
            "UPDATE users SET profile_pic=? WHERE id=?",
            (filename, session["user_id"])
        )

        conn.commit()
        conn.close()

    return redirect(url_for("profile"))


@app.route("/edit_profile", methods=["GET","POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("diabetes.db")
    c = conn.cursor()

    user_id = session["user_id"]

    # UPDATE EMAIL
    if request.method == "POST":

        new_email = request.form["email"]

        c.execute(
            "UPDATE users SET email=? WHERE id=?",
            (new_email, user_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("profile"))

    # GET CURRENT EMAIL
    c.execute(
        "SELECT email FROM users WHERE id=?",
        (user_id,)
    )

    user = c.fetchone()

    conn.close()

    if user:
        email = user[0]
    else:
        email = ""

    return render_template("edit_profile.html", email=email)

@app.route("/change_password", methods=["GET","POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("diabetes.db")
    c = conn.cursor()

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        c.execute(
            "SELECT password FROM users WHERE id=?",
            (session["user_id"],)
        )

        current_password = c.fetchone()[0]

        if check_password_hash(current_password, old_password):

            new_hash = generate_password_hash(new_password)

            c.execute(
                "UPDATE users SET password=? WHERE id=?",
                (new_hash, session["user_id"])
            )

            conn.commit()
            conn.close()

            return redirect(url_for("profile"))

        else:
            flash("Incorrect old password")

    conn.close()

    return render_template("change_password.html")

# ==============================
# CHAT PAGE
# ==============================
@app.route("/chat")
def chat():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("chat.html")

# ==============================
# AI CHATBOT
# ==============================
@app.route("/chatbot", methods=["POST"])
def chatbot():

    if "user_id" not in session:
        return jsonify({"reply":"Please login first"})

    data = request.get_json()
    message = data["message"]

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role":"system","content":"You are a diabetes health assistant."},
            {"role":"user","content":message}
        ]
    )

    reply = completion.choices[0].message.content

    return jsonify({"reply":reply})

#===============================






@app.route("/generate_diet", methods=["POST"])
def generate_diet():

    preference = request.form["diet"]

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"system",
                "content":"You are a certified diabetes nutrition specialist."
            },
            {
                "role":"user",
                "content":f"""
Create a 1-day diabetes friendly diet plan for a person following: {preference} diet.

Structure the response like this:

Breakfast:
Lunch:
Dinner:
Snacks:
Foods to Avoid:
Daily Tips:

Keep it simple and medically safe.
"""
            }
        ]
    )

    plan = completion.choices[0].message.content

    return jsonify({"diet":plan})

@app.route("/health_score")
def health_score():
    return render_template("health_score.html", score=None)

@app.route("/calculate_health_score", methods=["POST"])
def calculate_health_score():

    age = int(request.form["age"])
    weight = int(request.form["weight"])
    sleep = int(request.form["sleep"])
    activity = request.form["activity"]

    score = 100

    if sleep < 6:
        score -= 20

    if weight > 90:
        score -= 10

    if activity == "Sedentary":
        score -= 15

    return render_template("health_score.html", score=score)


@app.route("/sugar_tracker")
def sugar_tracker():
    return render_template("sugar_tracker.html")

@app.route("/glucose_advice", methods=["POST"])
def glucose_advice():

    data=request.get_json()

    sugar=data["sugar"]

    completion=groq_client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {"role":"system","content":"You are a diabetes specialist."},

            {"role":"user","content":f"My blood sugar level is {sugar} mg/dL. Give health advice."}

        ]

    )

    advice=completion.choices[0].message.content

    return jsonify({"advice":advice})

@app.route("/ai_diet")
def ai_diet():
    return render_template("ai_diet.html")


@app.route("/nearby_services")
def nearby_services():
    return render_template("nearby_services.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("diabetes.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id=?", (session["user_id"],))
    prediction_count = c.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        result=session.get("last_result"),
        risk_score=session.get("last_risk"),
        prediction_count=prediction_count
    )

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/featureslogin")
def featureslogin():
    print("FEATURES LOGIN LOADED")
    return render_template("featureslogin.html")

#===============================
# ==============================
## ==============================
# SUGAR TRACKER LOGIN (ADD THIS)
# ==============================
@app.route("/sugar_trackerlogin")
def sugar_trackerlogin():
    print("SUGAR TRACKER LOGIN LOADED ✅")
    return render_template("sugar_trackerlogin.html")


#================================
@app.route("/nearby_serviceslogin")
def nearby_serviceslogin():
    print("NEARBY SERVICES LOGIN LOADED")
    return render_template("nearby_serviceslogin.html")

#================================

@app.route("/ai_dietlogin")
def ai_dietlogin():
    print("AI DIET LOGIN LOADED")
    return render_template("ai_dietlogin.html")

#====================================
@app.route("/health_scorelogin")
def health_scorelogin():
    print("HEALTH SCORE LOGIN LOADED")
    return render_template("health_scorelogin.html")
# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)