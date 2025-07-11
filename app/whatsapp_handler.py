# whatsapp_handler.py

from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from app.sheets import save_appointment, save_feedback
from app.gemini_ai import analyze_feedback
from dotenv import load_dotenv

load_dotenv()

session = {}

FAQ = {
    "clinic hours": "🕒 We’re open:\nMon–Sat\n9 AM – 7 PM",
    "location": "📍 We are located at:\n2nd Main, Mysore\n📌 https://goo.gl/maps/example",
}


async def handle_message(data):
    msg = data.get("Body", "").strip().lower()
    sender = data.get("From", "")
    resp = MessagingResponse()
    reply = resp.message()

    # Handle FAQs
    for question in FAQ:
        if question in msg:
            reply.body(FAQ[question])
            return PlainTextResponse(str(resp))

    # Handle Feedback
    if msg.startswith("feedback:"):
        feedback_text = msg.split("feedback:", 1)[1].strip()
        summary = await analyze_feedback(feedback_text)
        save_feedback(sender, feedback_text, summary)
        reply.body(
            "🙏 Thank you for your feedback!\n\n"
            "Would you like to leave us a Google review?\n⭐ https://g.page/your-clinic/review"
        )
        return PlainTextResponse(str(resp))

    # Handle Appointment Booking Flow
    if sender not in session:
        session[sender] = {"step": "name"}
        reply.body("👋 Welcome!\nWhat is your name?")
    else:
        state = session[sender]

        if state["step"] == "name":
            state["name"] = msg.title()
            state["step"] = "date"
            reply.body(f"📅 Great, {state['name']}!\nWhat date would you like to book?")
        
        elif state["step"] == "date":
            state["date"] = msg
            state["step"] = "time"
            reply.body("⏰ What time works best for you?")
        
        elif state["step"] == "time":
            state["time"] = msg
            save_appointment(state["name"], state["date"], state["time"], sender)
            reply.body(
                f"✅ Your appointment is confirmed!\n\n"
                f"👤 Name: {state['name']}\n"
                f"📅 Date: {state['date']}\n"
                f"⏰ Time: {state['time']}\n\n"
                "Thank you for choosing us! 😊"
            )
            session.pop(sender)

    return PlainTextResponse(str(resp))
