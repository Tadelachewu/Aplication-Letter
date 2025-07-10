import telebot
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def get_user_id(message):
    print(f"Message from {message.from_user.first_name} (@{message.from_user.username})")
    print(f"User ID: {message.from_user.id}")
    bot.reply_to(message, f"Hello @{message.from_user.username or 'there'}! Logging your ID...")

bot.polling()