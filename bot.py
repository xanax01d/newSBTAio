import asyncio
#for logs
#import logging
#basic bot imports
from aiogram import Bot, Dispatcher,F
#import DBP to configure bot
from aiogram.client.default import DefaultBotProperties
#import mode to parse HTML tags in messages
from aiogram.enums.parse_mode import ParseMode
from configs.cfg import tbt
#import handler for /start command
from handlers import basic
#import handler for callback and class UserInfo for callback query
from handlers import callback
from utils.callback import UserInfo
from handlers.callback import SelectCourse, SelectGroup, SelectDay, SendSchedule
#import storage for FSM (Finite State Machine)
from utils.storage import redisStorage
#logs
#logging.basicConfig(level=logging.DEBUG)

async def main():
    #создаем переменную бота
    bot = Bot(token=tbt,
              default=DefaultBotProperties(
                  parse_mode=ParseMode.HTML,
              ))
    #объявляем диспатчер
    dp = Dispatcher(storage=redisStorage)
    #for test without redis database (i'm lazy)
    #dp = Dispatcher()
    #include routers
    dp.include_routers(basic.router,callback.router)
    #register callback query by levels of menu
    dp.callback_query.register(SelectCourse,UserInfo.filter(F.level == 1))
    dp.callback_query.register(SelectGroup,UserInfo.filter(F.level == 2))
    dp.callback_query.register(SelectDay,UserInfo.filter(F.level == 3))
    dp.callback_query.register(SendSchedule,UserInfo.filter(F.level == 4))
    #delete webhook's for optimization
    await bot.delete_webhook(drop_pending_updates=True)
    #starting bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        #run main..
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print('Bye-bye')
        exit()
