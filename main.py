from app import init_app
import asyncio
from worker import init_worker
from modules.logger import Logger

if __name__ == '__main__':
    logger = Logger()
    loop = asyncio.get_event_loop()

    loop.create_task(init_app(logger))
    loop.create_task(init_worker(logger))

    logger.info('Control+C to stop the worker.')
    loop.run_forever()
