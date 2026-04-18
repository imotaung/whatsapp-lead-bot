import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.config import logger, GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_CREDENTIALS_JSON, GOOGLE_SHEET_ID

class GoogleSheetsClient:
    def __init__(self):
        self.client = self._authenticate()
        self.sheet = self.client.open_by_key(GOOGLE_SHEET_ID).sheet1
        self._ensure_headers()
    
    def _authenticate(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if GOOGLE_CREDENTIALS_JSON:
            creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS_PATH, scope)
        return gspread.authorize(creds)
    
    def _ensure_headers(self):
        if not self.sheet.get_all_values():
            self.sheet.append_row(["Timestamp", "Phone Number", "Message", "Status"])
            logger.info("Added headers")
    
    def append_lead(self, phone_number, message, status="new"):
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()
        self.sheet.append_row([timestamp, phone_number, message, status])
        logger.info(f"Saved lead {phone_number}")

sheets_client = GoogleSheetsClient()