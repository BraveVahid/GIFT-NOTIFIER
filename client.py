from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client(
    name="GIFT-MONITOR",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)
