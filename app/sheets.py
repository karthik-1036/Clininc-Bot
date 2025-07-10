import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
load_dotenv()


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))

def save_appointment(name, date, time, phone):
    worksheet = sheet.worksheet("appointments")
    worksheet.append_row([name, date, time, phone])

def save_feedback(phone, message, summary):
    worksheet = sheet.worksheet("feedback")
    worksheet.append_row([phone, message, summary.get("summary", ""), summary.get("sentiment", "")])
