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


# 🧠 FALLBACK (ALWAYS WORKS)
def smart_fallback(prompt):
    prompt = prompt.lower()

    if "plan" in prompt:
        return (
            "📅 Your Daily Plan:\n\n"
            "1. 📚 Calculus - 2 hours\n"
            "2. 💻 C++ Practice - 1.5 hours\n"
            "3. 🌐 Web Development - 1 hour\n\n"
            "🚀 Stay consistent!"
        )

    elif "focus" in prompt:
        return "🎯 Focus on Calculus first. It has the highest impact right now."

    elif "hi" in prompt or "hello" in prompt:
        return "👋 Hey! I'm your AI Agent. Use /plan or ask me anything."

    else:
        return "🤖 I'm having trouble with AI right now, but I'm still here to help!"


# 🧠 AI FUNCTION (STABLE)
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
            timeout=25
        )

        print("STATUS:", response.status_code)

        # ❌ If API fails → fallback
        if response.status_code != 200:
            return smart_fallback(prompt)

        data = response.json()

        # ✅ Handle success
        if isinstance(data, list) and len(data) > 0:
            text = data[0].get("generated_text", "").strip()
            return text if text else smart_fallback(prompt)

        # ❌ API error format
        if isinstance(data, dict) and "error" in data:
            print("HF ERROR:", data)
            return smart_fallback(prompt)

        return smart_fallback(prompt)

    except requests.exceptions.Timeout:
        return "⏳ AI is slow right now. Try again."

    except Exception as e:
        print("ERROR:", e)
        return smart_fallback(prompt)


# 🚀 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Agent is LIVE (FREE MODE)!\n\n"
        "/plan → Daily plan\n"
        "Or just send a message 💬"
    )


# 📅 Plan
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = (
        "Create a structured daily plan for a CUET student "
        "studying Calculus, C++, and Web Development. "
        "Make it practical with time blocks."
    )

    reply = ask_ai(prompt)
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


# ▶️ Run
if __name__ == "__main__":
    main()