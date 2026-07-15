import os
import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import logging

# التوكن من المتغيرات البيئية (مهم للأمان)
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN غير موجود! أضفه في Render Environment Variables.")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحباً بك في البوت!\nأرسل /help لرؤية الأوامر.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠️ الأوامر:\n/start - بدء البوت\n/help - مساعدة\n/info - معلومات")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ البوت يعمل بنجاح على Render")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📨 " + update.message.text)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT, echo))
    
    print("🤖 البوت يعمل بنجاح...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
