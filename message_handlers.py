from pyrogram import Client
from pyrogram.types import Message
from start import clock
from client import bot
from pyrogram.filters import regex, private, command, successful_payment
from config import ADMIN_USERNAME, ADMIN_ID
from database import DBManager
from keyboards import get_keyboard
from texts import get_text
from pyrostates import set_state, del_state, at_state
from snippet_parser import extract_kavenegar_info

database = DBManager("gift_notifier.sqlite3")
data = {}


@bot.on_message(command("start") & private)
async def start_message_handler(_, message: Message):
    await message.reply(
        text="💎",
        reply_markup=get_keyboard("start_reply")
    )

    await message.reply(
        text=get_text("start").format(message.from_user.mention, clock.get_datetime()),
        reply_markup=get_keyboard("start_inline"),
        quote=True
    )


@bot.on_message(command("support") & regex("$👤 پشتیبانی^") & private)
async def support(_, message: Message):
    await message.reply(
        text=get_text("support").format(ADMIN_USERNAME),
        quote=True
    )


@bot.on_message(command("guide") & regex("$💡 راهنما^") & private)
async def guide(_, message: Message):
    await message.reply(
        text=get_text("guide"),
        quote=True
    )


@bot.on_message(command("info") & regex("^ℹ️ اطلاعات کاربر$") & private)
async def information(_, message: Message):
    user_id = message.from_user.id
    info = database.get_user(user_id)

    if info:
        user_id, receptor, token, sender, subscription_count = info
        await message.reply(
            text=get_text("info").format(user_id, receptor, sender, subscription_count, token, clock.get_datetime()),
            quote=True
        )
    else:
        await message.reply(
            text=get_text("user_not_found").format(message.from_user.mention, clock.get_datetime()),
            quote=True
        )


@bot.on_message(command("sub") &  regex("$🛒 تهیه اشتراک^") & private)
async def bye_subscription(_, message: Message):
    await message.reply(
        text=get_text("buy_subscription"),
        reply_markup=get_keyboard("cancel"),
        quote=True
    )
    set_state(message, "CODE_SNIPPET")


@bot.on_message(private & at_state("CODE_SNIPPET"))
async def receive_code_snippet(_, message: Message):
    global data

    user_id = message.from_user.id
    code_snippet = message.text
    kavenegar_info = extract_kavenegar_info(code_snippet)

    if kavenegar_info:
        data[user_id] = kavenegar_info
        await message.reply(
            text=get_text("ask_subscription_count"),
            reply_markup=get_keyboard("select_subscription_count"),
            quote=True
        )
        del_state(message)
    else:
        await message.reply(
            text=get_text("invalid_code_snippet"),
            quote=True
        )


@bot.on_message(successful_payment)
async def successful_payment_handler(client: Client, message):
    global data
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload

    if payload.startswith("subscription_sub_"):
        sub_type = int(payload.replace("subscription_sub_", ""))

        token, sender, receptor = data[user_id]
        database.add_user(user_id, receptor, sender, token, sub_type)

        await message.reply("✅")
        await message.reply(
            text=get_text("payment_success").format(sub_type),
            quote=True
        )

        await client.send_message(
            chat_id=ADMIN_ID,
            text=get_text("payment_notification").format(message.from_user.mention, sub_type)
        )
        del data[user_id]


@bot.on_pre_checkout_query()
async def pre_checkout_handler(client: Client, pre_checkout_query):
    await pre_checkout_query.answer(ok=True)
