import telebot
from telebot import types

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8766337619  # o'zingni ID
CHANNEL_ID = -1003958075206

# msg_id -> data storage
pending = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Nima darding bor gapir")

# ================= USER MESSAGE =================
@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def handle(message):
    try:
        if message.from_user.id == ADMIN_ID:
            return

        msg_id = message.message_id

        pending[msg_id] = {
            "message": message,
            "user_id": message.from_user.id
        }

        user = message.from_user

        text = message.text if message.content_type == "text" else "[media]"

        admin_text = f"""
👤 USER:
Name: {user.first_name}
Username: @{user.username if user.username else 'yo‘q'}
ID: {user.id}

📩 Xabar:
{text}
"""

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Yuborish", callback_data=f"send_{msg_id}"),
            types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{msg_id}")
        )

        bot.send_message(ADMIN_ID, admin_text, reply_markup=markup)

    except Exception as e:
        print("ERROR:", e)

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        data = call.data

        # ================= SEND =================
        if data.startswith("send_"):
            msg_id = int(data.split("_")[1])
            item = pending.get(msg_id)

            if item:
                message = item["message"]
                user_id = item["user_id"]

                # TEXT
                if message.content_type == "text":
                    bot.send_message(CHANNEL_ID, message.text)

                # PHOTO
                elif message.content_type == "photo":
                    bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=message.caption or "")

                # VIDEO
                elif message.content_type == "video":
                    bot.send_video(CHANNEL_ID, message.video.file_id, caption=message.caption or "")

                # DOCUMENT
                elif message.content_type == "document":
                    bot.send_document(CHANNEL_ID, message.document.file_id, caption=message.caption or "")

                # ADMIN CONFIRM
                bot.send_message(ADMIN_ID, "✅ Kanalga yuborildi")

                # USER NOTIFY
                bot.send_message(user_id, "✅Bold Hal Jiyan😎")

                pending.pop(msg_id, None)

        # ================= REJECT =================
        elif data.startswith("reject_"):
            msg_id = int(data.split("_")[1])
            item = pending.get(msg_id)

            if item:
                user_id = item["user_id"]

                bot.send_message(user_id, "❌Endi Chichvording Jiyan😂")
                bot.send_message(ADMIN_ID, "❌ Xabar rad etildi")

                pending.pop(msg_id, None)

        bot.answer_callback_query(call.id)

    except Exception as e:
        print("CALLBACK ERROR:", e)

# ================= RUN =================
bot.polling()