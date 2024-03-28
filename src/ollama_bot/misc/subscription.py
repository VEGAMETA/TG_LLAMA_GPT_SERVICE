from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from ollama_bot.models.user import User

async def check_subscription(session: AsyncSession, user_id) -> bool:
    user = await session.get(User, user_id)
    if not user.subscription_expire_time:
        return False
    if datetime.now() >= user.subscription_expire_time:
        user.subscription = False
        user.subscription_expire_time = None
        await session.commit()
        return False
    return True

async def pay_100(session: AsyncSession, user_id) -> bool:
    user = await session.get(User, user_id)
    
    ### TODO: Implement payment system
 
    user.balance += 100
    await session.commit()
    return True

async def pay_month(session: AsyncSession, user_id) -> bool:
    user = await session.get(User, user_id)
    if check_subscription(session, user_id):
        return False
    
    ### TODO: Implement payment system
    
    user.subscription_expire_time = datetime.now() + timedelta(days=30)
    user.subscription = True
    await session.commit()
    return True
