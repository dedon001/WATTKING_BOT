import os
import re
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# =========================
# SETTINGS
# =========================

TOKEN = os.getenv("TOKEN")

GROUP_USERNAME = "@wattkingsactiveengagementgroup"

POST_TOPIC_ID = 1103

AUTO_MESSAGE = "Drop Your Links and Engage in Others"

AUTO_MESSAGE_INTERVAL = 90

counter = 1
last_auto_message_id = None


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 Join Group 🔥",
                url="https://t.me/wattkingsactiveengagementgroup"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = """
🔥 Welcome to WATTKINGS ACTIVE GROUP 🔥

✅ Drop your X links
✅ Engage in others
✅ Grow together
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

    try:

        msg = await context.bot.send_message(
            chat_id=GROUP_USERNAME,
            message_thread_id=POST_TOPIC_ID,
            text=AUTO_MESSAGE
        )

        # DELETE OLD MESSAGE
        if last_auto_message_id:

            try:
                await context.bot.delete_message(
                    chat_id=GROUP_USERNAME,
                    message_id=last_auto_message_id
                )

            except:
                pass

        last_auto_message_id = msg.message_id

    except Exception as e:
        print(f"AUTO MESSAGE ERROR: {e}")


# =========================
# X LINK FORMATTER
# =========================

async def x_formatter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global counter

    if not update.message:
        return

    text = update.message.text or ""

    x_patterns = [
        "x.com/",
        "twitter.com/"
    ]

    if not any(pattern in text.lower() for pattern in x_patterns):
        return

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    # DELETE ORIGINAL MESSAGE
    try:
        await update.message.delete()
    except:
        pass

    formatted = f"""#{counter}

{username}

{text}

❤️
"""

    await context.bot.send_message(
        chat_id=GROUP_USERNAME,
        message_thread_id=POST_TOPIC_ID,
        text=formatted
    )

    counter += 1


# =========================
# MAIN
# =========================

def main():

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # START COMMAND
    app.add_handler(
        CommandHandler("start", start)
    )

    # X LINK FORMATTER
    app.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            x_formatter
        )
    )

    # AUTO MESSAGE LOOP
    app.job_queue.run_repeating(
        auto_post,
        interval=AUTO_MESSAGE_INTERVAL,
        first=10
    )

    print("🔥 WATTKING BOT RUNNING...")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()