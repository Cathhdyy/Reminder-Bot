import os
import requests
from flask import Flask
from dotenv import load_dotenv
import schedule
import threading
import time
from datetime import datetime
import logging
import sys
import pytz

# -----------------------------
# 🔹 Timezone
# -----------------------------
IST = pytz.timezone("Asia/Kolkata")

# -----------------------------
# 🔹 Load environment variables
# -----------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(".env file not found. Please create it in the project root.")

load_dotenv(dotenv_path)

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
TO_EMAIL = "sanskarsharmamusic999@gmail.com"

# Validate environment variables
if not SENDER_EMAIL or not BREVO_API_KEY:
    raise ValueError("SENDER_EMAIL or BREVO_API_KEY is missing in your .env file.")

print(f"✅ Loaded env: SENDER_EMAIL={SENDER_EMAIL}, BREVO_API_KEY={BREVO_API_KEY[:8]}…")

# -----------------------------
# 🔹 Flask app
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
    return "✅ Email sent!" if success else "❌ Email failed."

@app.route("/checknow")
def checknow():
    check_class()
    return "✅ Checked classes, see logs"

# -----------------------------
# 🔹 Timetable
# -----------------------------
timetable = {
    "Monday": [
        ("09:30", "Design Thinking – Nawang Lama"),
        ("10:37", "⚡ Test Class – Scheduler Check"),
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
    # Add other days similarly
}

# -----------------------------
# 🔹 Email function
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
        if response.status_code not in [200, 201, 202]:
            print("❌ Response:", response.text)
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print("❌ Email send failed:", e)
        return False

# -----------------------------
# 🔹 Class checker
# -----------------------------
def check_class():
    now = datetime.now(IST)
    today = now.strftime("%A")
    if today not in timetable:
        print(f"📅 No timetable for {today}")
        return

    today_classes = timetable[today]

    for i, (time_slot, subject) in enumerate(today_classes):
        class_time = datetime.strptime(time_slot, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        class_time = IST.localize(class_time)

        # ±2 minutes tolerance
        if abs((now - class_time).total_seconds()) <= 120:
            next_class = today_classes[i + 1][1] if i + 1 < len(today_classes) else "No more classes today!"
            body = f"📚 Current class: {subject}<br>⏭️ Next class: {next_class}"
            if send_email("Class Alert 📅", body):
                print(f"✅ Class alert sent for {subject} at {time_slot}")
            else:
                print(f"❌ Failed to send class alert for {subject} at {time_slot}")
            return

    print(f"🕒 Checked at {now.strftime('%H:%M:%S')} — no matching class time.")

# -----------------------------
# 🔹 Scheduler
# -----------------------------
def run_schedule():
    schedule.every(1).minutes.do(check_class)
    print("⏰ Scheduler started. Checking classes every minute...")
    while True:
        schedule.run_pending()
        time.sleep(60)
        print("🔁 Scheduler tick:", datetime.now(IST).strftime("%H:%M:%S"))

# -----------------------------
# 🔹 Run Flask + Scheduler
# -----------------------------
if __name__ == "__main__":
    # Run scheduler in a background thread
    threading.Thread(target=run_schedule, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
