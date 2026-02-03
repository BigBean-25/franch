from models import NotificationLog
from datetime import datetime, timezone
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests

logger = logging.getLogger(__name__)

# Email Configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@bigbeancafe.in")

# WhatsApp Configuration
WHATSAPP_API_URL = os.environ.get("WHATSAPP_API_URL", "")
WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_KEY", "")

async def send_email_notification(db, recipient: str, subject: str, message: str):
    """
    Send email notification using SMTP
    """
    notification = NotificationLog(
        type="email",
        recipient=recipient,
        subject=subject,
        message=message,
        status="pending"
    )
    
    try:
        # Check if SMTP is configured
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("SMTP not configured. Email logged but not sent.")
            notification.status = "pending"
            notification.error_message = "SMTP credentials not configured"
        else:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = recipient
            msg['Subject'] = subject
            
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <img src="https://customer-assets.emergentagent.com/job_bigbean-system/artifacts/cg0dat1r_BBC-Logo.png" alt="BigBeanCafe" style="width: 80px; height: 80px;">
                            <h2 style="color: #6F4E37; margin-top: 10px;">BigBeanCafe</h2>
                        </div>
                        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px;">
                            {message}
                        </div>
                        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                            <p>This is an automated message from BigBeanCafe Franchise Ordering System</p>
                            <p>&copy; 2025 BigBeanCafe. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            notification.status = "sent"
            notification.sent_at = datetime.now(timezone.utc)
            logger.info(f"Email sent to {recipient}: {subject}")
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
    Send WhatsApp notification using WhatsApp Business API
    """
    notification = NotificationLog(
        type="whatsapp",
        recipient=recipient,
        message=message,
        status="pending"
    )
    
    try:
        # Check if WhatsApp API is configured
        if not WHATSAPP_API_URL or not WHATSAPP_API_KEY:
            logger.warning("WhatsApp API not configured. Message logged but not sent.")
            notification.status = "pending"
            notification.error_message = "WhatsApp API not configured"
        else:
            # Send WhatsApp message
            payload = {
                "phone": recipient,
                "message": f"🏪 *BigBeanCafe*\n\n{message}\n\n_This is an automated message from BigBeanCafe Franchise Ordering System_"
            }
            
            headers = {
                "Authorization": f"Bearer {WHATSAPP_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                notification.status = "sent"
                notification.sent_at = datetime.now(timezone.utc)
                logger.info(f"WhatsApp sent to {recipient}")
            else:
                raise Exception(f"WhatsApp API returned status {response.status_code}")
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

async def notify_order_placed(db, order_data: dict, franchise_email: str, franchise_phone: str = None):
    """
    Send notifications when order is placed
    """
    subject = f"Order Placed - {order_data['order_number']}"
    message = f"""
    <h3 style="color: #6F4E37;">Order Placed Successfully!</h3>
    <p>Dear Customer,</p>
    <p>Your order <strong>{order_data['order_number']}</strong> has been placed successfully.</p>
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Order Number:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{order_data['order_number']}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Amount:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">₹{order_data['grand_total']:.2f}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Status:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;"><span style="background-color: #FEF3C7; color: #92400E; padding: 5px 10px; border-radius: 5px;">Pending Approval</span></td>
        </tr>
    </table>
    <p>Your order is pending approval. You will be notified once it's approved.</p>
    <p>Thank you for choosing BigBeanCafe!</p>
    """
    
    await send_email_notification(db, franchise_email, subject, message)
    
    if franchise_phone:
        whatsapp_msg = f"Order Placed!\n\nOrder: {order_data['order_number']}\nAmount: ₹{order_data['grand_total']:.2f}\nStatus: Pending Approval\n\nYou will be notified once approved."
        await send_whatsapp_notification(db, franchise_phone, whatsapp_msg)

async def notify_order_approved(db, order_data: dict, franchise_email: str, franchise_phone: str = None):
    """
    Send notifications when order is approved
    """
    subject = f"Order Approved - {order_data['order_number']}"
    message = f"""
    <h3 style="color: #059669;">Order Approved!</h3>
    <p>Dear Customer,</p>
    <p>Great news! Your order <strong>{order_data['order_number']}</strong> has been approved.</p>
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Order Number:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{order_data['order_number']}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Amount:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">₹{order_data['grand_total']:.2f}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Invoice Number:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{order_data.get('invoice_number', 'Generating...')}</td>
        </tr>
    </table>
    <p>Your invoice has been generated and is available for download from your dashboard.</p>
    <p>Thank you for your business!</p>
    """
    
    await send_email_notification(db, franchise_email, subject, message)
    
    if franchise_phone:
        whatsapp_msg = f"✅ Order Approved!\n\nOrder: {order_data['order_number']}\nAmount: ₹{order_data['grand_total']:.2f}\nInvoice: {order_data.get('invoice_number', 'Generating')}\n\nDownload invoice from your dashboard."
        await send_whatsapp_notification(db, franchise_phone, whatsapp_msg)

async def notify_order_rejected(db, order_data: dict, franchise_email: str, reason: str = "", franchise_phone: str = None):
    """
    Send notifications when order is rejected
    """
    subject = f"Order Rejected - {order_data['order_number']}"
    message = f"""
    <h3 style="color: #DC2626;">Order Rejected</h3>
    <p>Dear Customer,</p>
    <p>We regret to inform you that your order <strong>{order_data['order_number']}</strong> has been rejected.</p>
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Order Number:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{order_data['order_number']}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Reason:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{reason if reason else 'Not specified'}</td>
        </tr>
    </table>
    <p>Please contact support if you have any questions.</p>
    """
    
    await send_email_notification(db, franchise_email, subject, message)
    
    if franchise_phone:
        whatsapp_msg = f"❌ Order Rejected\n\nOrder: {order_data['order_number']}\nReason: {reason if reason else 'Not specified'}\n\nContact support for more details."
        await send_whatsapp_notification(db, franchise_phone, whatsapp_msg)

async def notify_credit_exhausted(db, franchise_name: str, franchise_email: str, franchise_phone: str = None):
    """
    Send notifications when credit is exhausted
    """
    subject = "Credit Limit Exhausted"
    message = f"""
    <h3 style="color: #DC2626;">Credit Limit Exhausted</h3>
    <p>Dear {franchise_name},</p>
    <p>Your credit limit has been exhausted.</p>
    <div style="background-color: #FEE2E2; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p style="margin: 0; color: #991B1B;"><strong>⚠️ Action Required</strong></p>
        <p style="margin: 10px 0 0 0;">Please make a payment of ₹1,00,000 to reset your credit and continue ordering.</p>
    </div>
    <p>You can make the payment from the "Pay Outstanding" section in your dashboard.</p>
    """
    
    await send_email_notification(db, franchise_email, subject, message)
    
    if franchise_phone:
        whatsapp_msg = "⚠️ Credit Exhausted!\n\nYour credit limit is exhausted. Please pay ₹1,00,000 to continue ordering.\n\nPay from: Dashboard > Pay Outstanding"
        await send_whatsapp_notification(db, franchise_phone, whatsapp_msg)

async def notify_payment_success(db, payment_data: dict, franchise_email: str, franchise_phone: str = None):
    """
    Send notifications when payment is successful
    """
    subject = "Payment Successful - Credit Reset"
    message = f"""
    <h3 style="color: #059669;">Payment Successful!</h3>
    <p>Dear Customer,</p>
    <p>Your payment has been processed successfully.</p>
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Amount Paid:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">₹{payment_data['amount']:.2f}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Payment ID:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{payment_data.get('razorpay_payment_id', 'N/A')}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Credit Status:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;"><span style="background-color: #D1FAE5; color: #065F46; padding: 5px 10px; border-radius: 5px;">Reset to ₹1,00,000</span></td>
        </tr>
    </table>
    <p>Your credit has been reset and you can now continue placing orders.</p>
    <p>Thank you for your payment!</p>
    """
    
    await send_email_notification(db, franchise_email, subject, message)
    
    if franchise_phone:
        whatsapp_msg = f"✅ Payment Successful!\n\nAmount: ₹{payment_data['amount']:.2f}\nPayment ID: {payment_data.get('razorpay_payment_id', 'N/A')}\n\nCredit Reset: ₹1,00,000\n\nYou can now place orders!"
        await send_whatsapp_notification(db, franchise_phone, whatsapp_msg)
