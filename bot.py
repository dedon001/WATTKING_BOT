import re
import asyncio
import aiosqlite

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
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

TOKEN = "8704508925:AAHyaCnfxqWRydWDiwkbN4a65VafFOjNGN4"

GROUP_LINK = "https://t.me/wattkingsactiveengagementgroup"

POST_TOPIC_ID = 1103

AUTO_MESSAGE = "Drop Your Links and Engage in Others"

WARN_LIMIT = 3

counter = 1
last_auto_message_id = None


# =========================
# DATABASE
# =========================

async def setup_database():

    async with aiosqlite.connect("database.db") as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS warns (
            user_id INTEGER PRIMARY KEY,
            warns INTEGER DEFAULT 0
        )
        """)

        await db.commit()


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🔥 Welcome to WATTKINGS ACTIVE GROUP 🔥

You are now part of the engagement network.

✅ Drop your X links
✅ Engage with others
✅ Grow together

Use the button below to join the group.
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 Join Group 🔥",
                url=GROUP_LINK
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=text,
        reply_markup=reply_markup
    )


# =========================
# AUTO MESSAGE
# =========================

async def auto_drop(context: ContextTypes.DEFAULT_TYPE):

    global last_auto_message_id

    try:

        # SEND NEW MESSAGE FIRST
        msg = await context.bot.send_message(
            chat_id=context.job.chat_id,
            message_thread_id=POST_TOPIC_ID,
            text=AUTO_MESSAGE
        )

        # DELETE OLD MESSAGE AFTER
        if last_auto_message_id:

            try:
                await context.bot.delete_message(
                    chat_id=context.job.chat_id,
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

    message = update.message

    if not message:
        return

    text = message.text or ""

    x_pattern = r"(https?://(x|twitter)\.com/\S+)"

    match = re.search(x_pattern, text)

    if match:

        x_link = match.group(1)

        tg_username = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else message.from_user.first_name
        )

        # DELETE ORIGINAL MESSAGE
        try:
            await message.delete()
        except:
            pass

        formatted = f"""
#{counter}

{tg_username}

{x_link}

❤️
"""

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            message_thread_id=POST_TOPIC_ID,
            text=formatted
        )

        counter += 1


# =========================
# @ALL COMMAND
# =========================

async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    admins = await context.bot.get_chat_administrators(
        update.effective_chat.id
    )

    admin_ids = [admin.user.id for admin in admins]

    if update.effective_user.id not in admin_ids:
        return

    members_text = "@all\n\n"

    try:

        async for member in context.bot.get_chat(
            update.effective_chat.id
        ):
            pass

    except:
        pass

    members_text += "Everyone please check the group."

    await update.message.reply_text(members_text)


# =========================
# MUTE COMMAND
# =========================

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    admins = await context.bot.get_chat_administrators(
        update.effective_chat.id
    )

    admin_ids = [admin.user.id for admin in admins]

    if update.effective_user.id not in admin_ids:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Reply to a user to mute them."
        )
        return

    target = update.message.reply_to_message.from_user

    permissions = ChatPermissions(
        can_send_messages=False
    )

    await context.bot.restrict_chat_member(
        chat_id=update.effective_chat.id,
        user_id=target.id,
        permissions=permissions
    )

    await update.message.reply_text(
        f"{target.first_name} has been muted."
    )


# =========================
# WARN COMMAND
# =========================

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    admins = await context.bot.get_chat_administrators(
        update.effective_chat.id
    )

    admin_ids = [admin.user.id for admin in admins]

    if update.effective_user.id not in admin_ids:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Reply to a user to warn them."
        )
        return

    target = update.message.reply_to_message.from_user

    async with aiosqlite.connect("database.db") as db:

        cursor = await db.execute(
            "SELECT warns FROM warns WHERE user_id=?",
            (target.id,)
        )

        row = await cursor.fetchone()

        if row:
            warns = row[0] + 1

            await db.execute(
                "UPDATE warns SET warns=? WHERE user_id=?",
                (warns, target.id)
            )

        else:
            warns = 1

            await db.execute(
                "INSERT INTO warns (user_id, warns) VALUES (?, ?)",
                (target.id, warns)
            )

        await db.commit()

    await update.message.reply_text(
        f"{target.first_name} now has {warns} warn(s)."
    )

    # AUTO MUTE AFTER LIMIT
    if warns >= WARN_LIMIT:

        permissions = ChatPermissions(
            can_send_messages=False
        )

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            permissions=permissions
        )

        await update.message.reply_text(
            f"{target.first_name} has been auto-muted after {WARN_LIMIT} warns."
        )


# =========================
# MAIN
# =========================

async def main():

    await setup_database()

    app = ApplicationBuilder().token(TOKEN).build()

    # START
    app.add_handler(
        CommandHandler("start", start)
    )

    # MUTE
    app.add_handler(
        CommandHandler("mute", mute)
    )

    # WARN
    app.add_handler(
        CommandHandler("warn", warn)
    )

    # @ALL
    app.add_handler(
        CommandHandler("all", all_command)
    )

    # X FORMATTER
    app.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            x_formatter
        )
    )

    # AUTO MESSAGE EVERY 2 MINUTES
    app.job_queue.run_repeating(
        auto_drop,
        interval=90,
        first=10,
        chat_id="@wattkingsactiveengagementgroup"
    )

    print("🔥 WATTKING BOT IS RUNNING...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()


# =========================
# RUN BOT
# =========================

if __name__ == "__main__":

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(main())