from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "ضع_توكن_البوت_هنا"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك 👋")

async def reply_to_greeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()

    if any(word in message for word in ["مرحبا", "السلام", "سلام", "hello", "hi"]):
        await update.message.reply_text("وعليكم السلام 👋 أهلاً بك")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_greeting))

app.run_polling()
