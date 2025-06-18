from config import ADMIN_ID
from database import DBManager
import asyncio
from sender import SmsSender

database = DBManager()

class Monitoring:
    @staticmethod
    async def detector(client):
        try:
            current_gifts = [gift.id for gift in await client.get_available_gifts() if
                             gift.is_limited and not gift.is_sold_out]
            last_gift_list = database.get_all_gifts()

            new_gifts = []
            for gift_id in current_gifts:
                if gift_id not in last_gift_list:
                    new_gifts.append(gift_id)

            if new_gifts:
                for gift_id in new_gifts:
                    database.add_gift(gift_id)
                return new_gifts
            return []
        except Exception as e:
            return []

    @staticmethod
    async def initialize(client):
        try:
            available_gifts = await client.get_available_gifts()
            for gift in available_gifts:
                if gift.is_limited and not gift.is_sold_out:
                    database.add_gift(gift.id)
        except Exception as e:
            pass

    @staticmethod
    async def start_monitoring(app):
        iteration_count = 0
        while True:
            iteration_count += 1
            if iteration_count == 120:
                await app.send_message(text="Checking for gifts...", chat_id=ADMIN_ID)
                iteration_count = 0
            try:
                new_gifts = await Monitoring.detector(app)

                if new_gifts:
                    for gift_id in new_gifts:
                        try:
                            await SmsSender.send_sms(f"New gift available: {gift_id}", app)
                        except Exception as e:
                            pass
                await asyncio.sleep(30)

            except Exception as e:
                await asyncio.sleep(30)
