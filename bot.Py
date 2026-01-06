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

# آی‌دی عددی ادمین (با @userinfobot بگیر)
ADMIN_ID = 8044612620  # ← اینو عوض کن

# ================== متغیرها ==================

blocked_users = set()
pending_replies = {}  # admin_id -> user_id

# ================== /start ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    user = update.effective_user
    if user.id in blocked_users:
        return

    await update.message.reply_text(
        "سلام ❤️\n"
        "پیامت رو بفرست تا به صورت ناشناس برای ادمین ارسال بشه."
    )

# ================== پیام کاربر ==================

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    user = update.effective_user

    # ❌ اگر خود ادمین است، این تابع اجرا نشود
    if user.id == ADMIN_ID:
        return

    if user.id in blocked_users:
        return

    text = update.message.text
    username = user.username or "NoUsername"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ پاسخ", callback_data=f"reply:{user.id}"),
            InlineKeyboardButton("⛔ مسدود", callback_data=f"block:{user.id}")
        ]
    ])

    msg = (
        "📩 پیام جدید\n\n"
        f"👤 یوزرنیم: @{username}\n"
        f"🆔 آیدی: {user.id}\n\n"
        f"💬 متن پیام:\n{text}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=msg,
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ پیامت ارسال شد.")
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

app.add_handler(CommandHandler("start", start))

# 👈 اول پاسخ ادمین
app.add_handler(MessageHandler(filters.REPLY, admin_reply))

# 👈 بعد پیام کاربران
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))

app.add_handler(CallbackQueryHandler(button_handler))
        )
        await update.message.reply_text("✅ پاسخ ارسال شد.")
    except Exception as e:
        print("ERROR sending reply:", e)
        await update.message.reply_text("❌ خطا در ارسال پاسخ.")

# ================== اجرای برنامه ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.REPLY, admin_reply))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
