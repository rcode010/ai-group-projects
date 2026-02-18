"""
Email Agent

Sends email alert when RAM is high.
Gets called by Monitor Agent.

Uses environment variables for configuration (professional approach).
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============ EMAIL CONFIGURATION (from .env) ============
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')


def send_email_alert(ram_percent, top_processes):
    """
    Send email alert about high RAM

    Args:
        ram_percent: Current RAM percentage
        top_processes: List of top processes
    """

    # Validate configuration
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("✗ Error: Email credentials not found in .env file!")
        return

    # Create email message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"⚠️ HIGH RAM ALERT: {ram_percent}%"

    # Email body
    body = f"""
HIGH RAM USAGE DETECTED!

Current RAM Usage: {ram_percent}%

Top RAM-Consuming Processes:
"""

    for i, proc in enumerate(top_processes, 1):
        body += f"  {i}. {proc['name']}: {proc['memory']}%\n"

    body += """
Please check the system and close unnecessary programs.

---
This is an automated alert from RAM Monitor System
"""

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        print(f"📧 Sending email to {RECIPIENT_EMAIL}...")

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("✓ Email sent successfully!")

    except Exception as e:
        print(f"✗ Email failed: {e}")
