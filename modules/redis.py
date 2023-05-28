import os
import redis
import asyncio
from dotenv import load_dotenv

load_dotenv()


async def get_db_connection(logger, tries=0):
    try:
        connection = redis.Redis(
          host=os.getenv('REDIS_HOST'),
          port=os.getenv('REDIS_PORT'),
          db=os.getenv('REDIS_DB_DEFAULT'))

        logger.info("Connected to Redis on port {}".format(os.getenv('REDIS_PORT')))
        return connection
    except Exception as e:
        if tries < 3:
            logger.info('Failed, retring...', tries)
            await asyncio.sleep(2)
            await get_db_connection(tries+1)
            return
        raise e
