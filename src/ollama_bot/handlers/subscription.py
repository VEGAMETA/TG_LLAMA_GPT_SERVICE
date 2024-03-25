from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from ollama_bot.models.user import User
from ollama_bot.misc.commands import commands
from ollama_bot.misc.language import get_language
from ollama_bot.models.transaction import Transaction

router = Router(name="subscription-commands-router")

@router.message(Command("subscription"))
@router.message(F.text.in_([commands.get("command_subscribe")]))
async def get_subscription_handler(message: Message, session: AsyncSession) -> None:
    """
    Command handler that sends a greeting message.
    """
    user = await session.get(User, user_id=message.from_user.id)
    language = await get_language(user.language)
            
    answer = language.get("balance") + user.balance 
    answer += language.get("subscription") * user.subscription
    answer += language.get("subscribed") + user.subscription_expire_time
    await message.answer(answer)

    if user.subscription_expire_time:
        if datetime.now() > user.subscription_expire_time:
            ...