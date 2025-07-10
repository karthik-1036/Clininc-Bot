from fastapi import FastAPI, Request
from app.whatsapp_handler import handle_message
import uvicorn

app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    return await handle_message(form)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=False)
