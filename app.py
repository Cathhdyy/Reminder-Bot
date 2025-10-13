# app.py
import os
import requests
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
TO_EMAIL = "sanskarsharmamusic999@gmail.com"
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

app = Flask(__name__)

@app.route("/")
def home():
    return "📬 Class Alert Agent (Brevo) is running!"

@app.route("/testmail")
def testmail():
    from scheduler import send_email
    success = send_email("Render Test", "If you see this, your Brevo mail works!")
    return "✅ Email sent! Check inbox/spam." if success else "❌ Email failed."
