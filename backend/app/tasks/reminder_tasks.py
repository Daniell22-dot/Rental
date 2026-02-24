# backend/app/tasks/reminder_tasks.py
from celery import Celery
from datetime import datetime, timedelta
from app.services.notification_service import NotificationService
from app.core.email import send_email

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def send_monthly_reminders():
    """Send payment reminders to all tenants"""
    notification_service = NotificationService()
    
    # Get all active tenants with upcoming payments
    tenants = get_active_tenants_with_upcoming_payments()
    
    for tenant in tenants:
        send_email(
            to=tenant.email,
            subject=f"Rent Payment Reminder - Due in {tenant.days_until_due} days",
            template="payment_reminder.html",
            context={
                'tenant_name': tenant.name,
                'amount': tenant.monthly_rent,
                'due_date': tenant.next_payment_date,
                'payment_link': generate_payment_link(tenant)
            }
        )

@celery.task
def check_overdue_payments():
    """Daily check for overdue payments and apply late fees"""
    # Implementation for checking and handling overdue payments
    pass