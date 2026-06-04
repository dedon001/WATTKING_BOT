import os
import sqlite3
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

DB_FILE = "database.db"

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

    number = increment_counter(topic_id)

    emoji = TOPICS[topic_id]["emoji"]

    formatted = f"""{emoji} #{number}

👤 {username}

🔗 {text}
"""

    await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=topic_id,
        text=formatted
    )


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

init_db()

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
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