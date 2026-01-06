import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ForceReply,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# ================== تنظیمات ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

# آی‌دی عددی ادمین (حتماً با @userinfobot بگیر)
ADMIN_ID = 8044612620  # ← اینو عوض کن

# ================== متغیرها ==================

blocked_users = set()
pending_replies = {}  # admin_id -> user_id

# ================== /start ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    if update.effective_user.id in blocked_users:
        return

    await update.message.reply_text(
        "سلام ❤️\n"
        "پیامت به صورت «ناشناس» برای ادمین ارسال می‌شه.\n"
        "پیامت رو اینجا بنویس و منتظر پاسخ باش 🤝"
    )

# ================== پیام کاربران ==================

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    user = update.effective_user

    # پیام‌های خود ادمین اینجا پردازش نشه
    if user.id == ADMIN_ID:
        return

    if user.id in blocked_users:
        return

    text = update.message.text
    username = user.username or "ندارد"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user.id}"),
            InlineKeyboardButton("⛔ مسدود", callback_data=f"block:{user.id}")
        ]
    ])

    # 👮 پیام کامل برای ادمین
    admin_message = (
        "📩 پیام ناشناس جدید\n\n"
        f"🆔 آیدی عددی: {user.id}\n"
        f"👤 یوزرنیم: @{username}\n\n"
        f"💬 متن پیام:\n{text}"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ پیامت ارسال شد.")
    except Exception as e:
        print("ERROR sending to admin:", e)
        await update.message.reply_text("❌ خطا در ارسال پیام.")

# ================== دکمه‌های ادمین ==================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split(":")
    user_id = int(user_id)

    if action == "reply":
        pending_replies[ADMIN_ID] = user_id
        await query.message.reply_text(
            "✍️ پاسخ خود را بنویسید:",
            reply_markup=ForceReply(selective=True)
        )

    elif action == "block":
        blocked_users.add(user_id)
        await query.message.reply_text(f"⛔ کاربر {user_id} مسدود شد.")

# ================== پاسخ ادمین ==================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    if update.effective_user.id != ADMIN_ID:
        return

    if ADMIN_ID not in pending_replies:
        return

    user_id = pending_replies.pop(ADMIN_ID)
    text = update.message.text

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📨 پاسخ ادمین:\n\n{text}"
        )
        await update.message.reply_text("✅ پاسخ ارسال شد.")
    except Exception as e:
        print("ERROR sending reply:", e)
        await update.message.reply_text("❌ خطا در ارسال پاسخ.")

# ================== اجرای برنامه ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # 👈 خیلی مهم: اول reply ادمین
    app.add_handler(MessageHandler(filters.REPLY, admin_reply))

    # 👈 بعد پیام کاربران
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))

    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
