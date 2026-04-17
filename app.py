from flask import Flask, render_template, jsonify
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import re

app = Flask(__name__)

# ---------- Gmail API ----------
def get_gmail_service():
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('gmail', 'v1', credentials=creds)
    return service


def clean_subject(subject):
    return subject if subject else "(No Subject)"


def get_emails():
    service = get_gmail_service()

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
            if name == "from":
                sender = h['value']
            if name == "date":
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
    return render_template("index.html")


@app.route("/emails")
def emails():
    try:
        data = get_emails()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)