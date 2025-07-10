import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def generate_letter(prompt_text):
    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""You are a professional HR expert.
Write a formal and strong job application letter based on the following details:

{prompt_text}

Make it polite, clear, and tailored to impress the hiring manager.
"""
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"❌ Error generating letter:\n{str(e)}"
