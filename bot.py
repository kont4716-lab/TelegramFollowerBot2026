import telebot
from telebot import types
import json
import os
from datetime import datetime

# Replace with your bot token
TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users_data.json"

# Load data from JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# Save data to JSON file
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users_data = load_data()

# Developer Facebook profile
DEV_PROFILE = "https://www.facebook.com/profile.php?id=61587991323622"

# Start command - French welcome
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
    continue_btn = types.InlineKeyboardButton("Continue", callback_data="continue")
    markup.add(continue_btn)
    
    welcome_text = (
        "Bienvenue dans le bot de support des comptes Facebook !\n\n"
        "Pour commencer, veuillez fournir le lien de votre compte Facebook."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Handle Facebook link input
@bot.message_handler(func=lambda message: True)
def handle_fb_link(message):
    user_id = str(message.chat.id)
    if user_id not in users_data or users_data[user_id].get("fb_link"):
        return  # Already has link or not started
    
    fb_link = message.text.strip()
    if "facebook.com" not in fb_link.lower():
        bot.send_message(message.chat.id, "Veuillez envoyer un lien Facebook valide.")
        return
    
    users_data[user_id]["fb_link"] = fb_link
    save_data(users_data)
    
    markup = types.InlineKeyboardMarkup()
    continue_btn = types.InlineKeyboardButton("Continue", callback_data="profile_created")
    markup.add(continue_btn)
    
    bot.send_message(
        message.chat.id,
        f"تم انشاء ملفك الشخصي\n\nPoints: 0",
        reply_markup=markup
    )

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = call.data
    
    if data == "continue":
        bot.edit_message_text(
            "الرجاء إرسال رابط حسابك على فيسبوك:",
            call.message.chat.id,
            call.message.message_id
        )
    
    elif data == "profile_created":
        markup = types.InlineKeyboardMarkup()
        points_btn = types.InlineKeyboardButton("All Points", callback_data="all_points")
        markup.add(points_btn)
        
        bot.edit_message_text(
            "تم انشاء ملفك الشخصي\n\nPoints: 0",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    elif data == "all_points":
        if user_id not in users_data:
            bot.answer_callback_query(call.id, "Error: Profile not found.")
            return
        
        markup = types.InlineKeyboardMarkup()
        follow_btn = types.InlineKeyboardButton("Follow Developer", url=DEV_PROFILE)
        done_btn = types.InlineKeyboardButton("Done", callback_data="done_follow")
        markup.row(follow_btn)
        markup.row(done_btn)
        
        bot.edit_message_text(
            f"المطور: {DEV_PROFILE}\n\n"
            "يرجى متابعة الحساب أعلاه للحصول على النقاط.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    elif data == "done_follow":
        if user_id not in users_data:
            bot.answer_callback_query(call.id, "Error.")
            return
        
        user = users_data[user_id]
        if not user.get("followed_dev"):
            user["points"] = user.get("points", 0) + 1
            user["followed_dev"] = True
            save_data(users_data)
            
            bot.edit_message_text(
                f"مبروك! حصلت على 1 نقطة.\n\n"
                f"Points: {user['points']}\n\n"
                "حسابك محفوظ في قاعدة البيانات وسيبقى دائماً.",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.edit_message_text(
                f"Points: {user.get('points', 0)}\n\n"
                "لقد حصلت على نقاطك بالفعل.",
                call.message.chat.id,
                call.message.message_id
            )
    
    bot.answer_callback_query(call.id)

# Help command
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Bot de support Facebook.\n\n"
        "Utilisez /start pour commencer.\n"
        "Tout est sauvegardé de manière persistante."
    )

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
