from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ForceReply
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

# ================== تنظیمات ==================
ADMIN_ID = 5046852230  # آیدی عددی شما
# ============================================

blocked_users = set()
pending_replies = {}  # admin_id -> user_id


# --------- شروع ---------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id in blocked_users:
        return

    await update.message.reply_text(
        "سلام ❤️.\n"
        "پیام ناشناسی که میخوای براش بفرستی رو اینجا تایپ کن و منتظر باش تا همینجا جوابتو بده 🤝"
    )


# --------- پیام کاربران ---------
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # جلوگیری از پردازش پیام مدیر
    if user.id == ADMIN_ID:
        return

    if user.id in blocked_users:
        return

    text = update.message.text
    username = user.username or "NoUsername"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user.id}"),
            InlineKeyboardButton("⛔ مسدود کردن", callback_data=f"block:{user.id}")
        ]
    ])

    msg = (
        f"📩 پیام جدید\n\n"
        f"👤 یوزرنیم: @{username}\n"
        f"🆔 آیدی: {user.id}\n\n"
        f"✉️ متن پیام:\n{text}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=msg,
        reply_markup=keyboard
    )

    await update.message.reply_text("پیام شما به صورت ناشناس ارسال شد✅")


# --------- دکمه‌های مدیر ---------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split(":")
    user_id = int(user_id)

    if action == "reply":
        pending_replies[ADMIN_ID] = user_id

        await query.message.reply_text(
            "پاسخ خود را بنویسید:",
            reply_markup=ForceReply(selective=True)
        )

    elif action == "block":
        blocked_users.add(user_id)

        await query.message.reply_text(
            f"⛔ کاربر {user_id} مسدود شد."
        )


# --------- پاسخ مدیر ---------
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if ADMIN_ID not in pending_replies:
        return

    user_id = pending_replies.pop(ADMIN_ID)
    text = update.message.text

    await context.bot.send_message(
        chat_id=user_id,
        text=f"✉️ پاسخ پیامت:\n\n{text}"
    )

    await update.message.reply_text("✅ پاسخ ارسال شد.")


# --------- اجرای ربات ---------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # ابتدا پاسخ مدیر بررسی شود
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, admin_reply))

    # سپس پیام کاربران
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))

    # دکمه‌ها
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()


