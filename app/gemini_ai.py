# telegram_handler.py

import httpx
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_telegram_message(data):
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip().lower()

    print("Incoming Telegram Message:", message)

    if not chat_id or not text:
        return {"ok": True}  # Nothing to reply

    # Example FAQ reply
    if "clinic hours" in text:
        reply = "🕒 We’re open:\nMon–Sat\n9 AM – 7 PM"
    elif text.startswith("feedback:"):
        reply = "🙏 Thank you for your feedback!"
    else:
        reply = "👋 Welcome to our clinic! Type 'clinic hours' or 'feedback: your message'"

    # Send reply back to Telegram
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

    return {"ok": True}
