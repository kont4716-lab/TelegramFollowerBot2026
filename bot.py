import os
import asyncio
import logging
import sqlite3

from flask import Flask, request

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# ==========================
# الإعدادات
# ==========================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN غير موجود في Environment Variables")


WEBHOOK_URL = "https://telegramfollowerbot2026-1.onrender.com"


DEVELOPER_FACEBOOK = (
    "https://www.facebook.com/profile.php?id=61587991323622"
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)



app = Flask(__name__)


telegram_app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)



# ==========================
# قاعدة البيانات SQLite
# ==========================

db = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY,

    username TEXT,

    facebook TEXT,

    points INTEGER DEFAULT 0

)
""")


db.commit()



# ==========================
# إنشاء مستخدم
# ==========================

def create_user(user_id, username):

    cursor.execute(
        "SELECT id FROM users WHERE id=?",
        (user_id,)
    )

    result = cursor.fetchone()


    if not result:

        cursor.execute(
            """
            INSERT INTO users
            (id, username, facebook, points)

            VALUES(?,?,?,?)
            """,

            (
                user_id,
                username or "Unknown",
                "",
                0
            )
        )

        db.commit()



# ==========================
# قائمة الأوامر
# ==========================

async def set_commands():

    commands = [

        BotCommand(
            "start",
            "تشغيل البوت"
        ),

        BotCommand(
            "addfacebook",
            "إضافة حساب فيسبوك"
        ),

        BotCommand(
            "profile",
            "حسابي"
        ),

        BotCommand(
            "accounts",
            "الحسابات"
        ),

        BotCommand(
            "top",
            "المتصدرون"
        ),

        BotCommand(
            "info",
            "معلومات البوت"
        )

    ]


    await telegram_app.bot.set_my_commands(commands)




# ==========================
# START
# ==========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    create_user(
        user.id,
        user.username
    )


    keyboard = [

        [
            InlineKeyboardButton(
                "👨‍💻 حساب المطور",
                url=DEVELOPER_FACEBOOK
            )
        ]

    ]


    await update.message.reply_text(

        "👋 أهلاً بك في نظام تبادل الحسابات\n\n"

        "اختر أمر من القائمة أو اكتب / لرؤية الأوامر\n\n"

        "📘 يمكنك إضافة حسابك باستعمال:\n"
        "/addfacebook",

        reply_markup=
        InlineKeyboardMarkup(keyboard)

    )



# ==========================
# إضافة حساب فيسبوك
# ==========================

async def add_facebook(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    create_user(
        user.id,
        user.username
    )


    context.user_data[
        "waiting_facebook"
    ] = True



    await update.message.reply_text(

        "📘 أرسل الآن رابط حساب فيسبوك الخاص بك:"
      
    # ==========================
# استقبال رابط فيسبوك
# ==========================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id


    if context.user_data.get("waiting_facebook"):

        link = update.message.text


        cursor.execute(
            """
            UPDATE users
            SET facebook=?
            WHERE id=?
            """,

            (
                link,
                user_id
            )
        )


        db.commit()


        context.user_data[
            "waiting_facebook"
        ] = False



        await update.message.reply_text(
            "✅ تم حفظ حسابك بنجاح\n"
            "يمكنك الآن استخدام البوت."
        )

        return



    await update.message.reply_text(
        "استخدم / لرؤية الأوامر"
    )




# ==========================
# الملف الشخصي
# ==========================

async def profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id


    create_user(
        user_id,
        update.effective_user.username
    )


    cursor.execute(
        """
        SELECT username, facebook, points
        FROM users
        WHERE id=?
        """,

        (user_id,)
    )


    data = cursor.fetchone()



    await update.message.reply_text(

        "👤 حسابك\n\n"

        f"📘 فيسبوك:\n{data[1] or 'غير مضاف'}\n\n"

        f"⭐ النقاط: {data[2]}"

    )





# ==========================
# عرض الحسابات
# ==========================

async def accounts(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    cursor.execute(
        """
        SELECT username, facebook, points
        FROM users
        WHERE facebook != ''
        """
    )


    rows = cursor.fetchall()



    if not rows:

        await update.message.reply_text(
            "لا توجد حسابات مضافة حاليا"
        )

        return



    text = "📘 الحسابات:\n\n"


    for row in rows:

        text += (

            f"👤 {row[0]}\n"

            f"⭐ {row[2]} نقطة\n"

            f"{row[1]}\n\n"

        )



    await update.message.reply_text(text)





# ==========================
# المتصدرون
# ==========================

async def top(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    cursor.execute(
        """
        SELECT username, points
        FROM users
        ORDER BY points DESC
        LIMIT 10
        """
    )


    rows = cursor.fetchall()


    text = "🏆 المتصدرون:\n\n"



    for index, row in enumerate(rows, 1):

        text += (

            f"{index}- {row[0]}\n"

            f"⭐ {row[1]} نقطة\n\n"

        )



    await update.message.reply_text(text)





# ==========================
# معلومات البوت
# ==========================

async def info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    count = cursor.fetchone()[0]


    await update.message.reply_text(

        "🤖 البوت يعمل\n\n"

        f"👥 عدد المستخدمين: {count}"

    )





# ==========================
# تسجيل الأوامر
# ==========================

telegram_app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


telegram_app.add_handler(
    CommandHandler(
        "addfacebook",
        add_facebook
    )
)


telegram_app.add_handler(
    CommandHandler(
        "profile",
        profile
    )
)


telegram_app.add_handler(
    CommandHandler(
        "accounts",
        accounts
    )
)


telegram_app.add_handler(
    CommandHandler(
        "top",
        top
    )
)


telegram_app.add_handler(
    CommandHandler(
        "info",
        info
    )
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




@app.route(
    f"/{TOKEN}",
    methods=["POST"]
)

def webhook():

    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )


    asyncio.run(
        telegram_app.process_update(update)
    )


    return "OK"





# ==========================
# تشغيل البوت
# ==========================

async def setup_bot():

    await telegram_app.initialize()


    await set_commands()



    await telegram_app.bot.set_webhook(

        f"{WEBHOOK_URL}/{TOKEN}"

    )


    await telegram_app.start()



    print(
        "🤖 Bot started successfully"
    )





if __name__ == "__main__":


    asyncio.run(
        setup_bot()
    )


    app.run(

        host="0.0.0.0",

        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )

))
