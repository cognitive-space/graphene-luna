# Graphene Luna

Graphene Luna is a websocket backend for GraphQL subscriptions in Django with Graphene. It does not require
Django Channels. It implements the [subscriptions-transport-ws](https://github.com/apollographql/subscriptions-transport-ws) protocol.

## Why Luna

Most of the Django Graphene websocket subscription implementations are broke with newer versions of Django or require Django Channels. While Django Channels is great, it is complex and requires extra infrastructure such as Redis. With new versions of Django, the included asynchronous features allow websockets to be created more "natively" with less infrastructure and code overhead.

*Graphene Luna is the new modern way to do GraphQL subscriptions in Django.*

## Installation

`pip install graphene-luna`

## Adding Luna to Your Django Project

### Step 1: Update Your `asgi.py`

Add the following at the end of your `asgi.py`

```python
from luna_ws import add_ws_app

application = add_ws_app(application)
```

The entire `asgi.py` should look something like the following:

```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = get_asgi_application()

from luna_ws import add_ws_app

application = add_ws_app(application)
```

### Step 2: Verify Your Schema is Setup

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

Currently Luna works with [Django Graphene](https://github.com/graphql-python/graphene-django) 3.0+ only. Also, Luna implements the older protocol of graphql-ws. We picked to implement the older subscription protocol because more frontend clients seemed to be compatible with it. In the future, we plan to implement the newer graphql-ws protocol too.

## Going Further

- [Example Subscriptions](docs/subs-examples.md)
- [Middleware for Websockets](docs/middleware.md)
- [Implementation Details](docs/details.md)
