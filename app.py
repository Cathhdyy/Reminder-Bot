import os
import requests
from flask import Flask
from dotenv import load_dotenv
import schedule
import threading
import time
from datetime import datetime, timedelta
import logging
import sys

# -----------------------------
# 🔹 Load environment variables
# -----------------------------
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # Your Brevo verified sender email
TO_EMAIL = "sanskarsharmamusic999@gmail.com"
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

if not BREVO_API_KEY:
    raise ValueError("Please set BREVO_API_KEY in your Render environment")

# -----------------------------
# 🔹 Flask app setup
# -----------------------------
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

@app.route("/")
def home():
    return "📬 Class Alert Agent (Brevo) is running!"

@app.route("/testmail")
def testmail():
    success = send_email("Render Test", "If you see this, your Brevo mail works!")
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
# 🔹 Email via Brevo API
# -----------------------------
def send_email(subject, body):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    data = {
        "sender": {"name": "Sanskar's Alert Agent", "email": SENDER_EMAIL},
        "to": [{"email": TO_EMAIL}],
        "subject": subject,
        "htmlContent": f"<p>{body}</p>",
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"📧 Sending to {TO_EMAIL} | Status: {response.status_code}")
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print("❌ Email send failed:", e)
        return False

# -----------------------------
# 🔹 Class checker (Improved)
# -----------------------------
def check_class():
    today = datetime.now().strftime("%A")
    now = datetime.now()

    if today not in timetable:
        return

    today_classes = timetable[today]
    for i, (time_slot, subject) in enumerate(today_classes):
        class_time = datetime.strptime(time_slot, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        # Allow a ±1 minute window to avoid timing misses
        if abs((now - class_time).total_seconds()) <= 60:
            next_class = today_classes[i + 1][1] if i + 1 < len(today_classes) else "No more classes today!"
            body = f"📚 Current class: {subject}<br>⏭️ Next class: {next_class}"
            send_email("Class Alert 📅", body)
            print(f"✅ Class alert sent for {subject} at {time_slot}")

# -----------------------------
# 🔹 Background scheduler
# -----------------------------
def run_schedule():
    schedule.every(1).minutes.do(check_class)
    print("⏰ Scheduler started. Checking for classes every minute...")
    while True:
        schedule.run_pending()
        time.sleep(60)
        print("🔁 Scheduler tick:", datetime.now().strftime("%H:%M:%S"))

# -----------------------------
# 🔹 Run Flask + Scheduler
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=run_schedule, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
