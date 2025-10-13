# scheduler.py
import os
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()
IST = pytz.timezone("Asia/Kolkata")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
TO_EMAIL = "sanskarsharmamusic999@gmail.com"
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

# ----------------- Timetable -----------------
timetable = {
    "Monday": [("09:30", "Design Thinking – Nawang Lama"), ("10:37", "⚡ Test Class – Scheduler Check")],
    # Add other days similarly
}

# ----------------- Email function -----------------
def send_email(subject, body):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
    data = {"sender": {"name": "Sanskar's Alert Agent", "email": SENDER_EMAIL},
            "to": [{"email": TO_EMAIL}],
            "subject": subject,
            "htmlContent": f"<p>{body}</p>"}
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"📧 Sending to {TO_EMAIL} | Status: {response.status_code}")
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print("❌ Email send failed:", e)
        return False

# ----------------- Class checker -----------------
def check_class():
    today = datetime.now(IST).strftime("%A")
    now = datetime.now(IST)
    if today not in timetable:
        return
    today_classes = timetable[today]
    for i, (time_slot, subject) in enumerate(today_classes):
        class_time = datetime.strptime(time_slot, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        class_time = IST.localize(class_time)
        if abs((now - class_time).total_seconds()) <= 60:
            next_class = today_classes[i + 1][1] if i + 1 < len(today_classes) else "No more classes today!"
            body = f"📚 Current class: {subject}<br>⏭️ Next class: {next_class}"
            send_email("Class Alert 📅", body)
            print(f"✅ Class alert sent for {subject} at {time_slot}")
            return
    print(f"🕒 Checked at {now.strftime('%H:%M:%S')} — no matching class time.")

# ----------------- Run -----------------
if __name__ == "__main__":
    check_class()
