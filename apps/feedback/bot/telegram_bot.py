from aiogram import Bot
from apps.feedback.bot.base import BaseBot
from apps.feedback.bot.exceptions import BotIsNoneException
from apps.feedback.bot.utils.message import SingleMessage


class TelegramBot(BaseBot):

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.token = token
        self.bot: Bot = None

    async def __aenter__(self) -> 'TelegramBot':
        self.bot = Bot(self.token)
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> None:
        await self.close()

    async def send_message(self, message: SingleMessage, user_id: int) -> None:
        """Send the message by telegram bot.

        Args:
            message (SingleMessage): Message to send.
            user_id (int): Receiver id
        """
        self.require_bot()
        await self.bot.send_message(chat_id=user_id, text=message.message)

    async def close(self) -> None:
        """Close the bot connection."""
        return self.bot.close()

    def require_bot(self) -> None:
        """Require calls to be executed inside bot context.

        Raises:
            BotIsNoneException: If field `bot` is None.
        """
        if self.bot is not None:
            return
        raise BotIsNoneException(
            "The bot field can't be null. " +
            "Make sure you used the bot inside context manager."
        )
