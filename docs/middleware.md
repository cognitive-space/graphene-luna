# Middleware

Websockets in general follow a different lifecycle then HTTP requests.

![websocket sequence](docs/websocket-sequence.png)

This means websockets in Django do not have a pre-established middleware mechanism. However, middleware is still helpful with websockets. Because websockets and GraphQL requests have a more complex lifecycle there are several different middleware mechanisms available. This document outlines all the options you have for doing middleware with Graphene GraphQL requests and websockets.

## Graphene Middleware

This middlware comes built into Graphene and can help you modify GraphQL requests that are both synchronous (queries and mutations) and asynchronous (subscriptions). This mechanism is not new to Luna, but is just here as a reminder since this mechanism works throughout all GraphQL requests. This allows you to create one middleware instead of having two different methods. So if you can use this middleware, it should be your first choice.

See the [Graphene middleware docs](https://docs.graphene-python.org/en/latest/execution/middleware/).

In Django you can set the middleware with the `GRAPHENE` setting.

```python
GRAPHENE = {
    ...
    'MIDDLEWARE': ['myproject.middleware.GraphQLMiddleware'],
}

```
