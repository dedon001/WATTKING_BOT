import re
import asyncio
import os
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
# SETTINGS
# =========================

TOKEN = "8704508925:AAGFdyw1b3X3Nvq0hZOr3SiOoBKwVyBppAM"

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

        # DELETE OLD MESSAGE AFTER NEW ONE SENDS
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
        print("AUTO MESSAGE ERROR:", e)


# =========================
# X LINK FORMATTER
# =========================

async def x_formatter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global counter

    if not update.message:
        return

    text = update.message.text or ""

    patterns = [
        "x.com/",
        "twitter.com/"
    ]

    if not any(p in text.lower() for p in patterns):
        return

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    try:
        await update.message.delete()
    except:
        pass

    formatted = f"""
#{counter}

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

    app = ApplicationBuilder().token(TOKEN).build()

    # START COMMAND
    app.add_handler(
        CommandHandler("start", start)
    )

    # X FORMATTER
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

    print("🔥 WATTKING BOT IS RUNNING...")

    app.run_polling()


# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
    main()