import os
import sqlite3
import re
import asyncio

from datetime import time

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
    filters
)

print("=" * 50)
print("RUNNING BOT_V2")
print("=" * 50)

TOKEN = "8704508925:AAF3Y78zAWI4Clmhw09mwUocM-8vZLcsfz8"

print("BOT TOKEN FOUND:", bool(TOKEN))

GROUP_ID = -1003337623917

TOPICS = {
    1103: {
        "name": "5 Engagements",
        "emoji": "🔥",
        "counter_key": "topic_1103",
    },
    1107: {
        "name": "15 Engagements",
        "emoji": "🔥",
        "counter_key": "topic_1107",
    },
    19381: {
        "name": "10 Likes",
        "emoji": "❤️",
        "counter_key": "topic_19381",
    },
}

COOLDOWNS = {
    1103: 5,
    1107: 15,
    19381: 10
}

DB_FILE = "database.db"

AUTO_TOPIC = 1107
AUTO_MESSAGE = "📢 Drop Your Link And Engage In Other Previous Links"

last_auto_message_id = None

# =========================
# DATABASE
# =========================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS counters (
        topic_id INTEGER PRIMARY KEY,
        current_number INTEGER NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_cooldowns (
        user_id INTEGER,
        topic_id INTEGER,
        last_post_number INTEGER,
        PRIMARY KEY (user_id, topic_id)
    )
    """)

    for topic_id in TOPICS:
        cur.execute(
            """
            INSERT OR IGNORE INTO counters
            (topic_id, current_number)
            VALUES (?, ?)
            """,
            (topic_id, 1)
        )

    conn.commit()
    conn.close()


def get_counter(topic_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "SELECT current_number FROM counters WHERE topic_id=?",
        (topic_id,)
    )

    row = cur.fetchone()

    conn.close()

    return row[0] if row else 1


def increment_counter(topic_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    current = get_counter(topic_id)

    cur.execute(
        """
        UPDATE counters
        SET current_number=?
        WHERE topic_id=?
        """,
        (current + 1, topic_id)
    )

    conn.commit()
    conn.close()

    return current

def get_user_cooldown(user_id, topic_id):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT last_post_number
        FROM user_cooldowns
        WHERE user_id=? AND topic_id=?
        """,
        (user_id, topic_id)
    )

    row = cur.fetchone()

    conn.close()

    return row[0] if row else None

def save_user_cooldown(user_id, topic_id, post_number):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO user_cooldowns
        (user_id, topic_id, last_post_number)
        VALUES (?, ?, ?)
        """,
        (user_id, topic_id, post_number)
    )

    conn.commit()
    conn.close()

# =========================
# X LINK HANDLER
# =========================

async def x_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    topic_id = update.message.message_thread_id

    if topic_id not in TOPICS:
        return

    text = update.message.text or ""

    if not (
        "x.com/" in text.lower()
        or "twitter.com/" in text.lower()
    ):
        return
    # Convert Topic 19381 links into X Like links

    if topic_id == 19381:

     match = re.search(
        r"/status/(\d+)",
        text
    )

    if match:

        tweet_id = match.group(1)

        text = (
            f"https://x.com/intent/like?tweet_id={tweet_id}"
        )

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    required_gap = COOLDOWNS[topic_id]

    last_post = get_user_cooldown(
    user.id,
    topic_id
    )

    current_number = get_counter(topic_id)

    if last_post is not None:

     if current_number - last_post < required_gap:

        try:
            await update.message.delete()
        except:
            pass

        warning = await context.bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=topic_id,
            text=f"⚠️ Wait for {required_gap} links before you drop another link"
        )

        await asyncio.sleep(10)

        try:
            await context.bot.delete_message(
                chat_id=GROUP_ID,
                message_id=warning.message_id
            )
        except:
            pass

        return

    try:
        await update.message.delete()
    except:
        pass

    number = increment_counter(topic_id)

    save_user_cooldown(
        user.id,
        topic_id,
        number
    )

    emoji = TOPICS[topic_id]["emoji"]

    formatted = f"""{emoji} #{number}

👤 {username}

🔗 {text}
"""

    posted = await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=topic_id,
        text=formatted
    )

    warning_text = None

    if topic_id == 1103:
        warning_text = "⚠️ Make sure to Engage previous 5 links"

    elif topic_id == 1107:
        warning_text = "⚠️ Make sure to Engage previous 15 links"

    elif topic_id == 19381:
        warning_text = "⚠️ Make sure to Engage (Like) previous 10 links"

    if warning_text:

     warning = await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=topic_id,
        text=warning_text
    )

    import asyncio

    await asyncio.sleep(10)

    try:
        await context.bot.delete_message(
            chat_id=GROUP_ID,
            message_id=warning.message_id
        )
    except:
        pass

async def auto_post(context: ContextTypes.DEFAULT_TYPE):

    global last_auto_message_id

    try:

        if last_auto_message_id:

            try:
                await context.bot.delete_message(
                    chat_id=GROUP_ID,
                    message_id=last_auto_message_id
                )
            except:
                pass

        msg = await context.bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=1107,
            text="📢 Drop Your Link And Engage In Other Previous Links"
        )

        last_auto_message_id = msg.message_id

    except Exception as e:
        print("AUTO MESSAGE ERROR:", e)

async def reset_counters(context: ContextTypes.DEFAULT_TYPE):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    for topic_id in TOPICS:
        cur.execute(
            """
            UPDATE counters
            SET current_number=1
            WHERE topic_id=?
            """,
            (topic_id,)
        )

    cur.execute(
        "DELETE FROM user_cooldowns"
    )

    conn.commit()
    conn.close()

    print("COUNTERS RESET TO 1")

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

    text = """
🔥 Welcome to WATTKINGS ACTIVE GROUP 🔥

✅ Drop your X links
✅ Follow topic rules
✅ Stay active
"""

    await update.message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================

# MAIN

# =========================

def main():

    print("RUNNING init_db()")
    init_db()
    print("init_db() FINISHED")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.job_queue.run_repeating(
        auto_post,
        interval=80,
        first=10
    )

    app.job_queue.run_daily(
        reset_counters,
        time=time(hour=1, minute=0)
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            x_link_handler
        )
    )

    print("🔥 WATTKINGS BOT V2 STARTING...")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
