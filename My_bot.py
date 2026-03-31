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


# 🧠 FREE AI FUNCTION (HuggingFace - FIXED)
def ask_ai(prompt):
    try:
        response = requests.post(
            "https://router.huggingface.co/hf-inference/models/google/flan-t5-base",
            headers={
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "inputs": prompt
            },
            timeout=30
        )

        print("STATUS:", response.status_code)
        print("RAW:", response.text)

        # ✅ Handle non-200 responses
        if response.status_code != 200:
            return f"⚠️ API Error ({response.status_code})"

        data = response.json()

        # ✅ Correct response parsing
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "⚠️ No response")

        elif isinstance(data, dict) and "error" in data:
            return f"⚠️ API Error: {data['error']}"

        else:
            return "⚠️ Unexpected AI response"

    except requests.exceptions.Timeout:
        return "⏳ AI is taking too long. Try again."

    except Exception as e:
        print("ERROR:", e)
        return "⚠️ AI system error"


# 🚀 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Agent is LIVE (FREE MODE)!\n\n"
        "/plan → Daily plan\n"
        "Or just send a message 💬"
    )


# 📅 Plan Command
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (
        "Create a structured daily plan for a CUET student "
        "studying Calculus, C++, and Web Development. "
        "Make it practical with time blocks."
    )

    reply = ask_ai(prompt)
    await update.message.reply_text(reply)


# 💬 Chat Handler
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


# ▶️ Run
if __name__ == "__main__":
    main()