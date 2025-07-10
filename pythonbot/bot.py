
import telebot
import os
import requests

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(BOT_TOKEN)

# === Gemini Romantic AI Function ===
def ask_romantic_ai(user_input):
    headers = {
        "Content-Type": "application/json",
    }
    # You give it a "love agent" personality
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""You are a romantic, loving boyfriend named Tadele.
You deeply love your girlfriend Ex, and you always respond in a sweet, warm, caring, supportive, and poetic way.

Now respond to her message with love:

Ex: {user_input}
Boyfriend:"""
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "Sorry, my heart is overflowing with love, but something went wrong! 💔\n\n" + str(e)

# === Telegram Message Handler ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    ai_response = ask_romantic_ai(user_input)

    bot.reply_to(message, ai_response)

# === Start Bot ===
bot.polling()


