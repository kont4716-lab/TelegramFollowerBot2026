import os
import asyncio
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحباً بك في البوت!\n\n"
        "أرسل /help لرؤية الأوامر."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ الأوامر:\n\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/info - معلومات البوت"
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ البوت يعمل بنجاح على Render 🚀"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text(
            "📨 " + update.message.text
        )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("info", info))
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
)


@app.route("/")
def home():
    return "Telegram Bot is running!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():

    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )

    asyncio.create_task(
        telegram_app.process_update(update)
    )

    return "OK"


async def setup_bot():

    await telegram_app.initialize()

    await telegram_app.bot.set_webhook(
        f"{WEBHOOK_URL}/{TOKEN}"
    )

    await telegram_app.start()

    print("🤖 Bot started successfully")


if __name__ == "__main__":

    asyncio.run(setup_bot())

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
              )
