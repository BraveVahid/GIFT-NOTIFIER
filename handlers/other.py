from utils.clock import IranClock
from pyrogram.filters import regex, private, command, group
from config import ADMIN_USERNAME, ADMIN_ID
from database import DBManager
from utils.keyboards import get_keyboard
from utils.texts import get_text
from client import bot

clock = IranClock()
database = DBManager("gift_notifier.sqlite3")


@bot.on_message(command("start") & private)
async def start_message_handler(_, message):
    await message.reply(
        text="💎",
        reply_markup=get_keyboard("start_reply")
    )

    await message.reply(
        text=get_text("start").format(message.from_user.mention, clock.get_datetime()),
        reply_markup=get_keyboard("start_inline"),
        quote=True
    )


@bot.on_message(regex(r"^👤 پشتیبانی$") & private)
async def support(_, message):
    await message.reply(
        text=get_text("support").format(ADMIN_USERNAME),
        quote=True
    )


@bot.on_message(regex(r"^💡 راهنما$") & private)
async def guide(_, message):
    await message.reply(
        text=get_text("guide"),
        quote=True
    )


@bot.on_message(regex(r"^ℹ️ اطلاعات کاربر$") & private)
async def information(_, message):
    info = database.get_user(message.from_user.id)

    if info:
        user_id, receptor, token, sender, subscription_count = info[1:6]
        await message.reply(
            text=get_text("info").format(user_id, receptor, sender, subscription_count, token, clock.get_datetime()),
            quote=True
        )
    else:
        await message.reply(
            text=get_text("user_not_found").format(message.from_user.mention, clock.get_datetime()),
            quote=True
        )


@bot.on_message(group)
async def get_groups(client, message):
    chat_id = message.chat.id
    chat_username = message.chat.username
    if database.add_group(chat_id):
        await client.send_message(
            text=f"**ربات عضو گروه {chat_username} شد!**",
            chat_id=ADMIN_ID
        )
