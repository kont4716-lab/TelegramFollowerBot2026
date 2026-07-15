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


# ==========================
# قاعدة بيانات مؤقتة
# ==========================

users = {}


# ==========================
# تسجيل المستخدم
# ==========================

def create_user(user_id, username):

    if user_id not in users:
        users[user_id] = {
            "username": username or "Unknown",
            "facebook": None,
            "points": 0
        }


# ==========================
# start
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    create_user(
        user.id,
        user.username
    )

    await update.message.reply_text(
        "👋 أهلاً بك في نظام تبادل الحسابات\n\n"
        "الأوامر:\n\n"
        "/addfacebook - إضافة حسابك\n"
        "/profile - حسابي\n"
        "/accounts - الحسابات\n"
        "/top - المتصدرون"
    )


# ==========================
# إضافة فيسبوك
# ==========================

async def add_facebook(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    create_user(user_id, update.effective_user.username)


    await update.message.reply_text(
        "📘 أرسل الآن رابط حساب فيسبوك الخاص بك:"
    )

    context.user_data["waiting_facebook"] = True



# ==========================
# استقبال الرابط
# ==========================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if context.user_data.get("waiting_facebook"):

        link = update.message.text

        users[user_id]["facebook"] = link

        context.user_data["waiting_facebook"] = False


        await update.message.reply_text(
            "✅ تم حفظ حسابك\n"
            "يمكنك الآن جمع النقاط."
        )

        return



    await update.message.reply_text(
        "استخدم /help لرؤية الأوامر"
    )



# ==========================
# الملف الشخصي
# ==========================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    create_user(user_id, update.effective_user.username)


    data = users[user_id]


    await update.message.reply_text(
        f"👤 حسابك\n\n"
        f"📘 الرابط:\n{data['facebook']}\n\n"
        f"⭐ النقاط: {data['points']}"
    )



# ==========================
# عرض الحسابات
# ==========================

async def accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not users:
        await update.message.reply_text(
            "لا توجد حسابات بعد"
        )
        return


    text = "📘 الحسابات:\n\n"


    for user_id, data in users.items():

        if data["facebook"]:

            text += (
                f"👤 {data['username']}\n"
                f"⭐ {data['points']} نقطة\n"
                f"{data['facebook']}\n\n"
            )


    await update.message.reply_text(text)



# ==========================
# ترتيب النقاط
# ==========================

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):

    ranking = sorted(
        users.values(),
        key=lambda x: x["points"],
        reverse=True
    )


    text = "🏆 المتصدرون:\n\n"


    for i, user in enumerate(ranking[:10], 1):

        text += (
            f"{i} - {user['username']}\n"
            f"⭐ {user['points']} نقطة\n\n"
        )


    await update.message.reply_text(text)



# ==========================
# معلومات
# ==========================

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"🤖 البوت يعمل\n"
        f"👥 المستخدمون: {len(users)}"
    )



# ==========================
# تسجيل الأوامر
# ==========================

telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    CommandHandler("addfacebook", add_facebook)
)

telegram_app.add_handler(
    CommandHandler("profile", profile)
)

telegram_app.add_handler(
    CommandHandler("accounts", accounts)
)

telegram_app.add_handler(
    CommandHandler("top", top)
)

telegram_app.add_handler(
    CommandHandler("info", info)
)


telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    )
)



# ==========================
# Webhook
# ==========================

@app.route("/")
def home():
    return "Telegram Bot Running"



@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():

    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )


    async def process():

        await telegram_app.process_update(update)


    asyncio.run(process())


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
        port=int(os.environ.get("PORT",10000))
               )
