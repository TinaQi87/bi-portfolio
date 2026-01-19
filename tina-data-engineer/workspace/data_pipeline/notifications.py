"""
Notification Module - Alerts for Pipeline Events
Supports: Slack, Email, Console logging
"""
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import requests

from config import SLACK_WEBHOOK, EMAIL_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def send_slack(message: str, status: str = "info") -> bool:
    """Send notification to Slack channel."""
    if not SLACK_WEBHOOK:
        logger.warning("Slack webhook not configured")
        return False
    
    emoji = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    payload = {
        "text": f"{emoji.get(status, 'ℹ️')} *Pipeline Alert*\n{message}",
        "username": "Data Pipeline Bot"
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Slack notification failed: {e}")
        return False


def send_email(subject: str, body: str) -> bool:
    """Send email notification."""
    if not EMAIL_CONFIG["sender"] or not EMAIL_CONFIG["recipients"][0]:
        logger.warning("Email not configured")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender"]
        msg['To'] = ", ".join(EMAIL_CONFIG["recipients"])
        msg['Subject'] = f"[Data Pipeline] {subject}"
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Email notification failed: {e}")
        return False


def notify(message: str, status: str = "info", channels: list = None):
    """
    Send notification to multiple channels.
    
    Args:
        message: Notification message
        status: success, error, warning, info
        channels: List of channels ['slack', 'email', 'log']
    """
    channels = channels or ['log']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    
    if 'log' in channels:
        log_func = getattr(logger, 'error' if status == 'error' else 'info')
        log_func(message)
    
    if 'slack' in channels:
        send_slack(full_message, status)
    
    if 'email' in channels and status == 'error':
        send_email(f"Pipeline {status.upper()}", f"<p>{full_message}</p>")
