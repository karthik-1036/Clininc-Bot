# app/telegram_handler.py

from fastapi.responses import JSONResponse
import os

session = {}

FAQ = {
    "clinic hours": "🕒 We’re open:\nMon–Sat\n9 AM – 7 PM",
    "location": "📍 We are located at:\n2nd Main, Mysore\n📌 https://goo.gl/maps/example",
}

async def handle_telegram_message(data):
    message = data.get("message", {})
    text = message.get("text", "").strip().lower()
    chat_id = message.get("chat", {}).get("id")

    from app.sheets import save_appointment, save_feedback
    from app.gemini_ai import analyze_feedback
    from app.telegram_utils import send_message

    if not chat_id:
        return JSONResponse(content={"ok": False})

    # FAQs
    for question in FAQ:
        if question in text:
            await send_message(chat_id, FAQ[question])
            return JSONResponse(content={"ok": True})

    # Feedback
    if text.startswith("feedback:"):
        feedback_text = text.split("feedback:", 1)[1].strip()
        summary = await analyze_feedback(feedback_text)
        save_feedback(str(chat_id), feedback_text, summary)
        await send_message(
            chat_id,
            "🙏 Thank you for your feedback!\n\nWould you like to leave us a Google review?\n⭐ https://g.page/your-clinic/review"
        )
        return JSONResponse(content={"ok": True})

    # Appointment Flow
    if chat_id not in session:
        session[chat_id] = {"step": "name"}
        await send_message(chat_id, "👋 Welcome!\nWhat is your name?")
    else:
        state = session[chat_id]

        if state["step"] == "name":
            state["name"] = text.title()
            state["step"] = "date"
            await send_message(chat_id, f"📅 Great, {state['name']}!\nWhat date would you like to book?")

        elif state["step"] == "date":
            state["date"] = text
            state["step"] = "time"
            await send_message(chat_id, "⏰ What time works best for you?")

        elif state["step"] == "time":
            state["time"] = text
            save_appointment(state["name"], state["date"], state["time"], str(chat_id))
            await send_message(
                chat_id,
                f"✅ Your appointment is confirmed!\n\n"
                f"👤 Name: {state['name']}\n"
                f"📅 Date: {state['date']}\n"
                f"⏰ Time: {state['time']}\n\n"
                "Thank you for choosing us! 😊"
            )
            session.pop(chat_id)

    return JSONResponse(content={"ok": True})
