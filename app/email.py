import resend
from app.config import logger, RESEND_API_KEY, NOTIFICATION_EMAIL

resend.api_key = RESEND_API_KEY

async def send_lead_notification(phone_number: str, message: str):
    try:
        params = {
            "from": "WhatsApp Bot <onboarding@resend.dev>",
            "to": [NOTIFICATION_EMAIL],
            "subject": f"New WhatsApp Lead: {phone_number}",
            "html": f"<h2>New Lead</h2><p>Phone: {phone_number}</p><p>Message: {message}</p>"
        }
        await resend.Emails.send_async(params)
        logger.info(f"Email sent for {phone_number}")
    except Exception as e:
        logger.error(f"Email failed: {e}")