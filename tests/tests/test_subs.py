import pytest

from django.core.cache import cache


@pytest.mark.asyncio
async def test_subscription(ws_client):
    cache.set('count', 0, 30)

    def track_count(result):
        count = cache.get('count')
        assert result['data']['countSeconds'] == count
        print('Subscription Count:', count)
        cache.set('count', count + 1, 30)

    query = "subscription {countSeconds(upTo: 5)}"
    await ws_client.subscribe(query=query, handle=track_count)

    count = cache.get('count')
    assert count == 5
