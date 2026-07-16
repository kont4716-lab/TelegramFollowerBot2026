import os
import asyncio
import logging
import json
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ====================== إعدادات ======================
TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN غير موجود في Environment Variables")

WEBHOOK_URL = "https://telegramfollowerbot2026-1.onrender.com"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app = Flask(__name__)

# إنشاء التطبيق
telegram_app = Application.builder().token(TOKEN).build()

DATA_FILE = "users_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users_data = load_data()
DEV_PROFILE = "https://www.facebook.com/profile.php?id=61587991323622"

# ====================== الأوامر ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users_data:
        users_data[user_id] = {"fb_link": None, "points": 0, "followed_dev": False}
        save_data(users_data)
    
    keyboard = [[InlineKeyboardButton("Continue", callback_data="continue")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Bienvenue dans le bot de support des comptes Facebook !\n\n"
        "Pour commencer, veuillez fournir le lien de votre compte Facebook.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    if user_id not in users_data or users_data[user_id].get("fb_link"):
        return
    
    if "facebook.com" not in text.lower():
        await update.message.reply_text("Veuillez envoyer un lien Facebook valide.")
        return
    
    users_data[user_id]["fb_link"] = text
    save_data(users_data)
    
    keyboard = [[InlineKeyboardButton("Continue", callback_data="profile_created")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("تم انشاء ملفك الشخصي\n\nPoints: 0", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data
    
    await query.answer()
    
    if data == "continue":
        await query.edit_message_text("الرجاء إرسال رابط حسابك على فيسبوك:")
    
    elif data == "profile_created":
        keyboard = [[InlineKeyboardButton("All Points", callback_data="all_points")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("تم انشاء ملفك الشخصي\n\nPoints: 0", reply_markup=reply_markup)
    
    elif data == "all_points":
        keyboard = [
            [InlineKeyboardButton("Follow Developer", url=DEV_PROFILE)],
            [InlineKeyboardButton("Done", callback_data="done_follow")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"المطور: {DEV_PROFILE}\n\nيرجى متابعة الحساب أعلاه.",
            reply_markup=reply_markup
        )
    
    elif data == "done_follow":
        user = users_data.get(user_id, {})
        if not user.get("followed_dev"):
            user["points"] = user.get("points", 0) + 1
            user["followed_dev"] = True
            users_data[user_id] = user
            save_data(users_data)
            await query.edit_message_text(
                f"مبروك! حصلت على 1 نقطة.\n\nPoints: {user['points']}\n\nحسابك محفوظ دائماً."
            )
        else:
            await query.edit_message_text(f"Points: {user.get('points', 0)}\n\nلقد حصلت على نقاطك بالفعل.")

# ====================== إضافة الهاندلرز ======================
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_message))

# ====================== Flask Routes ======================
@app.route("/")
def home():
    return "✅ Telegram Facebook Support Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    
    async def process():
        await telegram_app.process_update(update)
    
    asyncio.run(process())
    return "OK"

async def setup_bot():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    await telegram_app.start()
    print("🤖 Bot started successfully with webhook!")

if __name__ == "__main__":
    asyncio.run(setup_bot())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
