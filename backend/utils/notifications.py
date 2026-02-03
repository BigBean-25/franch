from models import NotificationLog
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def send_email_notification(db, recipient: str, subject: str, message: str):
    """
    Send email notification and log it
    """
    notification = NotificationLog(
        type="email",
        recipient=recipient,
        subject=subject,
        message=message,
        status="pending"
    )
    
    try:
        # TODO: Implement actual email sending logic (SMTP, SendGrid, etc.)
        # For now, we'll just log it
        logger.info(f"Email sent to {recipient}: {subject}")
        
        notification.status = "sent"
        notification.sent_at = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        notification.status = "failed"
        notification.error_message = str(e)
    
    # Save notification log
    doc = notification.model_dump()
    if notification.sent_at:
        doc['sent_at'] = doc['sent_at'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.notification_logs.insert_one(doc)
    return notification

async def send_whatsapp_notification(db, recipient: str, message: str):
    """
    Send WhatsApp notification and log it
    """
    notification = NotificationLog(
        type="whatsapp",
        recipient=recipient,
        message=message,
        status="pending"
    )
    
    try:
        # TODO: Implement actual WhatsApp sending logic (WhatsApp Business API)
        # For now, we'll just log it
        logger.info(f"WhatsApp sent to {recipient}: {message}")
        
        notification.status = "sent"
        notification.sent_at = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {recipient}: {str(e)}")
        notification.status = "failed"
        notification.error_message = str(e)
    
    # Save notification log
    doc = notification.model_dump()
    if notification.sent_at:
        doc['sent_at'] = doc['sent_at'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.notification_logs.insert_one(doc)
    return notification

async def notify_order_placed(db, order_data: dict, franchise_email: str):
    """
    Send notifications when order is placed
    """
    subject = f"Order Placed - {order_data['order_number']}"
    message = f"Your order {order_data['order_number']} for ₹{order_data['grand_total']:.2f} has been placed successfully and is pending approval."
    
    await send_email_notification(db, franchise_email, subject, message)

async def notify_order_approved(db, order_data: dict, franchise_email: str):
    """
    Send notifications when order is approved
    """
    subject = f"Order Approved - {order_data['order_number']}"
    message = f"Your order {order_data['order_number']} has been approved. Invoice: {order_data.get('invoice_number', 'Generating...')}"
    
    await send_email_notification(db, franchise_email, subject, message)

async def notify_order_rejected(db, order_data: dict, franchise_email: str, reason: str = ""):
    """
    Send notifications when order is rejected
    """
    subject = f"Order Rejected - {order_data['order_number']}"
    message = f"Your order {order_data['order_number']} has been rejected. Reason: {reason}"
    
    await send_email_notification(db, franchise_email, subject, message)

async def notify_credit_exhausted(db, franchise_name: str, franchise_email: str):
    """
    Send notifications when credit is exhausted
    """
    subject = "Credit Limit Exhausted"
    message = f"Your credit limit has been exhausted. Please make a payment to continue ordering."
    
    await send_email_notification(db, franchise_email, subject, message)

async def notify_payment_success(db, payment_data: dict, franchise_email: str):
    """
    Send notifications when payment is successful
    """
    subject = "Payment Successful"
    message = f"Your payment of ₹{payment_data['amount']:.2f} has been processed successfully. Your credit has been reset."
    
    await send_email_notification(db, franchise_email, subject, message)
