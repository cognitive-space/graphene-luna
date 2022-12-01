from django.core.cache import cache


class AuthAsyncMiddleware:
    def __init__(self, func):
        self.func = func

    async def __call__(self, ws, receive, send):
        if not hasattr(ws.request, 'user'):
            ws.request.user = 'Fake User'
            cache.set('user-set', True, 30)

        return await self.func(ws, receive, send)


class post_process_send:
    def __init__(self, ws, send):
        self.ws = ws
        self.send = send

    async def __call__(self, message):
        try:
            cache.incr('post-message')
        except ValueError:
            pass

        return await self.send(message)


class MessageMiddleware:
    def __init__(self, func):
        self.func = func

    async def __call__(self, ws, send, data):
        try:
            cache.incr('pre-message')
        except ValueError:
            pass

        send = post_process_send(ws, send)
        return await self.func(ws, send, data)
