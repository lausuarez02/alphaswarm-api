import asyncio
from typing import Optional

from alphaswarm.agent.clients.telegram_bot import TelegramApp
from alphaswarm.core.tool import AlphaSwarmToolBase
from telegram.constants import ParseMode


class SendTelegramNotification(AlphaSwarmToolBase):
    """
    Send a Telegram notification to the registered Telegram channel with the given message and priority.
    Returns a string describing whether the notification was sent successfully or not.
    """

    def __init__(self, telegram_bot_token: str, chat_id: int) -> None:
        super().__init__()

        self.token = telegram_bot_token
        self.chat_id = chat_id

        self._telegram_app = TelegramApp(bot_token=self.token)
        self._loop = asyncio.new_event_loop()

    def __del__(self) -> None:
        if self._loop and self._loop.is_running():
            self._loop.close()

    def forward(self, message: str, confidence: float, priority: str) -> str:
        """
        Args:
            message: The message to send. When sending alert message, ALWAYS include token symbol or address in the message.
            confidence: The confidence score, between 0 and 1.
            priority: The priority of the alert, one of 'high', 'medium', 'low'.
        """
        message_to_send = self.format_alert_message(message=message, confidence=confidence, priority=priority)

        async def send_message() -> None:
            await self._telegram_app.send_message(
                chat_id=self.chat_id, message=message_to_send, parse_mode=ParseMode.MARKDOWN
            )

        self._loop.run_until_complete(send_message())

        return "Message sent successfully"

    @classmethod
    def format_alert_message(cls, message: str, confidence: float, priority: Optional[str]) -> str:
        """Format the analysis result into a user-friendly message"""

        priority_str = f"*Priority:* {cls._get_priority_emoji(priority)} {priority.upper() if priority else ''}"

        return "\n\n".join(
            [
                "🔔 *AI Agent Alert*",
                priority_str,
                f"*Details:*\n{message}",
                f"*Confidence:* {confidence * 100:.1f}%",
            ]
        )

    @staticmethod
    def _get_priority_emoji(priority: Optional[str]) -> str:
        priority_emojis = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        return priority_emojis.get(priority or "", "⚪")
