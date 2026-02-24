import logging
from typing import Any
from app.config import settings

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, body: str):
    """
    Mock email sending logic. In a real app, use fast-mail or smtplib.
    """
    logger.info(f"Sending email to {to_email} with subject: {subject}")
    # SMTP logic would go here using settings.SMTP_SERVER, etc.
    print(f"EMAIL SENT TO {to_email}: {subject}")

async def send_payment_reminder(to_email: str, lease: Any):
    subject = f"Payment Reminder for {lease.unit.unit_number}"
    body = f"Hello, your payment for unit {lease.unit.unit_number} is due soon."
    await send_email(to_email, subject, body)

async def send_payment_receipt(to_email: str, payment: Any):
    subject = f"Payment Receipt: {payment.amount}"
    body = f"Thank you for your payment of {payment.amount}."
    await send_email(to_email, subject, body)
