from aiogram import Bot
from apps.feedback.bot.base import BaseBot
from apps.feedback.bot.utils.message import SingleMessage


class TelegramBot(BaseBot):

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.bot = Bot(token)

    async def send_message(self, message: SingleMessage, user_id: int) -> None:
        await self.bot.send_message(chat_id=user_id, text=message.message)
