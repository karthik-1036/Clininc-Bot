from fastapi import FastAPI, Request
from app.whatsapp_handler import handle_message

app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    return await handle_message(form)
