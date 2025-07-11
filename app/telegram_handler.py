from fastapi import APIRouter, Request
import httpx
import os

telegram_router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Better to load from .env
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@telegram_router.post("/telegram/7916999347:AAEZdSsrl3d77bZKvBiKWrVNblZbhNzpyak")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("📥 Incoming Telegram Update:", data)

    message = data.get("message")
    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        reply_text = f"👋 You said: {text}"

        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply_text},
            )

    return {"status": "ok"}

async def send_telegram_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
            print("➡️ Sending message to Telegram...")
            print("📬 Status Code:", response.status_code)
            print("📬 Telegram API Response:", response.json())
        except Exception as e:
            print("❌ Failed to send Telegram message:", str(e))
