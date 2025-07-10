# amharic or English choice
import os

import telebot
import requests

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(BOT_TOKEN)

# === In-Memory User Language Preferences ===
user_languages = {}

# === Gemini Romantic AI Function with Language ===
def ask_romantic_ai(user_input, language):
    headers = {
        "Content-Type": "application/json",
    }

    if language == "am":
        prompt = f"""አንተ የፍቅር ሙሉ የሆነ ወንድ መብት ነህ። የሴት መሪህ ዘቤን በጣም ትወዳለህ። መልስህ በፍቅር፣ በሞገስ፣ በመነሳትና በጥሩ ቃል ይሁን።

ዘቤ፡ {user_input}
ታደለ፡"""
    else:
        prompt = f"""You are a romantic, loving boyfriend named Tadele.
You deeply love your girlfriend Zebe, and you always respond in a sweet, warm, caring, supportive, and poetic way.

Now respond to her message with love:

Zebe: {user_input}
Boyfriend:"""

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "Sorry, something went wrong. 💔\n\n" + str(e)

# === Command Handler to Set Language ===
@bot.message_handler(commands=['language'])
def set_language(message):
    args = message.text.split()
    if len(args) >= 2:
        lang = args[1].lower()
        if lang in ["am", "en"]:
            user_languages[message.from_user.id] = lang
            reply = "ቋንቋ ወደ አማርኛ ተቀይሯል።" if lang == "am" else "Language set to English."
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Please choose either `am` or `en`.\nExample: /language am")
    else:
        bot.reply_to(message, "Usage: /language am or /language en")

# === Message Handler ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    user_id = message.from_user.id
    language = user_languages.get(user_id, "en")  # default to English

    bot.send_chat_action(message.chat.id, 'typing')
    ai_response = ask_romantic_ai(user_input, language)

    bot.reply_to(message, ai_response)

# === Start Bot ===
bot.polling()
