from aiogram.fsm.storage.redis import Redis,RedisStorage

redis = Redis(host='localhost',
              port='6379',
              password='iStillLoveYou')
redisStorage = RedisStorage(redis = redis)