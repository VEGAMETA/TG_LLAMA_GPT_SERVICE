from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from ollama_bot.models.user import User
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.misc.language import get_language
from ollama_bot.models.transaction import Transaction
from ollama_bot.misc.subscription import check_subscription
from ollama_bot.keyboards.reply.subscription import get_subscription_keyboard

router = Router(name="subscription-commands-router")


@router.message(Command("subscription"))
@router.message(F.text.in_(commands.get("command_subscription")))
async def get_subscription_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Handler for subscription etc.
    """
    await state.set_state(UserState.subscription)
    user_id = message.from_user.id
    user = await session.get(User, user_id)
    language = await get_language(user.language)

    answer = language.get("balance") + str(user.balance)
    answer += language.get("balance_after")
    if await check_subscription(session, user_id):
        answer += language.get("active_subscription")
        answer += language.get("expire_subscription")
        answer += user.subscription_expire_time.strftime(" %D %T")

    await message.answer(answer, reply_markup=get_subscription_keyboard(language))

@router.message(F.text.in_(commands.get("subscription_check")), UserState.subscription)
async def subscription_check(message: Message, state: FSMContext, session: AsyncSession) -> None:
    check_subscription(session, message.from_user.id)
    await get_subscription_handler(message, state, session)

@router.message(F.text.in_(commands.get("subscription_pay_100")), UserState.subscription)
async def subscription_pay_100(message: Message, state: FSMContext, session: AsyncSession) -> None:
    ...
    
@router.message(F.text.in_(commands.get("subscription_pay_month")), UserState.subscription)
async def subscription_pay_month(message: Message, state: FSMContext, session: AsyncSession) -> None:
    ...