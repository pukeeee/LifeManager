from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.core.utils.config import CHANNEL

CHANNEL_ID = f"{CHANNEL}"


async def subscriptionKeyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Subscribe to the channel", url=f"https://t.me/{CHANNEL[1:]}")],
            [InlineKeyboardButton(text="Check subscription", callback_data="check_subscription")]
        ]
    )
    return keyboard