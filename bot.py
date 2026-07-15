import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

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

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, greetings))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
