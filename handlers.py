from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from clock import IranClock
from pyrogram.filters import regex, private, command, successful_payment, group
from config import ADMIN_USERNAME, ADMIN_ID
from database import DBManager
from keyboards import get_keyboard
from texts import get_text
from pyrostates import set_state, del_state, at_state
from snippet_parser import extract_kavenegar_info
from config import API_HASH, API_ID, BOT_TOKEN

bot = Client(
    name="GIFT-MONITOR",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

clock = IranClock()
data = {}
database = DBManager("gift_notifier.sqlite3")


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


@bot.on_message(regex(r"^👤 پشتیبانی$") & private)
async def support(_, message: Message):
    await message.reply(
        text=get_text("support").format(ADMIN_USERNAME),
        quote=True
    )


@bot.on_message(regex(r"^💡 راهنما$") & private)
async def guide(_, message: Message):
    await message.reply(
        text=get_text("guide"),
        quote=True
    )


@bot.on_message(regex(r"^ℹ️ اطلاعات کاربر$") & private)
async def information(_, message: Message):
    user_id = message.from_user.id
    info = database.get_user(user_id)

    if info:
        user_id_db, receptor, token, sender, subscription_count = info[1:6]
        await message.reply(
            text=get_text("info").format(user_id_db, receptor, sender, subscription_count,
                                       "فعال" if subscription_count > 0 else "غیرفعال", token, clock.get_datetime()),
            quote=True
        )
    else:
        await message.reply(
            text=get_text("user_not_found").format(message.from_user.mention, clock.get_datetime()),
            quote=True
        )


@bot.on_message(regex(r"^🛒 تهیه اشتراک$") & private)
async def buy_subscription(_, message: Message):
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

    if all(kavenegar_info):
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
        sub_count_str = payload.replace("subscription_sub_", "")
        sub_type = int(sub_count_str)

        if user_id in data:
            token, sender, receptor = data[user_id]
            success = database.add_user(user_id, receptor, sender, token, sub_type)

            if success:
                await message.reply("✅")
                await message.reply(
                    text=get_text("payment_success").format(sub_type),
                    quote=True
                )

                await client.send_message(
                    chat_id=ADMIN_ID,
                    text=get_text("payment_notification").format(message.from_user.mention, sub_type)
                )
            else:
                await message.reply("❌ خطا در ثبت اطلاعات کاربر")

            del data[user_id]
        else:
            await message.reply("❌ اطلاعات کاربر یافت نشد")


@bot.on_pre_checkout_query()
async def pre_checkout_handler(_, pre_checkout_query):
    await pre_checkout_query.answer(ok=True)


@bot.on_callback_query(at_state("CODE_SNIPPET") & regex("cancel"))
async def cancel(_, callback_query: CallbackQuery):
    await callback_query.answer(
        get_text("cancel"),
        show_alert=True
    )
    await callback_query.message.delete()
    del_state(callback_query)


@bot.on_callback_query(regex(r"sub_(1|5|7|10)"))
async def receive_subscription_count(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    callback_data = callback.data

    prices = {
        "sub_1": 30,
        "sub_5": 150,
        "sub_7": 210,
        "sub_10": 270
    }

    descriptions = {
        "sub_1": "اشتراک برای 1 بار",
        "sub_5": "اشتراک برای 5 بار",
        "sub_7": "اشتراک برای 7 بار",
        "sub_10": "اشتراک برای 10 بار"
    }

    try:
        await callback.message.delete()
        await client.send_invoice(
            chat_id=user_id,
            title="خرید اشتراک",
            description=descriptions[callback_data],
            payload=f"subscription_{callback_data}",
            provider_token="284685532:TEST:M2JkZDMwZjk5NWJl",
            currency="XTR",
            prices=[{"label": "Subscription", "amount": 1}],
            reply_markup=get_keyboard("pay")
        )
        await callback.answer("در حال ایجاد صورتحساب...")
    except Exception as e:
        await callback.answer("خطا در ایجاد صورتحساب!", show_alert=True)


@bot.on_message(group)
async def get_groups(client: Client, message: Message):
    chat_id = message.chat.id
    chat_username = message.chat.username
    if database.add_group(chat_id):
        await client.send_message(
            text=f"**ربات عضو گروه {chat_username} شد!**",
            chat_id=ADMIN_ID
        )

#
# @bot.on_start()
# async def start(client: Client):
#     await Monitoring.initialize(client)
#     await Monitoring.start_monitoring(client)

if __name__ == "__main__":
    bot.run()
