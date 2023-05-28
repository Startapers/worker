import asyncio
from modules import redis, sql_db
from modules.dal import cache
from modules.recommend import RecommendationGenerator
from modules.dal.user import create


async def init_worker(logger):
    logger.info('starting worker...')

    cache_conn = await redis.get_db_connection(logger)
    sql = await sql_db.get_db_connection(logger)

    cache_dal = await cache.create(cache_conn, logger)
    user_dal = create(sql, logger)

    generator = RecommendationGenerator(cache_dal, user_dal)

    while True:
        job = await cache_dal.get('worker:job')
        if job:
            if job.get('job') == 'new':
                await generator.generate_recommendations_for_new(job.get('user_id'), job.get('tags'))
                continue

            if job.get('job') == 'all':
                await generator.generate_all()
                continue

            await generator.generate_recommendatations(id)
        logger.info('fetching job...')
        await asyncio.sleep(2)
