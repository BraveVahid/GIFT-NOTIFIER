from kavenegar import KavenegarAPI
from database import DBManager
from config import ADMIN_ID
from texts import get_text

database = DBManager()

class SmsSender:
    @staticmethod
    async def send_sms(message, client):
        active_users = DBManager.get_all_users()
        expired_users = []
        successful = []

        for _, user_id, receptor, sender, token, count in active_users:
            if count > 0 and database.update_subscription_count(user_id, count - 1):
                try:
                    api = KavenegarAPI(token)
                    params = {
                        "sender": sender,
                        "receptor": receptor,
                        "message": message
                    }
                    api.sms_send(params)
                    successful.append(receptor)
                except:
                    await client.send_message(
                        chat_id=ADMIN_ID,
                        text=f"Error sending SMS to {receptor}"
                    )
            else:
                await client.send_message(
                    text=get_text("subscription_ended")
                )
                expired_users.append(user_id)

        await client.send_message(
            chat_id=ADMIN_ID,
            text=f"**SMS send to users**: <blockquote expandable>{', '.join(successful)}</blockquote>\n**Total**: {len(successful)} users"
        )

        if expired_users:
            for user_id in expired_users:
                database.remove_user(user_id)
            await client.send_message(chat_id=ADMIN_ID, text=f"**Expired users removed**: <blockquote expandable>{', '.join(expired_users)}</blockquote>\n**Total**: {len(expired_users)} users")
