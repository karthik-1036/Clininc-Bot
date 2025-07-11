from fastapi import APIRouter, Request
import httpx, os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()
telegram_router = APIRouter()

TELEGRAM_TOKEN = "7916999347:AAEZdSsrl3d77bZKvBiKWrVNblZbhNzpyak"  # Better to load from .en
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Temporary in-memory user state (can be upgraded to Redis/DB)
user_state: Dict[int, str] = {}

@telegram_router.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != TELEGRAM_TOKEN:
        return {"status": "unauthorized"}

    data = await request.json()
    print("📥 Incoming Telegram Update:", data)

    message = data.get("message")
    if not message:
        return {"status": "ignored"}

    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # Handle commands and flow
    if text == "/start":
        reply = "👋 Welcome to Mysore Clinic Bot! You can:\n/book - Book Appointment\n/faq - Ask a Question\n/feedback - Leave Feedback"
    elif text == "/book":
        user_state[chat_id] = "awaiting_name"
        reply = "📋 Great! What's your full name?"
    elif chat_id in user_state:
        state = user_state[chat_id]
        reply = handle_booking(chat_id, state, text)
    else:
        reply = "❓ I didn't understand that. Try /start"

    # Send reply
    await send_telegram_message(chat_id, reply)
    return {"status": "ok"}

def handle_booking(chat_id: int, state: str, text: str) -> str:
    if state == "awaiting_name":
        user_state[chat_id] = {"name": text, "step": "awaiting_age"}
        return "📅 Thanks! How old are you?"
    elif isinstance(user_state[chat_id], dict) and user_state[chat_id].get("step") == "awaiting_age":
        user_state[chat_id]["age"] = text
        user_state[chat_id]["step"] = "awaiting_date"
        return "🗓️ What date would you like to book the appointment for? (e.g., 2025-07-15)"
    elif user_state[chat_id]["step"] == "awaiting_date":
        user_state[chat_id]["date"] = text
        user_state[chat_id]["step"] = "awaiting_time"
        return "⏰ What time?"
    elif user_state[chat_id]["step"] == "awaiting_time":
        user_state[chat_id]["time"] = text
        # Final step: save and confirm
        info = user_state.pop(chat_id)
        return f"✅ Appointment booked for {info['name']} (Age: {info['age']}) on {info['date']} at {info['time']}.\nWe'll see you then!"
    return "⚠️ Unexpected response. Please try again."

async def send_telegram_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
        except Exception as e:
            print("❌ Telegram send error:", str(e))
