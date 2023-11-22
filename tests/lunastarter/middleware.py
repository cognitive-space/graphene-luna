from django.core.cache import cache


class AuthAsyncMiddleware:
    def __init__(self, func):
        self.func = func

    async def __call__(self, ws):
        if not hasattr(ws.request, 'user'):
            ws.request.user = 'Fake User'
            cache.set('user-set', True, 30)

        return await self.func(ws)
