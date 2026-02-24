from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.payment import Payment
from app.models.lease import Lease
from app.models.tenant import Tenant
from app.core.email import send_payment_reminder, send_payment_receipt

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_payment(self, payment_in):
        new_payment = Payment(
            amount=payment_in.amount,
            tenant_id=payment_in.tenant_id,
            lease_id=payment_in.lease_id,
            payment_date=payment_in.payment_date,
            payment_method=payment_in.payment_method,
            status="completed"
        )
        self.db.add(new_payment)
        await self.db.commit()
        await self.db.refresh(new_payment)
        return new_payment

    async def get_tenant_payment_history(self, tenant_id: int):
        result = await self.db.execute(select(Payment).filter(Payment.tenant_id == tenant_id))
        return result.scalars().all()

    async def get_overdue_payments(self):
        result = await self.db.execute(select(Payment).filter(Payment.status.in_(['overdue', 'failed'])))
        return result.scalars().all()

    async def send_payment_receipt(self, payment_id: int):
        result = await self.db.execute(select(Payment).filter(Payment.id == payment_id))
        payment = result.scalars().first()
        if payment:
            # Need to join with tenant potentially
            result = await self.db.execute(select(Tenant).filter(Tenant.id == payment.tenant_id))
            tenant = result.scalars().first()
            if tenant:
                await send_payment_receipt(tenant.email, payment)

    async def track_monthly_payments(self):
        """Automatically track and update payment status"""
        result = await self.db.execute(select(Lease).filter(Lease.status == 'active'))
        active_leases = result.scalars().all()
        
        for lease in active_leases:
            # Placeholder for logic
            pass
    
    async def send_automatic_reminders(self):
        """Send payment reminders before due date"""
        result = await self.db.execute(
            select(Lease).filter(Lease.next_payment_date <= datetime.now() + timedelta(days=3))
        )
        upcoming_due_dates = result.scalars().all()
        
        for lease in upcoming_due_dates:
            result = await self.db.execute(select(Tenant).filter(Tenant.id == lease.tenant_id))
            tenant = result.scalars().first()
            if tenant:
                await send_payment_reminder(tenant.email, lease)