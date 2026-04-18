from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
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
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    Body: str = Form(None),
    From: str = Form(None),
    To: str = Form(None)
):
    if not Body or not From:
        raise HTTPException(status_code=400, detail="Missing parameters")
    
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    if signature:
        form_data = await request.form()
        if not validator.validate(str(request.url), form_data, signature):
            raise HTTPException(status_code=403, detail="Unauthorized")
    
    phone = From
    msg = Body.strip()
    logger.info(f"Message from {phone}: {msg}")
    
    if not rate_limiter.is_allowed(phone):
        resp = MessagingResponse()
        resp.message("Rate limit exceeded. Try later.")
        return PlainTextResponse(str(resp), media_type="application/xml")
    
    try:
        sheets_client.append_lead(phone, msg, "new")
    except Exception as e:
        logger.error(f"Sheets error: {e}")
    
    background_tasks.add_task(send_lead_notification, phone, msg)
    
    resp = MessagingResponse()
    resp.message(f"Thank you! We'll get back to you within 24 hours. Book here: {CALENDLY_BOOKING_URL}")
    return PlainTextResponse(str(resp), media_type="application/xml")

@app.get("/webhook")
async def webhook_get():
    return {"error": "POST only"}