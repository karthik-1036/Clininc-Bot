from fastapi import APIRouter, Request
import httpx
import os

router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Better to load from .env
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@router.post(f"/telegram/{TELEGRAM_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("✅ Telegram update received:")
    print(data)

    message = data.get("message")
    if not message:
        print("⚠️ No message field in update.")
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    print(f"👤 Chat ID: {chat_id}")
    print(f"📩 Incoming Text: {text}")

    if text == "/start":
        reply_text = "👋 Welcome to the Clinic Bot! How can I help you today?"
    else:
        reply_text = f"You said: {text}"

    await send_telegram_message(chat_id, reply_text)
    return {"ok": True}

async def send_telegram_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
            print("➡️ Sending message to Telegram...")
            print("📬 Status Code:", response.status_code)
            print("📬 Telegram API Response:", response.text)
        except Exception as e:
            print("❌ Failed to send Telegram message:", str(e))
