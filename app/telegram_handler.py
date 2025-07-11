from fastapi import APIRouter, Request
import httpx

router = APIRouter()

TELEGRAM_TOKEN = "7916999347:AAEZdSsrl3d77bZKvBiKWrVNblZbhNzpyak"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@router.post(f"/telegram/{TELEGRAM_TOKEN}")
async def telegram_webhook(request: Request):
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
        print("Telegram API response:", response.text)
