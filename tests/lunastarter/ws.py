from django.core.cache import cache

from luna_ws import GraphQLSubscriptionHandler


class WSHandler(GraphQLSubscriptionHandler):
    async def on_message(self, data):
        try:
            cache.incr('pre-message')
        except ValueError:
            pass

        await super().on_message(data)

        try:
            cache.incr('post-message')
        except ValueError:
            pass
