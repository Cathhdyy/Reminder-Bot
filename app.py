import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import schedule
import time
from datetime import datetime
from flask import Flask
import threading
import sys
import logging

# -----------------------------
# 🔹 Load environment variables
# -----------------------------
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = "sanskarsharmamusic999@gmail.com"

if not EMAIL or not PASSWORD:
    raise ValueError("Please set EMAIL and PASSWORD in your Render environment")

# -----------------------------
# 🔹 Flask app
# -----------------------------
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

@app.route("/")
def home():
    return "📬 Class Alert Agent is running!"

@app.route("/testmail")
def testmail():
    success = send_email("Render Test", "If you see this, your Render mail works!")
    if success:
        return "✅ Email sent! Check inbox/spam."
    else:
        return "❌ Email failed. Check Render logs."


# -----------------------------
# 🔹 Timetable
# -----------------------------
timetable = {
    "Monday": [
        ("09:30", "Design Thinking – Nawang Lama"),
        ("10:20", "Design Thinking – Nawang Lama"),
        ("12:50", "Mathematics - I – Nabin Dahal"),
        ("13:40", "Mathematics - I – Nabin Dahal"),
        ("14:30", "Programming for Problem Solving – Nawang Lama"),
        ("15:20", "Programming for Problem Solving – Nawang Lama")
    ],
    "Tuesday": [
        ("09:30", "Programming for Problem Solving – Nawang Lama"),
        ("10:20", "Programming for Problem Solving – Nawang Lama"),
        ("12:50", "English and Communication – Dechen Chopel Lepcha"),
        ("13:40", "English and Communication – Dechen Chopel Lepcha"),
        ("14:30", "Programming for Problem Solving – Nawang Lama"),
        ("15:20", "Programming for Problem Solving – Nawang Lama")
    ],
    "Wednesday": [
        ("09:30", "Modern Computer Architecture – Rojesh Pradhan"),
        ("10:20", "English and Communication – Dechen Chopel Lepcha"),
        ("11:10", "English and Communication – Dechen Chopel Lepcha"),
        ("12:50", "Physics – Vivek Srivastav"),
        ("13:40", "Physics – Vivek Srivastav"),
        ("14:30", "Physics – Vivek Srivastav"),
        ("15:20", "Physics – Vivek Srivastav")
    ],
    "Thursday": [
        ("09:30", "Modern Computer Architecture – Rojesh Pradhan"),
        ("09:55", "Modern Computer Architecture – Rojesh Pradhan"),
        ("11:10", "Physics – Vivek Srivastav"),
        ("12:50", "Personal Effectiveness – Mr. Swapan K. Mullick"),
        ("13:40", "Personal Effectiveness – Mr. Swapan K. Mullick"),
        ("14:30", "Club Activity – Unassigned"),
        ("15:20", "Club Activity – Unassigned")
    ],
    "Friday": [
        ("09:30", "Modern Computer Architecture – Rojesh Pradhan"),
        ("10:20", "Mathematics - I – Nabin Dahal"),
        ("11:10", "Mathematics - I – Nabin Dahal"),
        ("12:50", "Physics – Vivek Srivastav"),
        ("14:30", "Club Activity – Unassigned"),
        ("15:20", "Club Activity – Unassigned")
    ],
    "Saturday": [
        ("09:30", "Club Activity – Unassigned"),
        ("10:20", "Club Activity – Unassigned"),
        ("11:10", "Club Activity – Unassigned"),
        ("12:50", "Club Activity – Unassigned"),
        ("13:40", "Club Activity – Unassigned"),
        ("14:30", "Club Activity – Unassigned"),
        ("15:20", "Club Activity – Unassigned")
    ]
}

# -----------------------------
# 🔹 Email function
# -----------------------------
def send_email(subject, body):
    try:
        print(f"📨 Trying to send email from {EMAIL} to {TO_EMAIL}...")
        msg = MIMEText(body)
        msg['From'] = EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("🔹 Connecting to Gmail SMTP...")
            server.starttls()
            print("🔹 Logging in...")
            server.login(EMAIL, PASSWORD)
            print("🔹 Sending email...")
            server.send_message(msg)

        print(f"✅ Email sent: {subject}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# -----------------------------
# 🔹 Class checker
# -----------------------------
def check_class():
    today = datetime.now().strftime("%A")
    now = datetime.now().strftime("%H:%M")

    if today not in timetable:
        return

    today_classes = timetable[today]
    for i, (time_slot, subject) in enumerate(today_classes):
        if now == time_slot:
            next_class = today_classes[i + 1][1] if i + 1 < len(today_classes) else "No more classes today!"
            body = f"📚 Current class: {subject}\n⏭️ Next class: {next_class}"
            send_email("Class Alert 📅", body)

# -----------------------------
# 🔹 Schedule in background
# -----------------------------
def run_schedule():
    schedule.every(1).minutes.do(check_class)
    while True:
        schedule.run_pending()
        time.sleep(60)

# -----------------------------
# 🔹 Run Flask and schedule together
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=run_schedule, daemon=True).start()  # 🧠 Background thread
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
