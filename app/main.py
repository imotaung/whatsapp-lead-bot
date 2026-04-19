from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from app.config import logger, TWILIO_AUTH_TOKEN, CALENDLY_BOOKING_URL
from app.sheets import sheets_client
from app.email import send_lead_notification
from app.rate_limit import rate_limiter

app = FastAPI(title="WhatsApp Lead Capture Bot")

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>WhatsApp Lead Bot</title><meta charset="UTF-8"></head>
    <body style="font-family: Arial; text-align:center; padding:50px">
        <h1>WhatsApp Lead Capture Bot</h1>
        <p>Automatically collect leads from WhatsApp messages</p>
        <div style="display:flex; justify-content:center; gap:20px; margin:40px">
            <div style="border:1px solid #ccc; padding:20px; width:250px">
                <h3>Starter</h3>
                <div>$29/mo</div>
                <p>500 leads/month</p>
                <a href="#" style="background:#25D366; color:white; padding:10px; text-decoration:none">Sign up</a>
            </div>
            <div style="border:1px solid #ccc; padding:20px; width:250px">
                <h3>Pro</h3>
                <div>$79/mo</div>
                <p>Unlimited leads</p>
                <a href="#" style="background:#25D366; color:white; padding:10px; text-decoration:none">Sign up</a>
            </div>
        </div>
        <p>Webhook ready: <code>/webhook</code></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    # Try to get data from form or JSON
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        message_body = data.get('Body')
        sender_phone = data.get('From')
        twilio_number = data.get('To')
    else:
        form_data = await request.form()
        message_body = form_data.get('Body')
        sender_phone = form_data.get('From')
        twilio_number = form_data.get('To')
    
    if not message_body or not sender_phone:
        logger.warning(f"Missing data in webhook: Body={message_body}, From={sender_phone}")
        raise HTTPException(status_code=400, detail="Missing parameters")
    
    # Rate limiting
    if not rate_limiter.is_allowed(sender_phone):
        resp = MessagingResponse()
        resp.message("Rate limit exceeded. Try later.")
        return PlainTextResponse(str(resp), media_type="application/xml")
    
    # Save to Google Sheets
    try:
        sheets_client.append_lead(sender_phone, message_body, "new")
    except Exception as e:
        logger.error(f"Sheets error: {e}")
    
    # Send email notification
    background_tasks.add_task(send_lead_notification, sender_phone, message_body)
    
    # Auto-reply
    resp = MessagingResponse()
    resp.message(f"Thank you! We'll get back to you within 24 hours. Book here: {CALENDLY_BOOKING_URL}")
    return PlainTextResponse(str(resp), media_type="application/xml")

@app.get("/webhook")
async def webhook_get():
    return {"error": "POST only"}