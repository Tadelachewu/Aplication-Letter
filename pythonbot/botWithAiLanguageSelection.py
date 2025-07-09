import os
import telebot
import requests
import time
import traceback
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
user_languages = {}

# === Debug Setup ===
DEBUG = True

def debug_log(message):
    if DEBUG:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] DEBUG: {message}")

# === Language Selection Buttons ===
def get_language_buttons():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am")
    )
    return markup

# === Gemini Romantic AI ===
def ask_romantic_ai(user_input, language):
    headers = {"Content-Type": "application/json"}
    
    if language == "am":
        prompt = f"""አንተ በፍቅር የተሞላ ታደለ ነህ። ዘቤን በጣም ትወዳለህ። መልስህ ከፍተኛ ፍቅር፣ ሞገስና ቅንነት ያለው ይሁን።\n\nዘቤ፦ {user_input}\nታደለ፦"""
    else:
        prompt = f"""You are Tadele, a deeply romantic and loving boyfriend. Your replies to Zebe should always be full of love, sweetness, kindness, and poetry.\n\nZebe: {user_input}\nTadele:"""

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ],
        "generationConfig": {
            "temperature": 0.9,
            "topP": 1,
            "topK": 1,
            "maxOutputTokens": 2048
        }
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' not in result or not result['candidates']:
            return "💔 Gemini didn't return a valid response"
            
        return result['candidates'][0]['content']['parts'][0]['text']
        
    except requests.exceptions.RequestException as e:
        debug_log(f"API Error: {str(e)}")
        return "💔 Sorry, I'm having trouble connecting to the AI service."
    except Exception as e:
        debug_log(f"Unexpected Error: {str(e)}\n{traceback.format_exc()}")
        return "💔 An unexpected error occurred. Please try again."

# === /start Command ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        debug_log(f"/start from {message.from_user.id}")
        welcome_msg = """
💖 Welcome to LoveBot! 

I'm here to help you express your feelings in a romantic way. Please select your preferred language:
        """
        bot.send_message(
            message.chat.id,
            welcome_msg,
            reply_markup=get_language_buttons()
        )
    except Exception as e:
        debug_log(f"Start Error: {str(e)}")
        bot.send_message(message.chat.id, "⚠️ Couldn't initialize the bot. Please try again.")

# === Callback Handler ===
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    try:
        debug_log(f"📲 Raw callback data received - ID: {call.id} | Data: {call.data} | From: {call.from_user.id}")
        debug_log(f"📝 Full callback object: {call}")
        
        if call.data.startswith("lang_"):
            debug_log("🔄 Processing language selection callback")
            lang = call.data.split("_")[1]
            user_languages[call.from_user.id] = lang
            
            debug_log(f"🌐 Setting language to: {lang} for user {call.from_user.id}")
            
            # First answer the callback query
            bot.answer_callback_query(call.id, text=f"✓ {lang.upper()} language selected!")
            debug_log("✅ Callback query answered")
            
            # Then edit the original message
            try:
                if lang == "am":
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="✅ ቋንቋዎ ወደ አማርኛ ተቀይሯል!"
                    )
                else:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="✅ Language set to English!"
                    )
                debug_log("✏️ Original message edited")
            except Exception as edit_error:
                debug_log(f"⚠️ Couldn't edit message: {edit_error}")
                # Fallback to sending new message
                bot.send_message(call.message.chat.id, 
                                "✅ Language updated!" if lang == "en" 
                                else "✅ ቋንቋዎ ተቀይሯል!")
                
    except Exception as e:
        debug_log(f"🔥 Critical callback error: {str(e)}\n{traceback.format_exc()}")
        try:
            bot.answer_callback_query(call.id, text="⚠️ Error processing your request")
        except:
            pass  # Prevent infinite error loops

# === Message Handler ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.from_user.id
        
        if user_id not in user_languages:
            bot.send_message(
                message.chat.id,
                "🌍 Please select your language first:",
                reply_markup=get_language_buttons()
            )
            return

        bot.send_chat_action(message.chat.id, 'typing')
        response = ask_romantic_ai(message.text, user_languages[user_id])
        bot.send_message(message.chat.id, response)
        
    except Exception as e:
        debug_log(f"Message Error: {str(e)}")
        bot.send_message(message.chat.id, "💔 Sorry, I couldn't process your message")

# === Error Handler ===
@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def handle_unsupported_content(message):
    bot.reply_to(message, "⚠️ I can only process text messages right now.")

# === Main Loop ===
if __name__ == "__main__":
    debug_log("🤖 Starting LoveBot...")
    
    while True:
        try:
            debug_log("🔃 Starting polling...")
            bot.polling(none_stop=True, interval=3, timeout=30)
        except Exception as e:
            debug_log(f"Polling Error: {str(e)}")
            time.sleep(10)