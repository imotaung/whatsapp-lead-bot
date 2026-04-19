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