from telegram import Update
from telegram.ext import ContextTypes

# تخزين مؤقت (سيختفي إذا أعيد تشغيل البوت)
photos = []


async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photos.append(photo.file_id)

    await update.message.reply_text(
        f"✅ تم حفظ الصورة\n📸 عدد الصور المحفوظة: {len(photos)}"
    )


async def extract_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not photos:
        await update.message.reply_text("❌ لا توجد صور محفوظة")
        return

    await update.message.reply_text(
        f"📸 عدد الصور المحفوظة: {len(photos)}\nجاري الإرسال..."
    )

    for photo_id in photos:
        await update.message.reply_photo(photo=photo_id)
