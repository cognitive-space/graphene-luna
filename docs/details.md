# Implementation Details

## GraphQL Requests and Context

In Django websockets, a request object is not built in. Luna thus uses the django-ws in a `WebSocketRequest` object that works similar to a Django request object. In your subscriptions this request object can be accessed in the info objects context (`info.context`). In the Subscription Handler this is accessed via the websocket request attribute (`ws.request`).
