from aiohttp import web


class Handlers:

    def create_handlers(self, app):
        pass

    async def pong(request):
        return web.Response(text='pong')