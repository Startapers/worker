from aiohttp import web
from modules.handlers.handler import Handlers

routes = web.RouteTableDef()


async def init_app(logger):
    try:
        app = web.Application()

        app.add_routes([
            web.get('/maintenance/ping', Handlers.pong)
            ])

        logger.info("Server started")
        server = web.AppRunner(app)
        await server.setup()
        site = web.TCPSite(server, '0.0.0.0', port=8888)
        await site.start()
    except Exception as e:
        logger.error(e)
        return
