"""
Minimal feedback sender API.

Run locally for testing (requires Flask):

pip install Flask
python send_feedback.py

Environment variables (optional) to enable SMTP sending:
- SMTP_HOST
- SMTP_PORT (int)
- SMTP_USER
- SMTP_PASS
- FROM_EMAIL

If SMTP is not configured the endpoint will save the feedback JSON to disk under ./sent_feedbacks/ instead.
"""
from flask import Flask, request, jsonify
import os
import smtplib
from email.message import EmailMessage
import json
from datetime import datetime

app = Flask(__name__)


# Add simple CORS headers to allow browser fetches from a different origin (for local testing).
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USER)

SAVE_DIR = os.path.join(os.path.dirname(__file__), 'sent_feedbacks')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR, exist_ok=True)

@app.route('/api/send-feedback', methods=['POST'])
def send_feedback():
    data = request.get_json()
    if not data:
        return jsonify({'ok': False, 'message': 'No JSON body provided'}), 400

    email = data.get('email')
    feedback = data.get('feedback')
    interviewData = data.get('interviewData')

    if not email:
        return jsonify({'ok': False, 'message': 'Missing email field'}), 400

    payload = {
        'to': email,
        'feedback': feedback,
        'interviewData': interviewData,
        'sentAt': datetime.utcnow().isoformat() + 'Z'
    }

    # If SMTP config available, attempt to send
    if SMTP_HOST and SMTP_USER and SMTP_PASS and FROM_EMAIL:
        try:
            msg = EmailMessage()
            msg['Subject'] = 'Your Interview Feedback'
            msg['From'] = FROM_EMAIL
            msg['To'] = email
            body = 'Hello,\n\nAttached below is your interview feedback and transcript.\n\n' + feedback + '\n\n-- Interview Data (JSON) --\n' + json.dumps(interviewData, indent=2)
            msg.set_content(body)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)

            return jsonify({'ok': True, 'message': 'Feedback sent via SMTP'})
        except Exception as e:
            # fallback to save
            fname = os.path.join(SAVE_DIR, f'feedback_fallback_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.json')
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            return jsonify({'ok': False, 'message': 'SMTP failed, saved locally', 'error': str(e)}), 500

    # Otherwise save to disk
    fname = os.path.join(SAVE_DIR, f'feedback_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.json')
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

    return jsonify({'ok': True, 'message': f'Saved feedback to {fname}'})


@app.route('/api/send-feedback', methods=['OPTIONS'])
def send_feedback_options():
    # Reply to preflight CORS checks
    resp = jsonify({'ok': True})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    resp.headers['Access-Control-Allow-Methods'] = 'POST,OPTIONS'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
