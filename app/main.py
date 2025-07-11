# main.py

from fastapi import FastAPI, Request
from app.whatsapp_handler import handle_message as handle_whatsapp
from app.telegram_handler import telegram_router  # ✅ Removed broken import
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.include_router(telegram_router)


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    return await handle_whatsapp(form)


@app.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != os.getenv("TELEGRAM_BOT_TOKEN"):
        return {"ok": False, "description": "Invalid token"}
    data = await request.json()

    # ✅ Simple message parser to make the bot respond for now
    message = data.get("message", {}).get("text", "")
    chat_id = data.get("message", {}).get("chat", {}).get("id", None)

    if message == "/start" and chat_id:
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": "Welcome! 👋 Your Telegram bot is working!"
        }
    return {"ok": True}

