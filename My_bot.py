from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests

# 🔑 Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🚨 Safety check
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN missing")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY missing")

print("✅ Tokens loaded")

# 🧠 AI Function
def ask_ai(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",  # 🔥 reliable free model
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        print("STATUS:", response.status_code)
        print("RAW:", response.text)

        data = response.json()

        # ✅ SAFE parsing
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"⚠️ API Error: {data['error']}"
        else:
            return "⚠️ Unexpected response from AI"

    except Exception as e:
        print("ERROR:", e)
        return "⚠️ AI system error"

# 🚀 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 AI Agent is LIVE!\nUse /plan or just chat.")

# 📅 Plan
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ask_ai(
        "Create a structured daily plan for a CUET student studying Calculus, C++, and Web Development."
    )
    await update.message.reply_text(reply)

# 💬 Chat
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    reply = ask_ai(user_msg)
    await update.message.reply_text(reply)

# ▶️ Run bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("plan", plan))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Bot is running...")
app.run_polling()