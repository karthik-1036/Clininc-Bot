# main.py

from fastapi import FastAPI, Request
from app.whatsapp_handler import handle_message as handle_whatsapp
from app.telegram_handler import handle_telegram_message
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    return await handle_whatsapp(form)

@app.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != os.getenv("TELEGRAM_BOT_TOKEN"):
        return {"ok": False, "description": "Invalid token"}
    data = await request.json()
    return await handle_telegram_message(data)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000)
