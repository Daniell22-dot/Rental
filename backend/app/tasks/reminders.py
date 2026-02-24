from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.payment import Payment
from app.models.notification import Notification
import logging

logger = logging.getLogger(__name__)

async def send_rent_reminders():
    async with AsyncSessionLocal() as db:
        try:
            # Find tenants with overdue payments
            result = await db.execute(
                select(Tenant)
                .join(Payment)
                .filter(Payment.status == 'overdue')
                .distinct()
            )
            overdue_tenants = result.scalars().unique().all()

            for tenant in overdue_tenants:
                new_notif = Notification(
                    user_id=tenant.user_id,
                    title="Rent Payment Reminder",
                    message=f"Hello {tenant.first_name}, you have an outstanding rent balance. Please clear it to avoid penalties.",
                    type="payment_reminder" # Changed category/type to match model if needed, but 'type' was in monitoring, let's check notification.py
                )
                db.add(new_notif)
                logger.info(f"Rental reminder sent to tenant {tenant.id}")
            
            await db.commit()
        except Exception as e:
            logger.error(f"Error in rent reminders: {e}")
            await db.rollback()
