import asyncio
#import logging
from aiogram import Bot, Dispatcher,F
from configs.cfg import tbt
from handlers import basic
from handlers import callback
from utils.callback import UserInfo
from handlers.callback import SelectCourse, SelectGroup, SelectDay, SendSchedule
from utils.storage import redisStorage

#logging.basicConfig(level=logging.DEBUG)
#testing git,srry
async def main():
    #создаем переменную бота
    bot = Bot(token=tbt,parse_mode="HTML")
    #объявляем диспатчер
    dp = Dispatcher(storage=redisStorage)
    #включаем роутеры
    dp.include_routers(basic.router,callback.router)
    #включаем фабрику коллбеков на обработку каждого уровня меню
    dp.callback_query.register(SelectCourse,UserInfo.filter(F.level == 1))
    dp.callback_query.register(SelectGroup,UserInfo.filter(F.level == 2))
    dp.callback_query.register(SelectDay,UserInfo.filter(F.level == 3))
    dp.callback_query.register(SendSchedule,UserInfo.filter(F.level == 4))
    #удаляем вебхуки, что бы не спамило сообщениями после старта
    await bot.delete_webhook(drop_pending_updates=True)
    #запускаем бота собстна
    await dp.start_polling(bot)
if __name__ == "__main__":
    try:
        #стартуем мэин
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print('Bye-bye')
        exit()