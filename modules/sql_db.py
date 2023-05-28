import os
import asyncio
import psycopg2
from dotenv import load_dotenv

load_dotenv()


async def get_db_connection(logger, tries=0):
    try:
        connection = psycopg2.connect("user={user} password={password} host={host} port={port} dbname={dbname}".format(
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            dbname=os.getenv('DB_DATABASE')
        ))

        logger.info("Connected to PostgreSQL DB on port {}".format(os.getenv('DB_PORT')))
        return connection
    except Exception as e:
        if tries < 3:
            logger.info('Failed, retring... ' + tries)
            await asyncio.sleep(2)
            await get_db_connection(tries+1)
            return
        raise e
