from fastapi import APIRouter, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

telegram_router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


@telegram_router.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != TELEGRAM_TOKEN:
        return {"ok": False, "description": "Invalid token"}

    data = await request.json()
    print("Telegram update received:", data)

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        reply_text = "👋 Welcome to the Clinic Bot! How can I help you today?"
    else:
        reply_text = f"You said: {text}"

    await send_telegram_message(chat_id, reply_text)
    return {"ok": True}


async def send_telegram_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )
        print("➡️ Sending message to Telegram...")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)


