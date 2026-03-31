from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests

# 🔑 Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

# 🚨 Safety check
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN missing")

if not HF_API_KEY:
    raise ValueError("❌ HF_API_KEY missing")

print("✅ Tokens loaded")


# 🧠 FREE AI FUNCTION (HuggingFace)
def ask_ai(prompt):
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-large",
            headers={
                "Authorization": f"Bearer {HF_API_KEY}"
            },
            json={
                "inputs": prompt
            }
        )

        print("STATUS:", response.status_code)
        print("RAW:", response.text)

        data = response.json()

        if isinstance(data, list):
            return data[0].get("generated_text", "⚠️ No response")
        else:
            return f"⚠️ API Error: {data}"

    except Exception as e:
        print("ERROR:", e)
        return "⚠️ AI system error"


# 🚀 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Agent is LIVE (FREE MODE)!\n\n"
        "/plan → Daily plan\n"
        "Or just chat 💬"
    )


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


# ▶️ Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()