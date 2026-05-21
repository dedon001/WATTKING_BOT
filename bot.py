import re
import asyncio
import aiosqlite
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# =========================
# BOT SETTINGS
# =========================

TOKEN = "8704508925:AAGFdyw1b3X3Nvq0hZOr3SiOoBKwVyBppAM"

GROUP_LINK = "https://t.me/wattkingsactiveengagementgroup"

POST_TOPIC_ID = 1103

AUTO_MESSAGE = "Drop Your Links and Engage in Others"

AUTO_MESSAGE_TIME = 90  # 1 minute 30 seconds

counter = 1

last_auto_message_id = None

# =========================
# DATABASE
# =========================

DB_NAME = "database.db"


async def setup_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
        """)
        await db.commit()


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "Join Group 🚀",
                url=GROUP_LINK
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""
🔥 Welcome to WATTKINGS ACTIVE ENGAGEMENT 🔥

You are now connected to the engagement system.

✅ Drop your X links
✅ Engage in others
✅ Grow together

Click below to join the group.
"""

    await update.message.reply_text(
        text=text,
        reply_markup=reply_markup
    )


# =========================
# AUTO MESSAGE
# =========================

async def auto_post(context: ContextTypes.DEFAULT_TYPE):

    global last_auto_message_id

    bot = context.bot

    try:

        msg = await bot.send_message(
            chat_id="@wattkingsactiveengagementgroup",
            message_thread_id=POST_TOPIC_ID,
            text=AUTO_MESSAGE
        )

        new_message_id = msg.message_id

        await asyncio.sleep(5)

        if last_auto_message_id:
            try:
                await bot.delete_message(
                    chat_id="@wattkingsactiveengagementgroup",
                    message_id=last_auto_message_id
                )
            except:
                pass

        last_auto_message_id = new_message_id

    except Exception as e:
        print("AUTO POST ERROR:", e)


# =========================
# X LINK DETECTOR
# =========================

def contains_x_link(text):

    patterns = [
        r"x\.com\/",
        r"twitter\.com\/"
    ]

    for pattern in patterns:
        if re.search(pattern, text.lower()):
            return True

    return False


# =========================
# NUMBERING SYSTEM
# =========================

async def handle_x_links(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global counter

    if not update.message:
        return

    if not update.message.text:
        return

    text = update.message.text

    if not contains_x_link(text):
        return

    user = update.effective_user

    username = user.username if user.username else "NoUsername"

    first_name = user.first_name

    try:
        await update.message.delete()
    except:
        pass

    formatted = f"""#{counter}

@{username} || X {first_name}

{text}
"""

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        message_thread_id=POST_TOPIC_ID,
        text=formatted
    )

    counter += 1


# =========================
# MAIN
# =========================

async def main():

    await setup_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_x_links
        )
    )

    job_queue = app.job_queue

    job_queue.run_repeating(
        auto_post,
        interval=AUTO_MESSAGE_TIME,
        first=10
    )

    print("WATTKING BOT IS RUNNING...")

    app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())