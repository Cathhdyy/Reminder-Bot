import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load email credentials from .env
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = "sanskarsharmamusic999@gmail.com" # You can change this if you want

def send_email(subject, body):
    msg = MIMEText(body)
    msg['From'] = EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
    print(f"✅ Email sent: {subject}")

# Sample test message
subject = "⏰ Test Class Alert"
body = "📚 Current class: Sample Class\n⏭️ Next class: Sample Next Class"

send_email(subject, body)
