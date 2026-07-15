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

WEBHOOK_URL = "https://telegramfollowerbot2026-1.onrender.com"


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()


# تخزين الصور مؤقتاً
saved_photos = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحباً بك في البوت!\n\n"
        "📸 أرسل صورة لحفظها.\n"
        "📂 استخدم /extract لإرسال الصور المحفوظة.\n\n"
        "اكتب /help لرؤية الأوامر."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ الأوامر:\n\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/info - معلومات البوت\n"
        "/extract - استخراج الصور المحفوظة"
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"ℹ️ البوت يعمل بنجاح 🚀\n\n"
        f"📸 عدد الصور المحفوظة: {len(saved_photos)}"
    )


async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]

    saved_photos.append(photo.file_id)

    await update.message.reply_text(
        f"✅ تم حفظ الصورة\n\n"
        f"📸 عدد الصور المحفوظة: {len(saved_photos)}"
    )


async def extract_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not saved_photos:
        await update.message.reply_text(
            "❌ لا توجد صور محفوظة"
        )
        return

    await update.message.reply_text(
        f"📸 عدد الصور المحفوظة: {len(saved_photos)}\n"
        "⏳ جاري إرسال الصور..."
    )

    for photo_id in saved_photos:
        await update.message.reply_photo(
            photo=photo_id
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message and update.message.text:
        await update.message.reply_text(
            "📨 " + update.message.text
        )


# تسجيل الأوامر
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("info", info))
telegram_app.add_handler(CommandHandler("extract", extract_photos))


# استقبال الصور
telegram_app.add_handler(
    MessageHandler(filters.PHOTO, save_photo)
)


# استقبال النصوص
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

    async def process_update():
        await telegram_app.process_update(update)

    asyncio.run(process_update())

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
