from pyrogram import Client
from client import bot
from pyrogram.types import CallbackQuery
from pyrostates import at_state, del_state
from pyrogram.filters import regex

from keyboards import get_keyboard
from texts import get_text


@bot.on_callback_query(at_state("CODE_SNIPPET") & regex("cancel"))
async def cancel(_, callback_query: CallbackQuery):
    await callback_query.answer(
        get_text("cancel"),
        show_alert=True
    )
    await callback_query.message.delete()
    del_state(callback_query)


@bot.on_callback_query(regex("sub_(1|5|7|10)"))
async def receive_subscription_count(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data


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

    await callback.message.delete()
    await client.send_invoice(
        chat_id=user_id,
        title="خرید اشتراک",
        description=descriptions[data],
        payload=f"subscription_{data}",
        provider_token="",
        currency="XTR",
        prices=[{"label": "Subscription", "amount": prices[data]}],
        reply_markup=get_keyboard("pay")
    )
    await callback.answer("در حال ایجاد صورتحساب...")
