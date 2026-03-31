from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

# 🔑 Correct way
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
print("TOKEN:", TELEGRAM_TOKEN)

# 🚨 Safety check
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is not set in environment variables!")

print("✅ Token loaded successfully")

# 🚀 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Your Personal AI Agent is LIVE!\n\n"
        "Commands:\n"
        "/plan → Get your daily plan\n"
        "/start → Restart bot"
    )

# 📅 Plan Command
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Your plan for today:\n\n"
        "1. 📚 Study Calculus (2h)\n"
        "2. 💻 Practice C++ (1.5h)\n"
        "3. 🌐 Work on Web Dev (1h)\n\n"
        "🚀 Stay focused!"
    )

# 💬 Chat Handler
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI chat is currently disabled on hosted version.\n"
        "Local AI will be added later."
    )

# ▶️ Run bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("plan", plan))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Bot is running...")
app.run_polling()