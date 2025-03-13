import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_TOKEN = os.getenv("GITHUB_SECRET_TOKEN")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_TO = os.getenv("EMAIL_TO")
    EMAIL_FROM = os.getenv("EMAIL_FROM")

    PORT = int(os.getenv("PORT", 5000))