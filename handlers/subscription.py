from pyrogram.filters import regex, private, successful_payment
from pyrogram.types import LabeledPrice
from pyrostates import at_state, del_state, set_state
from database import DBManager
from client import bot
from utils.texts import get_text
from utils.keyboards import get_keyboard
from utils.user_state import UserData
from utils.snippet_parser import extract_kavenegar_info
from config import ADMIN_ID

user_data = dict()
database = DBManager("gift_notifier.sqlite3")


@bot.on_message(regex(r"^🛒 تهیه اشتراک$") & private)
async def buy_subscription(_, message):
    if database.get_user(message.from_user.id):
        await message.reply(
            text=get_text("user_has_sub"),
            quote=True
        )
    else:
        await message.reply(
            text=get_text("buy_subscription"),
            reply_markup=get_keyboard("cancel"),
            quote=True
        )
        set_state(message, "CODE_SNIPPET")

@bot.on_message(private & at_state("CODE_SNIPPET"))
async def receive_code_snippet(_, message):
    global user_data

    user_id = message.from_user.id
    code_snippet = message.text
    kavenegar_info = extract_kavenegar_info(code_snippet)

    if all(kavenegar_info):
        receptor, sender, token = kavenegar_info
        user_data[user_id] = UserData(receptor=receptor, sender=sender, token=token)
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

@bot.on_callback_query(regex(r"sub_(1|5|7|10)"))
async def receive_subscription_count(client, callback_query):
    user_id = callback_query.from_user.id
    callback_data = callback_query.data.split("_")[1]

    prices = {
        "1": 30,
        "5": 150,
        "7": 210,
        "10": 270
    }

    user = user_data[user_id]
    token, sender, receptor = user.sender, user.receptor, user.token

    try:
        await callback_query.message.delete()

        price_list = [LabeledPrice(
            label="Subscription",
            amount=prices[callback_data]
        )]

        await client.send_invoice(
            chat_id=user_id,
            title=f"GIFT NOTIFIER: BUY SUBSCRIPTION",
            description=get_text("description").format(receptor, sender, callback_data, callback_data),
            payload=f"subscription_{callback_data}",
            provider_token="",
            currency="XTR",
            prices=price_list,
            reply_markup=get_keyboard("pay"),
            reply_to_message_id=callback_query.message.reply_to_message_id
        )
        await callback_query.answer("در حال ایجاد صورتحساب...")
    except Exception as e:
        await callback_query.answer("خطا در ایجاد صورتحساب!", show_alert=True)
        print(f"Error creating invoice: {e}")


@bot.on_message(successful_payment)
async def successful_payment_handler(client, message):
    global user_data
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload

    if payload.startswith("subscription_sub_"):
        sub_count_str = payload.replace("subscription_sub_", "")
        sub_type = int(sub_count_str)

        if user_id in user_data:
            user = user_data[user_id]
            token, sender, receptor = user.sender, user.receptor, user.token
            if database.add_user(user_id, receptor, sender, token, sub_type):
                await message.reply("🎉")
                await message.reply(
                    text=get_text("payment_success").format(sub_type),
                    quote=True
                )

                await client.send_message(
                    chat_id=ADMIN_ID,
                    text=get_text("payment_notification").format(message.from_user.mention, sub_type)
                )
            else:
                await message.reply("❌ خطا در ثبت اطلاعات کاربر!")
            del user_data[user_id]
        else:
            await message.reply("❌ اطلاعات کاربر یافت نشد!")

@bot.on_pre_checkout_query()
async def pre_checkout_handler(_, pre_checkout_query):
    await pre_checkout_query.answer(ok=True)


@bot.on_callback_query(at_state("CODE_SNIPPET") & regex("cancel"))
async def cancel(client, callback_query):
    await client.send_message(
        text=get_text("cancel"),
        chat_id=callback_query.from_user.id,
        reply_to_message_id=callback_query.message.reply_to_message_id
    )
    await callback_query.message.delete()
    del_state(callback_query)


@bot.on_callback_query(regex(r"cancel_pay"))
async def cancel_pay(client, callback_query):
    await callback_query.message.delete()
    await client.send_message(
        text=get_text("cancel"),
        reply_to_message_id=callback_query.message.reply_to_message_id,
        chat_id=callback_query.from_user.id
    )
