import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! 👋")

async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if any(word in text for word in [
        "مرحبا",
        "السلام عليكم",
        "السلام",
        "سلام",
        "hello",
        "hi"
    ]):
        await update.message.reply_text("وعليكم السلام ورحمة الله وبركاته 🌹")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, greetings))

@app.route("/")
def home():
    return "Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

if __name__ == "__main__":
    import asyncio

    async def main():
        await telegram_app.initialize()
        await telegram_app.bot.set_webhook(
            url=f"https://telegramfollowerbot2026-1.onrender.com/{TOKEN}"
        )

    asyncio.run(main())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
