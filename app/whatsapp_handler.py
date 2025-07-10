from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from app.sheets import save_appointment, save_feedback
from app.gemini_ai import analyze_feedback
from dotenv import load_dotenv
load_dotenv()


session = {}

FAQ = {
    "clinic hours": "🕒 We’re open Mon–Sat, 9am to 7pm.",
    "location": "📍 2nd Main, Mysore. https://goo.gl/maps/example",
}

async def handle_message(data):
    msg = data.get("Body", "").strip().lower()
    sender = data.get("From", "")
    resp = MessagingResponse()
    reply = resp.message()

    # FAQ handling
    for question in FAQ:
        if question in msg:
            reply.body(FAQ[question])
            return PlainTextResponse(str(resp))

    # Feedback flow
    if msg.startswith("feedback:"):
        feedback_text = msg.split("feedback:", 1)[1].strip()
        summary = await analyze_feedback(feedback_text)
        save_feedback(sender, feedback_text, summary)
        reply.body("🙏 Thank you for your feedback! Would you like to leave a Google review?\nhttps://g.page/your-clinic/review")
        return PlainTextResponse(str(resp))

    # Appointment Booking
    if sender not in session:
        session[sender] = {"step": "name"}
        reply.body("👋 Welcome! What is your name?")
    else:
        state = session[sender]
        if state["step"] == "name":
            state["name"] = msg.title()
            state["step"] = "date"
            reply.body(f"📅 Great, {state['name']}! What date do you want to book?")
        elif state["step"] == "date":
            state["date"] = msg
            state["step"] = "time"
            reply.body("⏰ What time works best for you?")
        elif state["step"] == "time":
            state["time"] = msg
            save_appointment(state["name"], state["date"], state["time"], sender)
            reply.body(f"✅ Booking confirmed!\n👤 {state['name']}\n📅 {state['date']}\n⏰ {state['time']}")
            session.pop(sender)

    return PlainTextResponse(str(resp))
