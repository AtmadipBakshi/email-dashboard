from flask import Flask, render_template, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

app = Flask(__name__)
CORS(app)  # IMPORTANT for Vercel frontend

# ---------- Gmail API ----------
def get_gmail_service():
    try:
        creds = Credentials.from_authorized_user_file('token.json')
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print("Auth Error:", e)
        return None


def clean_subject(subject):
    return subject if subject else "(No Subject)"


def get_emails():
    service = get_gmail_service()

    # 🔥 Fallback if Gmail fails (IMPORTANT FOR DEPLOY)
    if service is None:
        return [
            {"subject": "Demo Email 1", "sender": "test@gmail.com", "date": "Today"},
            {"subject": "Demo Email 2", "sender": "noreply@google.com", "date": "Yesterday"}
        ]

    results = service.users().messages().list(
        userId='me',
        maxResults=10
    ).execute()

    messages = results.get('messages', [])
    email_list = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id']
        ).execute()

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])

        subject = ""
        sender = ""
        date = ""

        for h in headers:
            name = h['name'].lower()
            if name == "subject":
                subject = h['value']
            elif name == "from":
                sender = h['value']
            elif name == "date":
                date = h['value']

        email_list.append({
            "subject": clean_subject(subject),
            "sender": sender,
            "date": date
        })

    return email_list


# ---------- Routes ----------
@app.route("/")
def home():
    return "Backend is running 🚀"


@app.route("/emails")
def emails():
    try:
        data = get_emails()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})


# ---------- Run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))