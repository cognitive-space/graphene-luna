import pytest

from django.core.cache import cache


@pytest.mark.asyncio
async def test_subscription(ws_client):
    cache.set('count', 0, 30)

    def track_count(result):
        count = cache.get('count')
        assert result['data']['countSeconds'] == count
        print('Subscription Count:', count)
        cache.incr('count')

    query = "subscription {countSeconds(upTo: 5)}"
    await ws_client.subscribe(query=query, handle=track_count)

    count = cache.get('count')
    assert count == 5


@pytest.mark.asyncio
async def test_middleware(ws_client):
    cache.set('pre-message', 0)
    cache.set('post-message', 0)

    def dummy(result):
        pass

    query = "subscription {countSeconds(upTo: 2)}"
    await ws_client.subscribe(query=query, handle=dummy)

    assert cache.get('pre-message') == 2
    assert cache.get('post-message') == 2
