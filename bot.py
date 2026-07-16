import telebot
from telebot import types
import json
import os

# ===== إعداد التوكن لـ Render =====
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # استخدم هذا فقط للتجربة المحلية

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users_data.json"

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# Save data
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users_data = load_data()

DEV_PROFILE = "https://www.facebook.com/profile.php?id=61587991323622"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users_data:
        users_data[user_id] = {
            "fb_link": None,
            "points": 0,
            "followed_dev": False
        }
        save_data(users_data)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Continue", callback_data="continue"))
    
    bot.send_message(
        message.chat.id,
        "Bienvenue dans le bot de support des comptes Facebook !\n\n"
        "Pour commencer, veuillez fournir le lien de votre compte Facebook.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_fb_link(message):
    user_id = str(message.chat.id)
    if user_id not in users_data or users_data[user_id].get("fb_link"):
        return
    
    fb_link = message.text.strip()
    if "facebook.com" not in fb_link.lower():
        bot.send_message(message.chat.id, "Veuillez envoyer un lien Facebook valide.")
        return
    
    users_data[user_id]["fb_link"] = fb_link
    save_data(users_data)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Continue", callback_data="profile_created"))
    
    bot.send_message(message.chat.id, "تم انشاء ملفك الشخصي\n\nPoints: 0", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = call.data
    
    if data == "continue":
        bot.edit_message_text("الرجاء إرسال رابط حسابك على فيسبوك:", 
                              call.message.chat.id, call.message.message_id)
    
    elif data == "profile_created":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("All Points", callback_data="all_points"))
        bot.edit_message_text("تم انشاء ملفك الشخصي\n\nPoints: 0", 
                              call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif data == "all_points":
        if user_id not in users_data:
            bot.answer_callback_query(call.id, "Error: Profile not found.")
            return
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("Follow Developer", url=DEV_PROFILE))
        markup.row(types.InlineKeyboardButton("Done", callback_data="done_follow"))
        bot.edit_message_text(f"المطور: {DEV_PROFILE}\n\nيرجى متابعة الحساب أعلاه.", 
                              call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif data == "done_follow":
        user = users_data.get(user_id, {})
        if not user.get("followed_dev"):
            user["points"] = user.get("points", 0) + 1
            user["followed_dev"] = True
            users_data[user_id] = user
            save_data(users_data)
            bot.edit_message_text(f"مبروك! حصلت على 1 نقطة.\n\nPoints: {user['points']}\n\nحسابك محفوظ دائماً.", 
                                  call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(f"Points: {user.get('points', 0)}\n\nلقد حصلت على نقاطك بالفعل.", 
                                  call.message.chat.id, call.message.message_id)
    
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "استخدم /start لبدء البوت.")

if __name__ == "__main__":
    print("✅ Bot is running on Render...")
    bot.infinity_polling()
