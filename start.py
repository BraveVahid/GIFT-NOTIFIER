from monitoring import Monitoring
from pyrogram import Client
from client import bot
from database import DBManager
from clock import IranClock
import callback_handlers
import message_handlers

clock = IranClock()

@bot.on_start()
async def init_bot(client: Client):
    print("init_bot")
    DBManager("gift_notifier.sqlite3")
    await Monitoring.initialize(client)
    await Monitoring.start_monitoring(client)

bot.run()
