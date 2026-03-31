from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# 🔑 Your Telegram Bot Token
import os
TELEGRAM_TOKEN = os.getenv("8651088811:AAFce9S34eHp7tKwWqRGvEjZkqDubuAGpTs")

# 🧠 Local AI Function (Ollama)
def ask_local_ai(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

# 🚀 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Your Personal AI Agent is LIVE!\nUse /plan to start your day.")

# 📅 Plan Command
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = """
You are my Personal AI Agent.

I am a Mechatronics student at CUET.
I am learning C++, Web Development, and Calculus.
I want to freelance and go abroad for MS.

Create a clear, structured daily plan with priorities.
Keep it practical and realistic.
"""

    reply = "🤖 AI is temporarily disabled (hosting test successful!)"
    await update.message.reply_text(reply)

# 💬 Chat Handler
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    prompt = f"""
You are my Personal AI Agent.

User message: {user_msg}

Give a helpful, clear, and practical response.
"""

    reply = ask_local_ai(prompt)
    await update.message.reply_text(reply)

# ▶️ Run Bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("plan", plan))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Bot is running...")
app.run_polling()