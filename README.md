# Graphene Luna

Graphene Luna is a websocket backend for GraphQL subscriptions in Django with Graphene. It does not require
Django Channels. Luna implements the [graphql-ws protocol](https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md).

## Why Luna

Most of the Django Graphene websocket subscription implementations are broke with newer versions of Django or require Django Channels. While Django Channels is great, it is complex and requires extra infrastructure such as Redis. With new versions of Django, the included asynchronous features allow websockets to be created more "natively" with less infrastructure and code overhead.

*Graphene Luna is the new modern and easy way to do GraphQL subscriptions in Django.*

## django-ws

Graphene Luna relies on [django-ws](https://github.com/pizzapanther/django-ws). If you wish to customize your experience, refer to django-ws for things like middleware and customizing websocket methods.

## Installation

`pip install graphene-luna`

## Adding Luna to Your Django Project

See the [Luna Starter Project](https://github.com/cognitive-space/graphene-luna-starter) for a fully setup Django project with Graphene and Luna installed.

### Step 1: Update Your `asgi.py`

- Remove line: `from django.core.asgi import get_asgi_application`
- Remove line: `application = get_asgi_application()`

Add to the end:

```python
from django_ws import get_websocket_application

application = get_websocket_application()
```

### Step 2: Connect the GraphQL Websocket in `ws_urls.py`

Next to your root `urls.py` create a `ws_urls.py` like the example below that uses your websocket.

```python
from django.urls import path

import luna_ws

urlpatterns = [
  path('graphql', luna_ws.GraphQLSubscriptionHandler),
]
```

### Step 3: Verify Your Schema is Setup

You should have Graphene setup with a schema. If not see the [Graphene installation](https://docs.graphene-python.org/projects/django/en/latest/installation/) steps.

In your Graphene settings verify you have a schema:

```python
GRAPHENE = {
    'SCHEMA': 'myproject.schema.schema'
}
```

### Step 3: Add Your First Subscription

Add a subscription to your schema. A simple schema to test subscriptions work is shown below.


**myproject/schema.py**

```python
import asyncio

import graphene
from graphql import GraphQLError

class Subscription(graphene.ObjectType):
    count_seconds = graphene.Int(up_to=graphene.Int())

    async def subscribe_count_seconds(root, info, up_to):
        if up_to > 30:
            raise GraphQLError('Count too high, must be <= 30')

        for i in range(up_to):
            print('TestSubs: ', i)
            yield i
            await asyncio.sleep(1)

schema = graphene.Schema(
		query=Query,
		mutation=Mutation,
		subscription=Subscription,
)
```

### Step 4: Run Your Django Project Asynchronously

You will need to pick a way to [run Django asynchronously](https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/).

Running with Gunicorn looks something like:

`gunicorn myproject.asgi:application -k uvicorn.workers.UvicornWorker`

### Step 5: Test Out Your Subscription

Navigate to your GraphiQL Explorer and to test out the subscription above, use a query like:

```graphql
subscription {
  countSeconds(upTo: 30)
}
```

If you're subscription test was successful, then you can proceed to writing more advanced subscriptions.

## Compatibility Notes

Currently Luna works with [Django Graphene](https://github.com/graphql-python/graphene-django) 3.1+ only. Also, Luna implements the newer GraphQL subscription protocol [graphql-ws](https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md).

## Going Further

- [Example Subscriptions](docs/subs-examples.md)
- [Implementation Details](docs/details.md)
