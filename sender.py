from kavenegar import KavenegarAPI
from database import DBManager
from config import ADMIN_ID
from texts import get_text

database = DBManager()


class Sender:
    @staticmethod
    async def send_sms(text, client):
        active_users = database.get_all_users()
        expired_users = []
        successful = []

        for row in active_users:
            if len(row) < 6:
                continue

            _, user_id, receptor, token, sender, count = row[:6]

            if count > 0:
                if database.update_subscription_count(user_id, count - 1):
                    try:
                        api = KavenegarAPI(token)
                        params = {
                            "sender": sender,
                            "receptor": receptor,
                            "message": text
                        }
                        api.sms_send(params)
                        successful.append(receptor)
                    except Exception as e:
                        await client.send_message(
                            chat_id=ADMIN_ID,
                            text=f"Error sending SMS to {receptor}: {str(e)}"
                        )
                else:
                    expired_users.append(user_id)
            else:
                expired_users.append(user_id)
                await client.send_message(
                    chat_id=user_id,
                    text=get_text("subscription_ended")
                )

        if successful:
            await client.send_message(
                chat_id=ADMIN_ID,
                text=f"**اعلان گیفت جدید به کاربران پیامک شد:**: <blockquote expandable>{', '.join(successful)}</blockquote>\n**تعداد کل**: {len(successful)} کاربر"
            )

        if expired_users:
            for user_id in expired_users:
                database.remove_user(user_id)
            await client.send_message(
                chat_id=ADMIN_ID,
                text=f"**کاربرانی که اشتراک انها تمام شده است: **: <blockquote expandable>{', '.join(map(str, expired_users))}</blockquote>\n**تعداد کل**: {len(expired_users)} کاربر"
            )

    @staticmethod
    async def send_telegram_message(text, client):
        _, groups = database.get_all_groups()
        removed_groups = []
        if groups:
            for chat_id in groups:
                try:
                    client.send_message(
                        text=text,
                        chat_id=chat_id
                    )
                except Exception as e:
                    removed_groups.append(chat_id)

            if removed_groups:
                for chat_id in removed_groups:
                    database.remove_group(chat_id)
                client.send_message(
                    text=f"**ربات از گروه ها حذف شده است**: <blockquote expandable>{', '.join(removed_groups)}</blockquote>\n**تعداد کل**: {len(removed_groups)} کاربر"
                )
