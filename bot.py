import os
import logging

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN غير موجود في Environment Variables")

WEBHOOK_URL = "https://telegramfollowerbot2026.onrender.com"

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحباً بك في البوت!\n\nأرسل /help لرؤية الأوامر."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ الأوامر:\n"
        "/start - بدء البوت\n"
        "/help - مساعدة\n"
        "/info - معلومات"
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ البوت يعمل بنجاح على Render"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📨 " + update.message.text
    )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("info", info))
telegram_app.add_handler(MessageHandler(filters.TEXT, echo))


@app.route("/")
def home():
    return "Bot is running!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )

    telegram_app.update_queue.put_nowait(update)

    return "OK"


def run():
    import asyncio

    async def setup():
        await telegram_app.initialize()
        await telegram_app.bot.set_webhook(
            f"{WEBHOOK_URL}/{TOKEN}"
        )
        await telegram_app.start()

    asyncio.run(setup())


if __name__ == "__main__":
    run()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
