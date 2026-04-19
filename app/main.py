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
):
    # 1. Extract the form data from the request
    form_data = await request.form()
    
    # 2. Get the specific parameters sent by Twilio
    message_body = form_data.get('Body')
    sender_phone = form_data.get('From')
    twilio_number = form_data.get('To')

    # 3. Validate that we received the required information
    if not message_body or not sender_phone:
        logger.warning(f"Missing data in webhook: Body={message_body}, From={sender_phone}")
        raise HTTPException(status_code=400, detail="Missing parameters")
    
    # 4. (Your existing logic for saving to Sheets, rate limiting, etc. goes here)
    # ... rest of your existing code ...