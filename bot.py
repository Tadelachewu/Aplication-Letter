import os
import telebot
from dotenv import load_dotenv
from letter_ai import generate_letter

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Store user inputs step-by-step
user_data = {}

# Step order
steps = [
    "full_name",
    "address",
    "phone",
    "email",
    "job_title",
    "company_name",
    "experience",
    "achievements",
    "skills",
    "job_platform",
    "company_reason"
]

questions = {
    "full_name": "📝 What is your **full name**?",
    "address": "🏠 What is your **address**?",
    "phone": "📱 What is your **phone number**?",
    "email": "📧 What is your **email address**?",
    "job_title": "💼 What **job title** are you applying for?",
    "company_name": "🏢 What is the **company name**?",
    "experience": "⌛ How many **years of experience** and in what field?",
    "achievements": "🏆 Mention 1–2 **key achievements** with results (optional):",
    "skills": "🛠️ List your **top skills** (3–5):",
    "job_platform": "🌐 Where did you find the job? (e.g. LinkedIn, website)",
    "company_reason": "💡 Why do you want to work at this company?"
}

user_progress = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_progress[chat_id] = 0
    user_data[chat_id] = {}
    bot.send_message(chat_id, "👋 Welcome! I’ll help you generate a perfect job application letter.\nLet's begin!")
    ask_next_step(chat_id)

def ask_next_step(chat_id):
    step_index = user_progress.get(chat_id, 0)
    if step_index < len(steps):
        step = steps[step_index]
        bot.send_message(chat_id, questions[step], parse_mode="Markdown")
    else:
        # All inputs collected – Generate the letter
        inputs = user_data[chat_id]
        combined_prompt = (
            f"Name: {inputs['full_name']}\n"
            f"Address: {inputs['address']}\n"
            f"Phone: {inputs['phone']}\n"
            f"Email: {inputs['email']}\n"
            f"Job Title: {inputs['job_title']}\n"
            f"Company: {inputs['company_name']}\n"
            f"Experience: {inputs['experience']}\n"
            f"Achievements: {inputs.get('achievements', '')}\n"
            f"Skills: {inputs['skills']}\n"
            f"Job Platform: {inputs['job_platform']}\n"
            f"Why this company: {inputs['company_reason']}"
        )
        bot.send_chat_action(chat_id, 'typing')
        result = generate_letter(combined_prompt)
        bot.send_message(chat_id, "📄 Here's your application letter:\n\n" + result)
        # Reset user session
        user_progress[chat_id] = 0
        user_data[chat_id] = {}

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_progress:
        bot.send_message(chat_id, "Please type /start to begin your application letter.")
        return

    step_index = user_progress[chat_id]
    step_key = steps[step_index]
    user_data[chat_id][step_key] = message.text
    user_progress[chat_id] += 1
    ask_next_step(chat_id)

# Run the bot
if __name__ == "__main__":
    print("🚀 Bot is running...")
    bot.polling()
