import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import schedule
import time
from datetime import datetime
from flask import Flask
import threading

# -----------------------------
# 🔹 Load environment variables
# -----------------------------
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = "sanskarsharmamusic999@gmail.com"

if not EMAIL or not PASSWORD:
    raise ValueError("Please set EMAIL and PASSWORD in your .env file")

# -----------------------------
# 🔹 Flask app
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "📬 Class Alert Agent is running!"

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
    ]# Add other days here...
}

# -----------------------------
# 🔹 Email function
# -----------------------------
def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['From'] = EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

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
    # Start scheduler in a separate thread
    threading.Thread(target=run_schedule, daemon=True).start()
    
    # Start Flask server
    app.run(debug=True)
