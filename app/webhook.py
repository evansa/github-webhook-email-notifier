import hashlib
import hmac
import logging
import smtplib
from email.mime.text import MIMEText

from flask import Blueprint, current_app, jsonify, request

webhook_bp = Blueprint("webhook", __name__)
logging.basicConfig(level=logging.INFO)


@webhook_bp.route("/webhook", methods=["POST"])
def github_webhook():
    try:
        secret_token = current_app.config.get("SECRET_TOKEN")
        signature = request.headers.get("X-Hub-Signature-256")

        if not secret_token:
            logging.error("Missing SECRET_TOKEN in configuration")
            return jsonify({"error": "Server misconfiguration"}), 500

        if not verify_signature(secret_token, request.data, signature):
            logging.warning("Unauthorized webhook request received")
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json
        if not data or "text" not in data:
            logging.warning("Invalid payload received: %s", data)
            return jsonify({"error": "Invalid payload"}), 400

        send_email("GitHub Action Failure", data["text"])
        return jsonify({"message": "Notification sent"}), 200
    except Exception as e:
        logging.error("Unexpected error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


def verify_signature(secret, payload, signature) -> bool:
    try:
        if not signature:
            return False
        mac = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={mac}", signature)
    except Exception as e:
        logging.error("Error verifying signature: %s", str(e))
        return False


def send_email(subject, body) -> None:
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = current_app.config.get("EMAIL_FROM")
        msg["To"] = current_app.config.get("EMAIL_TO")

        if not msg["From"] or not msg["To"]:
            logging.error("Email configuration is missing required fields")
            return

        with smtplib.SMTP(
            current_app.config["SMTP_SERVER"], current_app.config["SMTP_PORT"]
        ) as server:
            server.starttls()
            server.login(
                current_app.config["SMTP_USERNAME"], current_app.config["SMTP_PASSWORD"]
            )
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        logging.info("Email sent successfully")
    except smtplib.SMTPException as e:
        logging.error("SMTP error: %s", str(e))
    except Exception as e:
        logging.error("Error sending email: %s", str(e))
