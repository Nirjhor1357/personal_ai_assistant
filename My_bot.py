from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests
import json

MEMORY_FILE = "memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
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
    user_id = str(update.message.from_user.id)
    memory = load_memory()

    user_data = memory.get(user_id, {})

    goal = user_data.get("goal", "be productive")
    last_focus = user_data.get("last_focus", "nothing yet")

    prompt = f"""
User goal: {goal}
Last focus: {last_focus}

Create a structured daily plan.
"""

    reply = ask_ai(prompt)
    await update.message.reply_text(reply)
    memory[user_id]["last_focus"] = "Calculus"
    save_memory(memory)

# 💬 Chat
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_msg = update.message.text.lower()

    memory = load_memory()
    user_data = memory.get(user_id, {})

    # 🧠 Direct memory responses
    if "my goal" in user_msg:
        goal = user_data.get("goal", "You haven't set a goal yet.")
        await update.message.reply_text(f"🎯 Your goal: {goal}")
        return

    if "my focus" in user_msg:
        focus = user_data.get("last_focus", "No focus set yet.")
        await update.message.reply_text(f"🎯 Last focus: {focus}")
        return

    # 🧠 Save last message
    if user_id not in memory:
        memory[user_id] = {}

    memory[user_id]["last_message"] = user_msg
    save_memory(memory)

    # 🤖 AI or fallback
    reply = ask_ai(user_msg)
    await update.message.reply_text(reply)
    
    
# ▶️ Set Goal
async def setgoal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    goal_text = " ".join(context.args)

    if not goal_text:
        await update.message.reply_text("❗ Usage: /setgoal your_goal_here")
        return

    memory = load_memory()

    if user_id not in memory:
        memory[user_id] = {}

    memory[user_id]["goal"] = goal_text

    save_memory(memory)

    await update.message.reply_text(f"🎯 Goal saved: {goal_text}")

# ▶️ Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(CommandHandler("setgoal", setgoal))
    
    print("🤖 Bot is running...")
    app.run_polling()


# ▶️ Run
if __name__ == "__main__":
    main()