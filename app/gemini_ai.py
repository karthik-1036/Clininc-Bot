import httpx
import os
from dotenv import load_dotenv
load_dotenv()


async def analyze_feedback(text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": os.getenv("GEMINI_API_KEY")}

    prompt = f"""Analyze the sentiment and summarize this patient feedback:
    "{text}"
    Respond in this format:
    {{
      "summary": "...",
      "sentiment": "positive" | "neutral" | "negative"
    }}"""

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=body, params=params, headers=headers)
        raw = res.json()
        output = raw['candidates'][0]['content']['parts'][0]['text']
        return eval(output)  # You can use json.loads(output) if formatted correctly
